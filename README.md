# JIRA Ticket Summarizer Agent Tool

An intelligent agent-based tool that reads JIRA tickets from an Excel file, summarizes them using Claude AI, and outputs the results to a new Excel spreadsheet.

## Features

- 🔗 **MCP Integration**: Uses Model Context Protocol to securely connect to your JIRA instance
- 🤖 **AI-Powered Summarization**: Claude AI generates intelligent, context-aware summaries of each ticket
- 📊 **Excel Integration**: Read ticket IDs from input Excel and generate formatted output Excel
- 🚀 **Batch Processing**: Process multiple tickets efficiently with multi-turn conversation context
- 🔐 **Secure Credentials**: Environment-based configuration for API keys and credentials

## Project Structure

```
.
├── jira_agent.py           # Main agent orchestrator
├── mcp_jira_server.py      # MCP server for JIRA
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
└── README.md              # This file
```

## Prerequisites

- Python 3.9+
- JIRA account with API token access
- Anthropic API key (for Claude)
- Input Excel file with JIRA ticket IDs

## Installation

### 1. Clone/Setup Project

```bash
cd "C:\Users\skumar22\OneDrive - Advanced Micro Devices Inc\Documents\Classification"
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
# JIRA Configuration
JIRA_URL=https://your-instance.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token-here

# Anthropic API
ANTHROPIC_API_KEY=sk-ant-...
```

### Getting JIRA Credentials

1. **JIRA URL**: Your Atlassian instance URL (e.g., https://company.atlassian.net)
2. **Email**: Your Atlassian account email
3. **API Token**: 
   - Go to https://id.atlassian.com/manage-profile/security/api-tokens
   - Click "Create API token"
   - Copy the token to your `.env`

### Getting Anthropic API Key

1. Visit https://console.anthropic.com/
2. Navigate to API keys section
3. Create a new API key
4. Add it to your `.env` as `ANTHROPIC_API_KEY`

## Input Excel Format

Your input Excel file should have a column containing JIRA ticket IDs. The tool will look for columns named:
- `ticket_id` (preferred)
- `Ticket ID`
- `ticket`
- `Ticket`
- `ID`
- Or defaults to the first column

Example:
| ticket_id |
|-----------|
| PROJ-123  |
| PROJ-456  |
| PROJ-789  |

## Usage

### Basic Usage

```bash
python jira_agent.py
```

The script will:
1. Read ticket IDs from `C:\Users\skumar22\OneDrive - Advanced Micro Devices Inc\Documents\Summary_Sheet\ticket.xlsx`
2. Fetch each ticket from JIRA
3. Generate AI summaries
4. Save results to `ticket_summary.xlsx` in the same directory

### Custom Paths

To use different input/output paths, modify the paths in `jira_agent.py`:

```python
input_path = r"path\to\your\input.xlsx"
output_path = r"path\to\your\output.xlsx"
```

## Output Excel Format

The output file (`ticket_summary.xlsx`) contains three columns:

| ticket_id | ticket_title | summary |
|-----------|--------------|---------|
| PROJ-123  | Bug in login flow | The authentication system fails when users... |
| PROJ-456  | Add export feature | Users need the ability to export... |

The summary column is:
- Word-wrapped for readability
- Automatically sized to fit content
- 2-3 sentence concise summaries

## MCP Server

The `mcp_jira_server.py` provides MCP tools for direct JIRA access:

### Available Tools

- **get_ticket**: Fetch a single JIRA ticket
  - Input: `ticket_id` (string, e.g., "PROJ-123")
  - Output: Ticket details (ID, title, description, status, assignee)

- **get_tickets_batch**: Fetch multiple tickets
  - Input: `ticket_ids` (array of strings)
  - Output: Array of ticket details

### Test MCP Connection

```python
from mcp_jira_server import connect_to_jira, jira_client
import os
from dotenv import load_dotenv

load_dotenv()
if connect_to_jira():
    print("✓ Successfully connected to JIRA")
else:
    print("✗ Failed to connect to JIRA")
```

## Error Handling

The tool handles several error scenarios:

- **Missing Credentials**: Clear error message if environment variables are not set
- **Connection Failed**: Reports JIRA connection issues
- **Invalid Ticket ID**: Skips tickets that don't exist, continues processing
- **Excel Errors**: Handles missing or malformed Excel files
- **Rate Limiting**: Automatically manages API calls

## Performance

- **Speed**: ~1-2 tickets per minute (depends on ticket size and AI processing)
- **Memory**: Minimal - processes tickets sequentially
- **Conversation Context**: Maintains last 10 exchanges for better summarization context

## Customization

### Change Summarization Style

Edit the system prompt in `jira_agent.py` (line ~127):

```python
system="You are a helpful assistant that summarizes JIRA tickets with a focus on business impact."
```

### Adjust Summary Length

Modify `max_tokens` parameter (default 500):

```python
response = self.client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=250,  # Shorter summaries
    ...
)
```

### Change Output Columns

Modify the results dictionary in `summarize_ticket_with_agent()`:

```python
result = {
    "ticket_id": ticket["ticket_id"],
    "ticket_title": ticket["title"],
    "summary": summary,
    "status": ticket["status"],  # Add more fields
}
```

## Troubleshooting

### "JIRA URL is not valid"
- Ensure `JIRA_URL` ends without trailing slash
- Use full URL: `https://company.atlassian.net`

### "Authentication failed"
- Verify email and API token are correct
- Ensure API token hasn't expired
- Check token permissions in JIRA

### "Ticket not found"
- Verify ticket ID is correct (case-sensitive)
- Ensure your JIRA account has access to the ticket's project
- Check if ticket has been deleted

### "Rate limit exceeded"
- The tool includes automatic rate limiting
- Wait a few minutes before running again
- Check JIRA API usage limits

### Excel file locked
- Close the Excel file in other applications
- Or use a different output path

## Advanced Usage

### Process from Different Excel Sheet

```python
summarizer = JIRATicketSummarizer(jira_url, email, api_token)
ticket_ids = summarizer.read_ticket_ids_from_excel("custom_path.xlsx")
results = summarizer.process_tickets(ticket_ids)
summarizer.save_results_to_excel(results, "output.xlsx")
```

### Get Tickets Programmatically

```python
from jira_agent import JIRATicketSummarizer

summarizer = JIRATicketSummarizer(jira_url, email, api_token)
ticket = summarizer.fetch_ticket_details("PROJ-123")
summary = summarizer.summarize_ticket_with_agent(ticket)
print(f"Summary: {summary}")
```

## Dependencies

- **jira**: Atlassian JIRA Python client
- **anthropic**: Anthropic Claude AI API client
- **openpyxl**: Excel file handling
- **pandas**: Data manipulation and Excel I/O
- **python-dotenv**: Environment variable management

## License

MIT License - Feel free to use and modify

## Support

For issues or questions:
1. Check environment variables are correctly set
2. Verify JIRA and Anthropic API access
3. Review error messages in console output
4. Check connectivity to both JIRA and Anthropic APIs

## Next Steps

1. ✅ Set up environment variables
2. ✅ Install dependencies
3. ✅ Prepare input Excel file
4. ✅ Run `python jira_agent.py`
5. ✅ Check `ticket_summary.xlsx` for results
