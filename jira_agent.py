"""Main Agent Tool for JIRA Ticket Summarization"""
import json
import pandas as pd
from jira import JIRA
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# Determine which LLM to use
USE_ONPREM_LLM = os.getenv("LLM_BASE_URL") is not None

if USE_ONPREM_LLM:
    from openai import OpenAI
    print("Using On-Premises LLM")
else:
    from anthropic import Anthropic
    print("Using Anthropic Claude")

class JIRATicketSummarizer:
    """Agent that reads JIRA tickets and summarizes them"""
    
    def __init__(self, jira_url: str, email: str, api_token: str):
        """Initialize the summarizer with JIRA credentials"""
        self.jira = JIRA(
            server=jira_url,
            basic_auth=(email, api_token)
        )
        
        # Initialize LLM client based on configuration
        self.use_onprem_llm = os.getenv("LLM_BASE_URL") is not None
        
        if self.use_onprem_llm:
            # Use OpenAI-compatible on-premises LLM
            # Some gateways require Ocp-Apim-Subscription-Key and may use the same
            # value as the API key. Prefer explicit subscription key, then fallback.
            subscription_key = os.getenv("LLM_SUBSCRIPTION_KEY") or os.getenv("LLM_API_KEY")
            client_kwargs = {
                "base_url": os.getenv("LLM_BASE_URL"),
                "api_key": os.getenv("LLM_API_KEY"),
            }
            if subscription_key:
                client_kwargs["default_headers"] = {
                    "Ocp-Apim-Subscription-Key": subscription_key
                }

            self.llm_client = OpenAI(
                **client_kwargs
            )
            self.llm_model = os.getenv("LLM_MODEL", "gpt-4.1-mini")
            print(f"[SUCCESS] Connected to on-premises LLM at {os.getenv('LLM_BASE_URL')}")
        else:
            # Use Anthropic Claude
            self.llm_client = Anthropic()
            self.llm_model = "claude-3-5-sonnet-20241022"
            print("[SUCCESS] Using Anthropic Claude API")
        
        self.conversation_history = []

    def _user_display(self, user_obj) -> str:
        """Return a readable user name across Jira Cloud/Server variants."""
        if not user_obj:
            return ""
        return (
            getattr(user_obj, "displayName", None)
            or getattr(user_obj, "name", None)
            or getattr(user_obj, "emailAddress", None)
            or ""
        )

    def _trim_text(self, text: str, limit: int = 1000) -> str:
        """Trim long text fields to keep token usage bounded."""
        if not text:
            return ""
        value = str(text)
        if len(value) <= limit:
            return value
        return value[:limit] + "..."
        
    def read_ticket_ids_from_excel(self, excel_path: str) -> list[str]:
        """Read JIRA ticket IDs from Excel file"""
        try:
            df = pd.read_excel(excel_path)
            # Look for common column names
            ticket_col = None
            for col in ['ticket_id', 'Ticket ID', 'ticket', 'Ticket', 'ID', 'id']:
                if col in df.columns:
                    ticket_col = col
                    break
            
            if ticket_col is None:
                # Default to first column
                ticket_col = df.columns[0]
            
            ticket_ids = df[ticket_col].astype(str).tolist()
            print(f"[SUCCESS] Read {len(ticket_ids)} ticket IDs from {excel_path}")
            return ticket_ids
        except Exception as e:
            print(f"[FAILED] Error reading Excel file: {e}")
            return []
    
    def fetch_ticket_details(self, ticket_id: str) -> dict:
        """Fetch ticket details from JIRA"""
        try:
            issue = self.jira.issue(ticket_id)
            fields = issue.fields

            # Watchers are not always included on issue.fields and can require a separate API call.
            watchers = []
            try:
                watchers_data = self.jira.watchers(ticket_id)
                watchers = [self._user_display(w) for w in getattr(watchers_data, "watchers", []) if self._user_display(w)]
            except Exception:
                watchers = []

            issuelinks = []
            for link in getattr(fields, "issuelinks", []) or []:
                link_type = getattr(getattr(link, "type", None), "name", "")
                inward = getattr(link, "inwardIssue", None)
                outward = getattr(link, "outwardIssue", None)
                if inward:
                    issuelinks.append({
                        "type": link_type,
                        "direction": "inward",
                        "key": getattr(inward, "key", ""),
                        "summary": getattr(getattr(inward, "fields", None), "summary", ""),
                    })
                if outward:
                    issuelinks.append({
                        "type": link_type,
                        "direction": "outward",
                        "key": getattr(outward, "key", ""),
                        "summary": getattr(getattr(outward, "fields", None), "summary", ""),
                    })

            comments = []
            for c in (getattr(getattr(fields, "comment", None), "comments", []) or [])[:10]:
                comments.append({
                    "author": self._user_display(getattr(c, "author", None)) or "Unknown",
                    "created": str(getattr(c, "created", "")),
                    "body": self._trim_text(getattr(c, "body", ""), 1200),
                })

            attachments = []
            for a in getattr(fields, "attachment", []) or []:
                attachments.append({
                    "filename": getattr(a, "filename", ""),
                    "size": getattr(a, "size", None),
                    "mimeType": getattr(a, "mimeType", ""),
                    "created": str(getattr(a, "created", "")),
                    "author": self._user_display(getattr(a, "author", None)) or "Unknown",
                })

            worklogs = []
            for w in (getattr(getattr(fields, "worklog", None), "worklogs", []) or [])[:20]:
                worklogs.append({
                    "author": self._user_display(getattr(w, "author", None)) or "Unknown",
                    "created": str(getattr(w, "created", "")),
                    "timeSpent": getattr(w, "timeSpent", ""),
                    "timeSpentSeconds": getattr(w, "timeSpentSeconds", None),
                    "comment": self._trim_text(getattr(w, "comment", ""), 400),
                })

            subtasks = []
            for st in getattr(fields, "subtasks", []) or []:
                subtasks.append({
                    "key": getattr(st, "key", ""),
                    "summary": getattr(getattr(st, "fields", None), "summary", ""),
                    "status": getattr(getattr(getattr(st, "fields", None), "status", None), "name", ""),
                })

            components = [getattr(c, "name", "") for c in (getattr(fields, "components", []) or []) if getattr(c, "name", None)]
            fix_versions = [getattr(v, "name", "") for v in (getattr(fields, "fixVersions", []) or []) if getattr(v, "name", None)]
            affected_versions = [getattr(v, "name", "") for v in (getattr(fields, "versions", []) or []) if getattr(v, "name", None)]

            parent = getattr(fields, "parent", None)
            parent_info = {
                "key": getattr(parent, "key", "") if parent else "",
                "summary": getattr(getattr(parent, "fields", None), "summary", "") if parent else "",
            }

            issue_type = getattr(getattr(fields, "issuetype", None), "name", "")
            priority = getattr(getattr(fields, "priority", None), "name", "")
            reporter = self._user_display(getattr(fields, "reporter", None)) or ""
            assignee = self._user_display(getattr(fields, "assignee", None)) or "Unassigned"
            resolution = getattr(getattr(fields, "resolution", None), "name", "")
            environment = self._trim_text(getattr(fields, "environment", ""), 1000)

            timetracking = getattr(fields, "timetracking", None)
            timetracking_info = {
                "originalEstimate": getattr(timetracking, "originalEstimate", "") if timetracking else "",
                "remainingEstimate": getattr(timetracking, "remainingEstimate", "") if timetracking else "",
                "timeSpent": getattr(timetracking, "timeSpent", "") if timetracking else "",
                "originalEstimateSeconds": getattr(timetracking, "originalEstimateSeconds", None) if timetracking else None,
                "remainingEstimateSeconds": getattr(timetracking, "remainingEstimateSeconds", None) if timetracking else None,
                "timeSpentSeconds": getattr(timetracking, "timeSpentSeconds", None) if timetracking else None,
            }

            project = getattr(fields, "project", None)
            project_info = {
                "key": getattr(project, "key", "") if project else "",
                "name": getattr(project, "name", "") if project else "",
            }

            return {
                "ticket_id": issue.key,
                "title": getattr(fields, "summary", ""),
                "description": self._trim_text(getattr(fields, "description", ""), 6000),
                "status": getattr(getattr(fields, "status", None), "name", ""),
                "issue_type": issue_type,
                "priority": priority,
                "reporter": reporter,
                "assignee": assignee,
                "resolution": resolution,
                "resolution_date": str(getattr(fields, "resolutiondate", "")),
                "labels": list(getattr(fields, "labels", []) or []),
                "components": components,
                "fix_versions": fix_versions,
                "affected_versions": affected_versions,
                "due_date": str(getattr(fields, "duedate", "")),
                "environment": environment,
                "project": project_info,
                "parent": parent_info,
                "subtasks": subtasks,
                "linked_issues": issuelinks,
                "comments": comments,
                "attachments": attachments,
                "worklogs": worklogs,
                "watchers": watchers,
                "timetracking": timetracking_info,
                "created": str(getattr(fields, "created", "")),
                "updated": str(getattr(fields, "updated", "")),
            }
        except Exception as e:
            print(f"[FAILED] Error fetching ticket {ticket_id}: {e}")
            return None
    
    def summarize_ticket_with_agent(self, ticket: dict) -> str:
        """Use LLM to summarize a ticket (Anthropic or On-Premises)"""
        jira_payload = json.dumps(ticket, indent=2, ensure_ascii=True)
        user_message = f"""
Please provide a concise summary of this JIRA ticket:

    JIRA ticket payload:
    {jira_payload}

    Provide a brief 3-5 sentence summary that captures:
    1) the main issue and business/engineering impact,
    2) key technical context and dependencies,
    3) current status, ownership, and timeline signals,
    4) notable risks or blockers from links/comments/worklogs.
"""
        
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        try:
            if self.use_onprem_llm:
                # Use OpenAI-compatible API
                response = self.llm_client.chat.completions.create(
                    model=self.llm_model,
                    max_tokens=500,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful assistant that summarizes JIRA tickets concisely and accurately. Focus on the core issue and impact.",
                        },
                        *self.conversation_history,
                    ]
                )
                summary = response.choices[0].message.content
            else:
                # Use Anthropic API
                response = self.llm_client.messages.create(
                    model=self.llm_model,
                    max_tokens=500,
                    system="You are a helpful assistant that summarizes JIRA tickets concisely and accurately. Focus on the core issue and impact.",
                    messages=self.conversation_history
                )
                summary = response.content[0].text
            
            # Keep last 5 exchanges for context
            self.conversation_history.append({
                "role": "assistant",
                "content": summary
            })
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            return summary
        except Exception as e:
            print(f"[FAILED] Error summarizing ticket: {e}")
            return "Unable to generate summary"
    
    def process_tickets(self, ticket_ids: list[str]) -> list[dict]:
        """Process all tickets and generate summaries"""
        results = []
        
        print(f"\n[INFO] Processing {len(ticket_ids)} tickets...")
        for i, ticket_id in enumerate(ticket_ids, 1):
            print(f"[{i}/{len(ticket_ids)}] Processing {ticket_id}...", end=" ")
            
            ticket = self.fetch_ticket_details(ticket_id)
            if ticket:
                summary = self.summarize_ticket_with_agent(ticket)
                result = {
                    "ticket_id": ticket["ticket_id"],
                    "ticket_title": ticket["title"],
                    "summary": summary
                }
                results.append(result)
                print("[SUCCESS]")
            else:
                print("[FAILED]")
        
        return results
    
    def save_results_to_excel(self, results: list[dict], output_path: str) -> bool:
        """Save results to Excel file"""
        def _write_excel(path: str) -> None:
            df = pd.DataFrame(results)

            # Ensure correct column order
            df = df[["ticket_id", "ticket_title", "summary"]]

            # Create excel writer with formatting
            with pd.ExcelWriter(path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Tickets', index=False)

                # Get the workbook and worksheet
                workbook = writer.book
                worksheet = writer.sheets['Tickets']

                # Auto-adjust column widths
                worksheet.column_dimensions['A'].width = 15
                worksheet.column_dimensions['B'].width = 40
                worksheet.column_dimensions['C'].width = 60

                # Wrap text in summary column
                from openpyxl.styles import Alignment
                for row in worksheet.iter_rows(min_col=3, max_col=3, min_row=2):
                    for cell in row:
                        cell.alignment = Alignment(wrap_text=True, vertical='top')

        try:
            _write_excel(output_path)
            print(f"\n[SUCCESS] Results saved to {output_path}")
            return True
        except PermissionError:
            # Excel often holds a lock if the file is open; save to an alternate name.
            base = Path(output_path)
            timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
            fallback_path = str(base.with_name(f"{base.stem}_{timestamp}{base.suffix}"))
            try:
                _write_excel(fallback_path)
                print(f"\n[INFO] Output file is locked: {output_path}")
                print(f"[SUCCESS] Results saved to alternate file: {fallback_path}")
                return True
            except Exception as e:
                print(f"[FAILED] Error saving fallback results: {e}")
                return False
        except Exception as e:
            print(f"[FAILED] Error saving results: {e}")
            return False
    
    def run(self, input_excel_path: str, output_excel_path: str) -> bool:
        """Main workflow: read tickets, summarize, and save results"""
        print("[INFO] Starting JIRA Ticket Summarizer Agent")
        print(f"[INPUT] {input_excel_path}")
        print(f"[OUTPUT] {output_excel_path}")
        
        # Step 1: Read ticket IDs from input Excel
        ticket_ids = self.read_ticket_ids_from_excel(input_excel_path)
        if not ticket_ids:
            print("[FAILED] No ticket IDs found")
            return False
        
        # Step 2: Process each ticket
        results = self.process_tickets(ticket_ids)
        
        if not results:
            print("[FAILED] No tickets were successfully processed")
            return False
        
        # Step 3: Save results to output Excel
        success = self.save_results_to_excel(results, output_excel_path)
        
        if success:
            print(f"\n[SUCCESS] Successfully processed {len(results)} tickets")
        
        return success


def main():
    """Main entry point"""
    # Load JIRA credentials from environment
    jira_url = os.getenv("JIRA_BASE_URL") or os.getenv("JIRA_URL")  # Support both names
    jira_email = os.getenv("JIRA_EMAIL")
    jira_api_token = os.getenv("JIRA_API_TOKEN")
    
    if not all([jira_url, jira_email, jira_api_token]):
        print("[FAILED] Missing JIRA credentials in environment variables")
        print("Please set JIRA_URL, JIRA_EMAIL, and JIRA_API_TOKEN")
        return False
    
    # Check LLM configuration
    use_onprem = os.getenv("LLM_BASE_URL") is not None
    
    if use_onprem:
        # On-premises LLM
        if not all([os.getenv("LLM_BASE_URL"), os.getenv("LLM_API_KEY")]):
            print("[FAILED] Missing on-premises LLM credentials")
            print("Please set LLM_BASE_URL, LLM_API_KEY, and optionally LLM_SUBSCRIPTION_KEY and LLM_MODEL")
            return False
        print("[INFO] Using on-premises LLM")
    else:
        # Anthropic API
        if not os.getenv("ANTHROPIC_API_KEY"):
            print("[FAILED] Missing Anthropic API key")
            print("Please set ANTHROPIC_API_KEY or configure on-premises LLM")
            return False
        print("[INFO] Using Anthropic Claude API")
    
    # Initialize summarizer with error handling
    try:
        print(f"\n[INFO] Connecting to JIRA: {jira_url}")
        summarizer = JIRATicketSummarizer(
            jira_url=jira_url,
            email=jira_email,
            api_token=jira_api_token
        )
    except Exception as e:
        error_msg = str(e)
        
        # Check for common errors
        if "401" in error_msg or "Unauthorized" in error_msg:
            print("\n[FAILED] JIRA AUTHENTICATION FAILED (HTTP 401)")
            print("\nPossible causes:")
            print("  1. JIRA_EMAIL is incorrect")
            print("  2. JIRA_API_TOKEN is invalid or expired")
            print("  3. API token has insufficient permissions")
            print("  4. JIRA instance requires different authentication")
            print("\nSolutions:")
            print("  * Double-check your JIRA email address")
            print("  * Verify API token hasn't expired")
            print("  * Generate a new API token if needed")
            print("  * Run: python test_jira_connection.py for diagnostics")
            return False
        else:
            print(f"\n[FAILED] JIRA Connection Error: {error_msg}")
            print("Troubleshooting:")
            print("  * Verify JIRA_URL is correct")
            print("  * Check network connectivity")
            print("  * Ensure JIRA server is running")
            return False
    
    # Define paths
    input_path = r"C:\Users\skumar22\OneDrive - Advanced Micro Devices Inc\Documents\Summary_Sheet\ticket.xlsx"
    output_path = r"C:\Users\skumar22\OneDrive - Advanced Micro Devices Inc\Documents\Summary_Sheet\ticket_summary.xlsx"
    
    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Run the agent
    return summarizer.run(input_path, output_path)


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
