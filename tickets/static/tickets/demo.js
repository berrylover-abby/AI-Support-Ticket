const form = document.getElementById("ticket-form");
const button = document.getElementById("submit-button");
const feedback = document.getElementById("feedback");
const titleInput = document.getElementById("title");
const descriptionInput = document.getElementById("description");
const emptyState = document.getElementById("empty-state");
const ticketResult = document.getElementById("ticket-result");
const analysisResult = document.getElementById("analysis-result");
const ticketStatus = document.getElementById("ticket-status");

let submitting = false;

form.addEventListener("submit", async (event) => {
    // Submit through the API instead of reloading the page.
    event.preventDefault();
    if (submitting) return;

    const title = titleInput.value.trim();
    const description = descriptionInput.value.trim();

    if (!title || !description) {
        feedback.textContent = "Enter a title and description.";
        feedback.className = "error";
        return;
    }

    // Prevent duplicate submissions and edits while waiting.
    submitting = true;
    button.disabled = true;
    titleInput.disabled = true;
    descriptionInput.disabled = true;
    button.textContent = "Analyzing…";
    form.setAttribute("aria-busy", "true");
    feedback.className = "";
    feedback.textContent = "Saving your request and preparing suggestions…";
    ticketResult.hidden = true;
    analysisResult.hidden = true;
    emptyState.hidden = false;
    emptyState.textContent = "Preparing your analysis…";

    let errorMessage = "Unable to confirm submission. Check the review queue before trying again.";

    try {
        const response = await fetch("/api/tickets/", {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "X-CSRFToken": form.querySelector(
                    '[name="csrfmiddlewaretoken"]'
                ).value,
            },
            body: JSON.stringify({ title, description }),
        });

        if (!response.ok) {
            errorMessage = response.status === 400
                ? "Check the title and description, then try again."
                : `Submission failed (HTTP ${response.status}). Refresh the page and try again.`;
            throw new Error(`HTTP ${response.status}`);
        }

        const ticket = await response.json();
        emptyState.hidden = true;
        ticketResult.hidden = false;

        document.getElementById("review-link").href =
            `/admin/tickets/ticket/${ticket.id}/change/`;

        const failed = ticket.status === "analysis_failed";
        ticketStatus.classList.toggle("failed", failed);
        ticketStatus.textContent =
            `Ticket #${ticket.id} · ${failed ? "Analysis failed" : "Pending review"}`;

        if (failed) {
            // A saved ticket can still have an unsuccessful analysis.
            feedback.className = "error";
            feedback.textContent = "Ticket saved. Analysis failed. Open the review queue to retry.";
        } else {
            const analysis = ticket.ai_result;
            analysisResult.hidden = false;

            // Render model text safely without interpreting it as HTML.
            document.getElementById("result-category").textContent = analysis.category;
            document.getElementById("result-priority").textContent = analysis.priority;
            document.getElementById("result-priority").dataset.priority = analysis.priority;
            document.getElementById("result-summary").textContent = analysis.summary;
            document.getElementById("result-reply").textContent = analysis.suggested_reply;

            feedback.className = "success";
            feedback.textContent = "Ticket saved. Suggestions are ready for review.";
        }
    } catch (error) {
        feedback.className = "error";
        feedback.textContent = errorMessage;
        emptyState.textContent = "No confirmed result to display.";
        console.error("Ticket submission failed:", error);
    } finally {
        // Restore the form after both successful and failed requests.
        submitting = false;
        button.disabled = false;
        titleInput.disabled = false;
        descriptionInput.disabled = false;
        button.textContent = "Analyze ticket";
        form.removeAttribute("aria-busy");
    }
});