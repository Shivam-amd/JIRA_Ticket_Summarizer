# Atlassian Cloud JIRA Setup Guide

## Overview

This guide covers setting up the JIRA Ticket Summarizer with **Atlassian Cloud JIRA**.

---

## 🚀 Quick Setup

### Your Configuration
```env
JIRA_URL=https://amd.atlassian.net
JIRA_EMAIL=shivam.kumar2@amd.com
JIRA_API_TOKEN=your-api-token
```

---

## 🔑 Step 1: Get Your Atlassian API Token

### Option A: Cloud API Token (Recommended)

1. **Go to**: https://id.atlassian.com/manage-profile/security/api-tokens
2. **Log in** with your Atlassian account
3. **Click**: "Create API token"
4. **Name it**: `JIRA Ticket Summarizer`
5. **Copy the token** (visible only once!)
6. **Save to `.env`**:
   ```env
   JIRA_API_TOKEN=your-token-here
   ```

---

## ✅ Step 2: Verify Your Setup

### Update `.env` with:
```env
# JIRA Cloud (Atlassian) Configuration
JIRA_URL=https://amd.atlassian.net
JIRA_EMAIL=shivam.kumar2@amd.com
JIRA_API_TOKEN=your-api-token-here

# LLM Configuration
LLM_BASE_URL=https://llm-api.amd.com/OnPrem
LLM_API_KEY=562ebc96a3124e00920a32fddbdf8216
LLM_MODEL=gpt-4.1-mini
```

### Test the connection:
```bash
python test_jira_connection.py
```

Expected output:
```
TEST 1: Direct REST API Call (Basic Auth)
Status Code: 200
[SUCCESS] Authentication successful!
```

---

## 🎯 Step 3: Run the Agent

```bash
python jira_agent.py
```

The agent will:
1. ✓ Connect to Atlassian Cloud JIRA
2. ✓ Read ticket IDs from Excel
3. ✓ Fetch each ticket
4. ✓ Summarize using on-premises LLM
5. ✓ Save results to Excel

---

## 📊 Understanding Atlassian Cloud API

### Authentication
- **Method**: HTTP Basic Auth
- **Email**: Your Atlassian account email
- **Token**: API token (NOT password)

### API Endpoints
```
Base: https://your-company.atlassian.net/rest/api/2/

Examples:
- Get issue: /issue/PROJ-123
- Search: /search?jql=...
- Server info: /serverInfo
```

---

## 🔧 Troubleshooting

### Issue: HTTP 401 Unauthorized

**Solutions**:
1. Verify email is exactly correct
2. Check API token hasn't expired
3. Generate a new token if needed
4. Run: `python test_jira_connection.py`

### Issue: HTTP 404 Not Found

**Solutions**:
1. Verify JIRA_URL is correct: `https://amd.atlassian.net`
2. Check that ticket IDs exist in JIRA
3. Ensure you have access to the project

### Issue: Connection Timeout

**Solutions**:
1. Check internet connection
2. Verify firewall isn't blocking JIRA
3. Try accessing JIRA in browser first

---

## 💡 Tips

### Finding Your JIRA Cloud URL
- Go to your JIRA instance
- URL is in format: `https://your-company.atlassian.net`
- Example: `https://amd.atlassian.net`

### API Token Security
- ⚠️ Never commit to git
- ⚠️ Keep in `.env` only (add to `.gitignore`)
- ⚠️ Regenerate if exposed
- ✅ Tokens are safer than passwords

### Batch Processing
- Add all ticket IDs to Excel
- Run agent once to process all
- No need to run multiple times

---

## ✨ Full Workflow

```
1. Prepare Input Excel
   └─ Add JIRA ticket IDs

2. Run Agent
   └─ python jira_agent.py

3. Agent processes each ticket:
   ├─ Fetches from Atlassian Cloud
   ├─ Sends to on-premises LLM
   └─ Generates summary

4. Review Output Excel
   └─ ticket_summary.xlsx
```

---

## 📞 Support

For Atlassian Cloud issues:
- Atlassian docs: https://docs.atlassian.com/
- API reference: https://developer.atlassian.com/cloud/jira/

For tool issues:
- Run: `python test_jira_connection.py`
- Check: README.md
- Review: error messages in console

---

## ✅ Checklist

- [ ] Have Atlassian Cloud JIRA account
- [ ] Generated API token
- [ ] Updated `.env` with credentials
- [ ] Ran `test_jira_connection.py` successfully
- [ ] Prepared input Excel with ticket IDs
- [ ] Ready to run `python jira_agent.py`

---

**You're ready to summarize JIRA tickets with Atlassian Cloud!** 🎉
