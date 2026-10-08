# JIRA Ticket Summarizer Skill

## Purpose
This project reads JIRA ticket IDs, fetches the corresponding issue data, and summarizes each ticket using a configured LLM. It supports both a local Flask web interface and a direct Python batch flow.

## How the project is executed

### 1) Web application flow
The main app is launched from the project root with:

```bash
python web_app.py
```

This starts a Flask server on:

```text
http://127.0.0.1:5000
```

Key behavior in `web_app.py`:
- `GET /` renders the UI.
- `POST /summarize` accepts either:
  - manual ticket IDs, or
  - an uploaded Excel file.
- IDs are normalized, de-duplicated, and queued as a background job.
- Each job fetches JIRA details and invokes the summarizer one ticket at a time.
- The results are returned as a JSON payload and can be exported to Excel.

### 2) Direct batch processing flow
The core logic is defined in `jira_agent.py` and can be used directly through the `JIRATicketSummarizer` class.

Typical invocation pattern:

```python
from jira_agent import JIRATicketSummarizer

summarizer = JIRATicketSummarizer(
    jira_url="https://your-instance.atlassian.net",
    email="user@example.com",
    api_token="token_here",
)

issue = summarizer.fetch_ticket_details("PROJ-123")
summary = summarizer.summarize_ticket_with_agent(issue)
```

### 3) Required environment variables
The application uses `.env` configuration values provided by the environment.

For JIRA:

```env
JIRA_BASE_URL=https://your-instance.atlassian.net
# or JIRA_URL
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token
```

For Anthropic (default path):

```env
ANTHROPIC_API_KEY=your-key
```

For on-prem/OpenAI-compatible LLMs:

```env
LLM_BASE_URL=https://your-llm-gateway
LLM_API_KEY=your-key
LLM_MODEL=gpt-4.1-mini
LLM_SUBSCRIPTION_KEY=optional-subscription-key
```

The project decides which model provider to use by checking whether `LLM_BASE_URL` is present.

## How a ticket is summarized

The summarization pipeline is:

1. Fetch the raw JIRA issue (`fetch_ticket_details`).
2. Package the issue into a JSON payload.
3. Send that payload to the chosen LLM.
4. Ask the model for a concise 3–5 sentence summary focusing on:
   - business/engineering impact,
   - technical context and dependencies,
   - current status, ownership, and timeline signals,
   - risks or blockers from comments, links, and worklogs.

### JIRA fields considered during summarization
The summarizer collects and includes these fields from the issue when building the ticket payload:

- `ticket_id`
- `title`
- `description`
- `status`
- `issue_type`
- `priority`
- `reporter`
- `assignee`
- `resolution`
- `resolution_date`
- `labels`
- `components`
- `fix_versions`
- `affected_versions`
- `due_date`
- `environment`
- `project`
- `parent`
- `subtasks`
- `linked_issues`
- `comments`
- `attachments`
- `worklogs`
- `watchers`
- `timetracking`
- `created`
- `updated`

Additionally, the code trims very large text values to control prompt size, particularly:
- description,
- comments,
- worklogs,
- environment,
- and general text content.

## Manual input and Excel parsing
The UI accepts ticket IDs in several formats:
- one per line,
- comma-separated,
- space-separated.

For Excel uploads, the application checks these candidate columns in order:

```text
ticket_id, Ticket ID, ticket, Ticket, ID, id
```

If none exist, it falls back to the first column in the workbook.

## Summary output
The final summary is returned as a row containing:

```text
ticket_id
ticket_title
summary
```

This output is used in the UI and can also be exported as an Excel report.

## Operational notes
- Requests are processed in a background thread for the web UI.
- Jobs maintain status, progress, and result payloads in memory.
- Errors are surfaced cleanly if the JIRA configuration, LLM config, or ticket lookup fails.
- The default web app uses port `5000`.

## Quick reference commands

```bash
python web_app.py
```

Then open:

```text
http://127.0.0.1:5000
```

For direct Python usage:

```bash
python jira_agent.py
```

This project relies on the JIRA issue content and the LLM prompt to generate a business-focused summary rather than simply restating the raw ticket description.
