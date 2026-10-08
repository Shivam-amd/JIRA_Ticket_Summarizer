"""MCP Server for JIRA integration"""
import json
from jira import JIRA
from mcp.server import Server
from mcp.types import Tool, TextContent, ToolResult
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize MCP Server
server = Server("jira-mcp-server")

# JIRA configuration
JIRA_URL = os.getenv("JIRA_BASE_URL") or os.getenv("JIRA_URL", "https://your-instance.atlassian.net")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

jira_client = None


def connect_to_jira():
    """Initialize JIRA connection"""
    global jira_client
    try:
        jira_client = JIRA(
            server=JIRA_URL,
            basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN)
        )
        return True
    except Exception as e:
        print(f"Failed to connect to JIRA: {e}")
        return False


@server.call_tool()
async def handle_tool_call(name: str, arguments: dict) -> ToolResult:
    """Handle tool calls from the MCP client"""
    
    if name == "get_ticket":
        ticket_id = arguments.get("ticket_id")
        if not jira_client:
            connect_to_jira()
        
        try:
            issue = jira_client.issue(ticket_id)
            return ToolResult(
                content=[TextContent(
                    type="text",
                    text=json.dumps({
                        "ticket_id": issue.key,
                        "title": issue.fields.summary,
                        "description": issue.fields.description or "",
                        "status": issue.fields.status.name,
                        "assignee": issue.fields.assignee.name if issue.fields.assignee else "Unassigned",
                    })
                )]
            )
        except Exception as e:
            return ToolResult(
                content=[TextContent(type="text", text=f"Error fetching ticket {ticket_id}: {str(e)}")],
                is_error=True
            )
    
    elif name == "get_tickets_batch":
        ticket_ids = arguments.get("ticket_ids", [])
        if not jira_client:
            connect_to_jira()
        
        try:
            results = []
            for ticket_id in ticket_ids:
                issue = jira_client.issue(ticket_id)
                results.append({
                    "ticket_id": issue.key,
                    "title": issue.fields.summary,
                    "description": issue.fields.description or "",
                    "status": issue.fields.status.name,
                })
            return ToolResult(content=[TextContent(type="text", text=json.dumps(results))])
        except Exception as e:
            return ToolResult(
                content=[TextContent(type="text", text=f"Error fetching batch: {str(e)}")],
                is_error=True
            )
    
    return ToolResult(
        content=[TextContent(type="text", text=f"Unknown tool: {name}")],
        is_error=True
    )


# Define available tools
def get_tools() -> list[Tool]:
    """Return list of available tools"""
    return [
        Tool(
            name="get_ticket",
            description="Fetch a single JIRA ticket by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticket_id": {
                        "type": "string",
                        "description": "The JIRA ticket ID (e.g., PROJ-123)"
                    }
                },
                "required": ["ticket_id"]
            }
        ),
        Tool(
            name="get_tickets_batch",
            description="Fetch multiple JIRA tickets by their IDs",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticket_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of JIRA ticket IDs"
                    }
                },
                "required": ["ticket_ids"]
            }
        )
    ]


if __name__ == "__main__":
    # Test connection
    if connect_to_jira():
        print("✓ Connected to JIRA successfully")
    else:
        print("✗ Failed to connect to JIRA")
