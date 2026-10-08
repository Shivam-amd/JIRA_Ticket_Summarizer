# Configuration Guide

## Environment Setup

### 1. Create `.env` file

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 2. Add your credentials

Edit `.env` with your actual credentials:

```env
# JIRA Configuration (Required)
JIRA_URL=https://your-company.atlassian.net
JIRA_EMAIL=your.email@company.com
JIRA_API_TOKEN=your-api-token-here

# Anthropic API (Required for summarization)
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

## Getting Your Credentials

### JIRA Setup

1. **Find Your JIRA URL**
   - Open your Atlassian instance
   - URL format: `https://your-company.atlassian.net`
   - Copy the full URL

2. **Generate API Token**
   - Go to: https://id.atlassian.com/manage-profile/security/api-tokens
   - Log in if prompted
   - Click "Create API token"
   - Give it a name (e.g., "JIRA Ticket Summarizer")
   - Copy the token
   - Paste into `.env` as `JIRA_API_TOKEN`

3. **Use Your Email**
   - Use the email associated with your Atlassian account
   - This is your login email for JIRA

### Anthropic API Setup

1. **Visit Anthropic Console**
   - Go to: https://console.anthropic.com/

2. **Create API Key**
   - Click "API keys" in left sidebar
   - Click "Create key"
   - Give it a name (e.g., "JIRA Summarizer")
   - Copy the key
   - Paste into `.env` as `ANTHROPIC_API_KEY`

3. **Save API Key Securely**
   - You can only see it once after creation
   - Store it safely

## File Structure

```
.
├── .env                 # Environment variables (DO NOT commit)
├── .env.example        # Template (can commit)
├── jira_agent.py       # Main agent script
├── mcp_jira_server.py  # MCP server for JIRA
├── setup.py            # Interactive setup script
├── requirements.txt    # Python dependencies
├── README.md           # Full documentation
├── QUICKSTART.md       # Quick reference
└── CONFIG.md          # This file
```

## Excel File Setup

### Input File Location
```
C:\Users\skumar22\OneDrive - Advanced Micro Devices Inc\Documents\Summary_Sheet\ticket.xlsx
```

### Input File Format

Your Excel file should have at least one column with JIRA ticket IDs:

**Option 1: Column named "ticket_id"**
| ticket_id |
|-----------|
| PROJ-123  |
| PROJ-456  |
| PROJ-789  |

**Option 2: Column named "Ticket ID"**
| Ticket ID |
|-----------|
| PROJ-123  |
| PROJ-456  |

**Option 3: First column (any name)**
| ID        |
|-----------|
| PROJ-123  |
| PROJ-456  |

The tool will automatically detect the correct column.

### Output File

Output will be saved to:
```
C:\Users\skumar22\OneDrive - Advanced Micro Devices Inc\Documents\Summary_Sheet\ticket_summary.xlsx
```

Output format:
| ticket_id | ticket_title | summary |
|-----------|--------------|---------|
| PROJ-123  | Bug Title    | 2-3 sentence AI-generated summary |
| PROJ-456  | Feature Name | 2-3 sentence AI-generated summary |

## Verification

### Test JIRA Connection

Create a test script `test_jira.py`:

```python
import os
from dotenv import load_dotenv
from jira import JIRA

load_dotenv()

try:
    jira = JIRA(
        server=os.getenv("JIRA_URL"),
        basic_auth=(os.getenv("JIRA_EMAIL"), os.getenv("JIRA_API_TOKEN"))
    )
    print("✓ JIRA connection successful")
    
    # Try fetching a test project
    projects = jira.projects()
    print(f"✓ Found {len(projects)} projects")
    for project in projects[:3]:
        print(f"  - {project.key}: {project.name}")
        
except Exception as e:
    print(f"✗ Error: {e}")
```

Run it:
```bash
python test_jira.py
```

### Test Anthropic Connection

Create a test script `test_anthropic.py`:

```python
import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

try:
    client = Anthropic()
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=100,
        messages=[{"role": "user", "content": "Say 'Hello from JIRA Summarizer!'"}]
    )
    print("✓ Anthropic connection successful")
    print(f"Response: {response.content[0].text}")
except Exception as e:
    print(f"✗ Error: {e}")
```

Run it:
```bash
python test_anthropic.py
```

## Troubleshooting

### `.env` file not found

**Error:** `ModuleNotFoundError: No module named 'dotenv'`

**Solution:**
```bash
pip install python-dotenv
```

### Cannot access .env

Make sure:
1. File is in the same directory as `jira_agent.py`
2. File is named `.env` (with leading dot)
3. File is readable by your user

### JIRA authentication fails

**Error:** `JIRA URL must not be None`

**Solution:**
- Check JIRA_URL ends without trailing slash
- Use full URL: `https://company.atlassian.net`
- Verify API token is valid (tokens can expire)

### Anthropic API key invalid

**Error:** `AuthenticationError: 401 Unauthorized`

**Solution:**
- Verify API key is copied completely
- Check key hasn't been revoked
- Generate a new key if needed

## Running the Agent

After setup is complete:

```bash
python jira_agent.py
```

The agent will:
1. Read ticket IDs from input Excel
2. Fetch each ticket from JIRA
3. Generate summaries using Claude
4. Save results to output Excel

## Security Notes

- **Never commit `.env` file** to git
- `.env` is in `.gitignore` by default
- Keep API tokens confidential
- Regenerate tokens if compromised
- Use strong, unique tokens

## Performance Tips

- **Batch size**: Process 1-2 tickets per minute
- **Large batches**: May take several minutes
- **Rate limits**: JIRA and Anthropic have rate limits
- **API costs**: Anthropic charges per token used

## Support

If you have issues:

1. Check `.env` is properly configured
2. Verify JIRA and Anthropic credentials
3. Run test scripts to isolate the problem
4. Check error messages in console output
5. Review logs for detailed information

## Next Steps

1. ✅ Install dependencies: `pip install -r requirements.txt`
2. ✅ Configure `.env` file with credentials
3. ✅ Prepare input Excel file with ticket IDs
4. ✅ Run: `python jira_agent.py`
5. ✅ Review output in `ticket_summary.xlsx`
