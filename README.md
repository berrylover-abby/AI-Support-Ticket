# AI Support Ticket Demo

A small support-ticket workflow that demonstrates backend engineering and practical LLM integration. A customer submits a ticket, the backend saves it and asks an LLM for a structured analysis, and a human reviews and confirms the result.

## MVP goal

Complete one reliable end-to-end workflow in one week. The AI assists a human; it does not make or send the final customer-facing response on its own.

## User flow

1. Submit a ticket with a title and description through the REST API.
2. Save the ticket before starting AI analysis.
3. Ask the LLM for a category, priority, short summary, and suggested reply.
4. Validate the structured result, then save it with the ticket.
5. A human opens the ticket in Django Admin, reviews and edits the suggestion, then confirms it.
6. Save the confirmed category, priority, summary, and reply. The reply is not sent to the customer.

If analysis fails, keep the ticket, record the failure, show an analysis-failed state, and allow a human to retry it.

## MVP scope

- REST endpoints to create tickets and retrieve a ticket list and ticket details.
- Persistent ticket, AI suggestion, and human-confirmed result data.
- One LLM request per analysis, with validated structured output.
- Django Admin as the human review interface.
- Basic application logging and clear handling of invalid model output and provider errors.
- Traceability for the model, prompt version, analysis time, and original AI suggestion.
- A small fixed evaluation set of 5–10 sample tickets to check output shape and expected category/priority.

### Categories and priorities

Categories: `account`, `billing`, `technical`, `other`.

Priorities: `low`, `medium`, `high`. Judge priority by the user's practical impact; urgent wording alone does not make a ticket high priority.

### Ticket states

`pending_analysis` → `pending_review` → `confirmed`, with `analysis_failed` for unsuccessful analysis. A failed ticket can be retried.

## Explicitly out of scope

- User accounts, permissions, and multi-tenant support.
- Sending replies or integrating with email, chat, Zendesk, or Intercom.
- Knowledge bases, retrieval-augmented generation, or vector databases.
- Multiple agents, tools, or complex orchestration.
- Automatic assignment, SLA management, notifications, analytics dashboards, or a polished customer-facing frontend.
- React in the first version. Consider a small UI only after the backend workflow is complete.

## Technology choices

- **Backend/API:** Python, Django, Django REST Framework.
- **Database:** SQLite, accessed through Django ORM and migrations.
- **Human review:** Django Admin.
- **LLM:** Provider and model are not selected yet; no API key is available at project start. Develop the workflow with a deterministic mock analysis first, then connect one provider when credentials are available.
- **Structured output:** Require a fixed JSON shape for `category`, `priority`, `summary`, and `suggested_reply`; validate fields and allowed values in the backend before saving a successful analysis.
- **Logging/errors:** Use Django's standard logging. Record analysis outcomes and provider/validation failures without logging secrets. Preserve the ticket on failure and support manual retry.
- **Human-in-the-loop:** Keep AI suggestions separate from human-confirmed values. Confirmation is an explicit human action in Admin.

## One-week build plan

Keep each day focused on one small result; move on only when the current slice works.

1. **Day 1 — Project setup:** Create the Django project and app, configure DRF and SQLite, and make the first migration.
2. **Day 2 — Ticket API:** Define the ticket data model and implement ticket creation, list, and detail endpoints.
3. **Day 3 — Review workflow:** Add statuses and AI/review fields; make tickets usable in Django Admin for human review and confirmation.
4. **Day 4 — AI boundary:** Implement mock analysis, fixed-schema validation, and failure state/retry behavior.
5. **Day 5 — Real LLM:** Connect one provider if an API key is available; keep the mock usable for local development.
6. **Day 6 — Traceability and evaluation:** Store model/prompt metadata and original suggestions; run the 5–10 sample-ticket evaluation and fix obvious issues.
7. **Day 7 — Interview readiness:** Write setup and API documentation, prepare a short demo flow, and explain architecture, tradeoffs, and limitations.

If time gets tight, finish the end-to-end backend flow and Admin review before adding any UI.

## Definition of done

- A ticket can be submitted through the API and remains saved if AI analysis fails.
- Successful analysis produces validated values from the allowed category and priority sets.
- A human can review, edit, and confirm a suggestion in Django Admin.
- The original AI suggestion and confirmed result can be distinguished and inspected later.
- The evaluation examples and a repeatable demo flow are documented.
