# AI Support Ticket

An AI-powered support ticket system built with Django. It turns support requests into structured categories, priorities, summaries, and reply drafts, with human review before confirmation.

Tickets are persisted before analysis, so provider errors do not lose the original request. Reviewers can edit suggestions, retry failed analysis, and inspect the original AI output and model metadata.

![Live analysis of an invoice request, awaiting human review](docs/images/demo.png)

## Workflow

1. Submit a title and description on the homepage, which calls the REST API.
2. Save the ticket before starting AI analysis.
3. Ask the LLM for a category, priority, short summary, and suggested reply.
4. Validate the structured result, then save it with the ticket.
5. A human opens the ticket in Django Admin, reviews and edits the suggestion, then confirms it.
6. Save the confirmed category, priority, summary, and reply. The reply is not sent to the customer.

If analysis fails, keep the ticket, record the failure, show an analysis-failed state, and allow a human to retry it.

## Features

- REST endpoints to create tickets and retrieve a ticket list and ticket details.
- Persistent ticket, AI suggestion, and human-confirmed result data.
- One LLM request per analysis, with validated structured output.
- Django Admin as the human review interface.
- A responsive submission page with loading feedback, analysis results, failure messages, and a link to human review.
- Basic application logging and clear handling of invalid model output and provider errors.
- Traceability for the model, prompt version, analysis time, and original AI suggestion.
- Five fixed evaluation cases and two targeted prompt regression checks.

### Categories and priorities

Categories: `account`, `billing`, `technical`, `other`.

Priorities: `low`, `medium`, `high`. Judge priority by the user's practical impact; urgent wording alone does not make a ticket high priority.

### Ticket states

`pending_analysis` → `pending_review` → `confirmed`, with `analysis_failed` for unsuccessful analysis. A failed ticket can be retried.

## Technology

- **Backend/API:** Python, Django, Django REST Framework.
- **Frontend:** A Django template, plain CSS, and JavaScript `fetch`; no separate build or frontend dependencies.
- **Database:** SQLite, accessed through Django ORM and migrations.
- **Human review:** Django Admin.
- **LLM:** OpenAI Responses API with `gpt-4.1-mini`, called through Python's standard-library HTTP client. A deterministic mock remains available for local development. The application does not require the OpenAI SDK.
- **Structured output:** Request strict JSON Schema output for `category`, `priority`, `summary`, and `suggested_reply`; validate the result with a DRF serializer before saving.
- **Logging/errors:** Use Django's standard logging. Record analysis outcomes and provider/validation failures without logging secrets. Preserve the ticket on failure and support manual retry.
- **Human-in-the-loop:** Keep AI suggestions separate from human-confirmed values. Confirmation is an explicit human action in Admin.

## Traceability and evaluation

Successful analyses store the requested model name, prompt version, and completion time alongside the original suggestion. These fields are read-only in Admin and describe the latest successful analysis. Human-reviewed values are stored separately.

The [evaluation record](EVALUATION.md) documents expected labels, observed outputs, and prompt revisions. The five-case v1 baseline produced 5/5 valid outputs, 5/5 category matches, and 4/5 priority matches. Prompt v2 adds explicit priority and reply rules; two targeted regression cases passed structure and label checks.

See [Architecture](ARCHITECTURE.md) for request handling, validation, state transitions, and component responsibilities.

## Run locally on Windows

From the project directory in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py runserver
```

Mock mode is the default and needs no API key. For real analysis, stop the server and run the following in the same terminal:

```powershell
# Read the key without displaying it or including it in a command.
$ticketApiKey = Read-Host "Paste API key" -AsSecureString
$env:OPENAI_API_KEY = [System.Net.NetworkCredential]::new("", $ticketApiKey).Password
$env:TICKET_AI_MODE = "openai"
.\.venv\Scripts\python.exe manage.py runserver
```

Environment variables apply to the current terminal and programs started from it. Real requests require an API key with available credits and incur API usage charges.

Open `http://127.0.0.1:8000/` to submit a ticket. The page identifies mock or live mode. **Review this ticket** opens the saved ticket in Admin, where the administrator login is required. Mock returns fixed sample suggestions for development and workflow testing.

## REST API

- `POST /api/tickets/`: submit `title` and `description`. Save the ticket first, then analyze synchronously. `201 Created` means the ticket was persisted; inspect `status` to determine the analysis outcome.
- `GET /api/tickets/`: return tickets, newest first.
- `GET /api/tickets/{id}/`: return one ticket.

The API returns `status` and `ai_result` as read-only fields. A successful analysis sets `pending_review`; an expected analysis failure sets `analysis_failed`. In Admin at `/admin/tickets/ticket/`, select **Analyze selected tickets** to retry a failed ticket. Edit and save the review fields before selecting **Confirm selected tickets**.

API-created tickets are analyzed automatically. Admin-created tickets start in `pending_analysis` and require the analysis action. The HTTP client uses a 20-second network timeout; analysis runs within the request, so submission waits for it.

### Create a ticket

Send this JSON body to `POST /api/tickets/`:

```json
{
  "title": "Need a copy of my invoice",
  "description": "My payment succeeded and my account works normally. I need an invoice for my expense records."
}
```

The response includes the saved ticket ID, input fields, creation time, status, and structured `ai_result`. Invalid input returns `400 Bad Request`.
