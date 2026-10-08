# Quick Start Guide

## 5-Minute Setup

### Step 1: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 2: Configure Credentials

Create a `.env` file in the project root:
```
JIRA_URL=https://your-instance.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

**How to get credentials:**

**JIRA API Token:**
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Copy and paste into `.env`

**Anthropic API Key:**
1. Go to https://console.anthropic.com/
2. Create an API key in the dashboard
3. Copy and paste into `.env`

### Step 3: Prepare Input Excel

Your input file should look like this:

| ticket_id |
|-----------|
| PROJ-123  |
| PROJ-456  |

Location: `C:\Users\skumar22\OneDrive - Advanced Micro Devices Inc\Documents\Summary_Sheet\ticket.xlsx`

### Step 4: Run the Agent

```powershell
python jira_agent.py
```

**Output:** `C:\Users\skumar22\OneDrive - Advanced Micro Devices Inc\Documents\Summary_Sheet\ticket_summary.xlsx`

## What It Does

1. **Reads** ticket IDs from your input Excel file
2. **Fetches** each ticket from JIRA using the API
3. **Summarizes** each ticket using Claude AI
4. **Saves** results to a new Excel file with columns:
   - Ticket ID
   - Ticket Title
   - Summary (AI-generated)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| `Authentication failed` | Check JIRA_EMAIL and JIRA_API_TOKEN in .env |
| `JIRA URL is not valid` | Use full URL: https://company.atlassian.net |
| `Ticket not found` | Verify ticket ID is correct and you have access |
| `ANTHROPIC_API_KEY not set` | Add key to .env file |

## Advanced Options

See `README.md` for:
- Custom output paths
- Changing summary length
- Modifying summarization style
- Using the MCP server directly
- Batch processing

## Example Output

Input file: `ticket.xlsx`
```
PROJ-101
PROJ-102
```

Output file: `ticket_summary.xlsx`
```
Ticket ID | Ticket Title              | Summary
----------|---------------------------|----------
PROJ-101  | Fix login button bug       | The login button fails to respond on mobile browsers...
PROJ-102  | Add password reset feature | Users need a self-service password reset option...
```

## Next Steps

1. ✅ Dependencies installed
2. ✅ Environment configured
3. ✅ Input file prepared
4. ✅ Run `python jira_agent.py`
5. ✅ Review `ticket_summary.xlsx`

**Happy summarizing! 🚀**
