# MCP JIRA Integration Guide

## Overview

The `mcp.json` file configures the Model Context Protocol (MCP) server for JIRA. This allows seamless integration with Atlassian JIRA using the official MCP server.

## Files Created

### 1. mcp.json
```json
{
  "mcpServers": {
    "jira": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-jira"],
      "env": {
        "JIRA_API_TOKEN": "${JIRA_API_TOKEN}",
        "JIRA_EMAIL": "${JIRA_EMAIL}",
        "JIRA_BASE_URL": "${JIRA_BASE_URL}"
      }
    }
  }
}
```

**Location:** `C:\Users\skumar22\OneDrive - Advanced Micro Devices Inc\Documents\Classification\mcp.json`

## Configuration

### Environment Variables (.env)

The MCP server reads these variables from your `.env` file:

- `JIRA_BASE_URL`: Your JIRA instance base URL (e.g., https://amd.atlassian.net)
- `JIRA_EMAIL`: Your email address (e.g., shivam.kumar2@amd.com)
- `JIRA_API_TOKEN`: Your JIRA API token

### Updated .env Variables

The `.env` file now uses `JIRA_BASE_URL` instead of `JIRA_URL`:

```
JIRA_BASE_URL=https://amd.atlassian.net
JIRA_EMAIL=shivam.kumar2@amd.com
JIRA_API_TOKEN=ATATT3xFfGF0llc_10qQdTtuEY5eQn8yzPqAceXAmkf8BHneMq5xfif_J_0KET5JF5xye-5NnmwolCHoKa46S4r4tyHsidxurD0vtKEQA_ShOBWqIwZBjWHjfTgVBExuiHn2pN3mHIbOIoI_jN5aEa8xVa6M4STSn-0BfPZRGxO9szuv2pbY9uI=DB322DE2
```

## How to Use

### With VS Code Copilot

1. The MCP server will be loaded automatically if VS Code recognizes `mcp.json`
2. Copilot can then access JIRA API methods
3. Use natural language to query and manage JIRA tickets

### With Claude Desktop

If using Claude Desktop with MCP support:

1. Claude reads `mcp.json` on startup
2. JIRA server is initialized with your credentials from `.env`
3. You can interact with JIRA through Claude's interface

### With Python Script

Your `jira_agent.py` has been updated to support both `JIRA_BASE_URL` and `JIRA_URL`:

```bash
python jira_agent.py
```

## MCP Server Functions

The official MCP JIRA server typically provides:

- **Search Issues**: Query JIRA using JQL
- **Get Issue Details**: Fetch specific ticket information
- **Create Issues**: Create new tickets
- **Update Issues**: Modify existing tickets
- **Assign Issues**: Change issue assignments
- **Add Comments**: Add comments to tickets
- **List Projects**: Get available projects
- **Get Project Details**: Fetch project information

## Authentication Notes

The MCP server handles authentication using:
- Basic Auth with `JIRA_EMAIL` and `JIRA_API_TOKEN`
- Credentials passed via environment variables from `.env`

## Troubleshooting

### If MCP Server Doesn't Start

1. **Check Node.js installation:**
   ```bash
   node --version
   npm --version
   ```

2. **Verify credentials in .env:**
   - `JIRA_BASE_URL` is correct
   - `JIRA_EMAIL` is correct
   - `JIRA_API_TOKEN` is valid and not expired

3. **Check if MCP package is available:**
   ```bash
   npm search @modelcontextprotocol/server-jira
   ```

### If JIRA Requests Fail

1. Verify you have access to the tickets/projects
2. Check if your API token is still valid
3. Ensure your JIRA account has API access enabled
4. For SSO accounts, contact your JIRA admin for alternative auth methods

## Integration with Your Tool

The `jira_agent.py` script now reads both:
- `JIRA_BASE_URL` (new, preferred)
- `JIRA_URL` (fallback for backward compatibility)

This ensures compatibility with both the MCP configuration and the Python script.

## Next Steps

1. **Test the MCP configuration** with VS Code or Claude Desktop
2. **Verify JIRA connectivity** using the official MCP tools
3. **Consider replacing Python script** with MCP-based queries if integration is seamless
4. **Monitor authentication** - ensure tokens don't expire

## Security Notes

⚠️ **Important:**
- Never commit `.env` file to version control
- Keep your API token confidential
- Rotate tokens periodically
- Use `.env.example` as a template for sharing configuration structure

## References

- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Atlassian JIRA API Documentation](https://developer.atlassian.com/cloud/jira/rest/)
- [MCP JIRA Server GitHub](https://github.com/modelcontextprotocol/servers)
