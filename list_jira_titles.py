"""List ticket IDs and titles fetched from Jira without invoking the LLM."""
import os

from dotenv import load_dotenv

from jira_agent import JIRATicketSummarizer


def main() -> int:
    load_dotenv()

    summarizer = JIRATicketSummarizer(
        jira_url=os.getenv("JIRA_BASE_URL") or os.getenv("JIRA_URL"),
        email=os.getenv("JIRA_EMAIL"),
        api_token=os.getenv("JIRA_API_TOKEN"),
    )

    input_path = r"C:\Users\skumar22\OneDrive - Advanced Micro Devices Inc\Documents\Summary_Sheet\ticket.xlsx"
    ticket_ids = summarizer.read_ticket_ids_from_excel(input_path)
    print(f"TICKET_COUNT={len(ticket_ids)}")

    for ticket_id in ticket_ids:
        ticket = summarizer.fetch_ticket_details(ticket_id)
        if ticket:
            print(f"{ticket['ticket_id']} | {ticket['title']}")
        else:
            print(f"{ticket_id} | <fetch failed>")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())