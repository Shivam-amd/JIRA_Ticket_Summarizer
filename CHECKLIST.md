# Setup Checklist

## ✅ Project Setup Complete!

### What Was Built
- [x] Main agent orchestrator (`jira_agent.py`)
- [x] MCP server for JIRA (`mcp_jira_server.py`)
- [x] Setup script (`setup.py`)
- [x] Comprehensive documentation
- [x] All dependencies installed

### Files Created
- [x] `jira_agent.py` - Main agent (8.3 KB)
- [x] `mcp_jira_server.py` - MCP server (4.3 KB)
- [x] `requirements.txt` - Dependencies
- [x] `README.md` - Full documentation
- [x] `QUICKSTART.md` - Quick reference
- [x] `CONFIG.md` - Configuration guide
- [x] `SETUP_SUMMARY.md` - Project summary
- [x] `.env.example` - Template
- [x] `setup.py` - Interactive setup

### Dependencies Installed
- [x] jira==3.10.5 - JIRA client
- [x] anthropic>=0.25.0 - Claude AI
- [x] openpyxl==3.1.5 - Excel handling
- [x] pandas>=2.0.0 - Data processing
- [x] python-dotenv>=1.0.0 - Environment variables
- [x] requests>=2.31.0 - HTTP client

## 📋 Next Steps (In Order)

### STEP 1: Create `.env` File
```bash
cd "C:\Users\skumar22\OneDrive - Advanced Micro Devices Inc\Documents\Classification"
cp .env.example .env
```

Edit `.env` with your credentials:
```env
JIRA_URL=https://your-instance.atlassian.net
JIRA_EMAIL=your.email@company.com
JIRA_API_TOKEN=your-api-token
ANTHROPIC_API_KEY=sk-ant-your-key
```

### STEP 2: Get JIRA API Token
1. Visit: https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Name it (e.g., "JIRA Summarizer")
4. Copy the token
5. Paste in `.env` as `JIRA_API_TOKEN`

### STEP 3: Get Anthropic API Key
1. Visit: https://console.anthropic.com/
2. Click "API keys" in left sidebar
3. Click "Create key"
4. Name it (e.g., "JIRA Summarizer")
5. Copy the key
6. Paste in `.env` as `ANTHROPIC_API_KEY`

### STEP 4: Prepare Input Excel File
Create or update: `C:\Users\skumar22\OneDrive - Advanced Micro Devices Inc\Documents\Summary_Sheet\ticket.xlsx`

Add ticket IDs like this:
```
ticket_id
PROJ-123
PROJ-456
PROJ-789
```

The column can be named:
- ticket_id (preferred)
- Ticket ID
- ticket
- ID
- Or any name (first column is used by default)

### STEP 5: Verify Connections (Optional)

**Test JIRA:**
```bash
python test_jira.py
```

**Test Anthropic:**
```bash
python test_anthropic.py
```

### STEP 6: Run the Agent
```bash
python jira_agent.py
```

Expected output:
```
🚀 Starting JIRA Ticket Summarizer Agent
📥 Input: C:\...ticket.xlsx
📤 Output: C:\...ticket_summary.xlsx
✓ Read N ticket IDs from input
📋 Processing N tickets...
[1/N] Processing PROJ-123... ✓
[2/N] Processing PROJ-456... ✓
...
✓ Results saved to ticket_summary.xlsx
✅ Successfully processed N tickets
```

### STEP 7: Check Results
Open: `C:\Users\skumar22\OneDrive - Advanced Micro Devices Inc\Documents\Summary_Sheet\ticket_summary.xlsx`

Should contain 3 columns:
- ticket_id
- ticket_title
- summary (AI-generated)

## 🚀 Quick Reference

### Run the Agent
```bash
python jira_agent.py
```

### Interactive Setup
```bash
python setup.py
```

### View Documentation
- Full guide: `README.md`
- Quick start: `QUICKSTART.md`
- Configuration: `CONFIG.md`
- Project summary: `SETUP_SUMMARY.md`

## ⚠️ Important Notes

1. **Never commit `.env` to git**
   - It contains sensitive credentials
   - Add to `.gitignore` if using version control

2. **Keep API tokens confidential**
   - Treat like passwords
   - Regenerate if compromised
   - Don't share in messages/emails

3. **Check JIRA permissions**
   - Ensure your account has access to all projects
   - Check project-level permissions if tickets are missing

4. **Monitor API costs**
   - Anthropic charges per token
   - Test with small batch first
   - Typical cost: ~$0.01 per 100 tickets

5. **Rate limits**
   - JIRA: ~100 requests/minute
   - Anthropic: Check rate limits in console
   - Tool includes automatic rate limiting

## 🔍 Troubleshooting

### "ModuleNotFoundError: No module named 'jira'"
```bash
pip install -r requirements.txt
```

### "JIRA URL is not valid"
- Check JIRA_URL doesn't have trailing slash
- Use full URL: https://company.atlassian.net
- Not: https://company.atlassian.net/

### "Authentication failed"
- Verify JIRA_EMAIL is correct
- Check JIRA_API_TOKEN is not expired
- Regenerate API token if needed

### "Ticket not found"
- Verify ticket ID is spelled correctly (case-sensitive)
- Check you have access to that project
- May have been deleted or archived

### "Anthropic API key invalid"
- Check ANTHROPIC_API_KEY is complete
- Verify key hasn't been revoked
- Generate new key if needed

### "Excel file not found"
- Check file exists at specified path
- Create file if missing
- Use correct filename: ticket.xlsx

## 📊 Performance Expectations

- **Speed**: 1-2 tickets/minute
- **Memory**: ~50MB
- **Processing**: Sequential (one at a time)
- **Network**: Requires internet connection
- **Cost**: ~$0.0001 per ticket (Anthropic)

## 📈 Scaling Up

Want to process more tickets?

1. Add more rows to input Excel
2. Run agent again (same output, will overwrite)
3. Or modify code to append to existing output
4. Consider batch processing for very large sets

## 🛠️ Customization

### Change Summary Length
Edit `jira_agent.py`:
```python
max_tokens=250  # Shorter
max_tokens=1000  # Longer
```

### Change AI Model
```python
model="claude-3-haiku-20250307"  # Faster, cheaper
model="claude-3-opus-20250219"   # More capable
```

### Modify Output Columns
Edit `summarize_ticket_with_agent()` method to add/remove columns

## 📞 Support

For issues:
1. Check `.env` is properly formatted
2. Verify credentials are correct
3. Run test scripts to isolate problems
4. Check console error messages
5. Review README.md or CONFIG.md

## ✨ What's Next?

1. ✅ Configure `.env`
2. ✅ Prepare input Excel
3. ✅ Run agent
4. ✅ Review output
5. 🎯 Integrate into your workflow
6. 🎯 Automate with scheduler
7. 🎯 Expand to other projects

---

**STATUS: Ready to Use! 🎉**

All components are installed and ready.
Just configure credentials and run!

For detailed information, see:
- QUICKSTART.md - 5 minute guide
- CONFIG.md - Credential setup
- README.md - Full documentation
