"""Flask UI for JIRA Ticket Summarizer.

Supports two flows:
1) Upload an Excel file with ticket IDs.
2) Enter ticket IDs manually.
"""

from __future__ import annotations

from io import BytesIO
import os
import json
import threading
import uuid
from pathlib import Path
from typing import List

import pandas as pd
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, send_file, url_for

from jira_agent import JIRATicketSummarizer


load_dotenv()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB upload cap
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

JOBS = {}
JOBS_LOCK = threading.Lock()


def _build_summarizer() -> JIRATicketSummarizer:
    jira_url = os.getenv("JIRA_BASE_URL") or os.getenv("JIRA_URL")
    jira_email = os.getenv("JIRA_EMAIL")
    jira_api_token = os.getenv("JIRA_API_TOKEN")

    if not all([jira_url, jira_email, jira_api_token]):
        raise ValueError("Missing JIRA configuration in .env")

    use_onprem = os.getenv("LLM_BASE_URL") is not None
    if use_onprem and not all([os.getenv("LLM_BASE_URL"), os.getenv("LLM_API_KEY")]):
        raise ValueError("Missing on-prem LLM configuration in .env")

    if not use_onprem and not os.getenv("ANTHROPIC_API_KEY"):
        raise ValueError("Missing ANTHROPIC_API_KEY in .env")

    return JIRATicketSummarizer(jira_url=jira_url, email=jira_email, api_token=jira_api_token)


def _parse_manual_ticket_ids(raw_value: str) -> List[str]:
    if not raw_value:
        return []

    # Accept commas, spaces, and line breaks.
    normalized = raw_value.replace(",", "\n").replace(" ", "\n")
    values = [v.strip().upper() for v in normalized.splitlines() if v.strip()]

    # Preserve order while removing duplicates.
    seen = set()
    unique_values = []
    for value in values:
        if value not in seen:
            seen.add(value)
            unique_values.append(value)
    return unique_values


def _create_job(
    ticket_ids: List[str],
    ticket_ids_text: str,
    mode: str,
    source_name: str = "",
    source_path: str = "",
) -> str:
    job_id = str(uuid.uuid4())
    with JOBS_LOCK:
        JOBS[job_id] = {
            "status": "queued",
            "mode": mode,
            "ticket_ids_text": ticket_ids_text,
            "ticket_ids": ticket_ids,
            "total": len(ticket_ids),
            "completed": 0,
            "results": [],
            "error": None,
            "source_name": source_name,
            "source_path": source_path,
        }
    return job_id


def _set_job_state(job_id: str, **kwargs) -> None:
    with JOBS_LOCK:
        if job_id in JOBS:
            JOBS[job_id].update(kwargs)


def _run_job(job_id: str) -> None:
    _set_job_state(job_id, status="running")

    with JOBS_LOCK:
        job = JOBS.get(job_id)
        ticket_ids = list(job["ticket_ids"]) if job else []

    try:
        summarizer = _build_summarizer()
    except Exception as exc:
        _set_job_state(job_id, status="failed", error=str(exc))
        return

    results = []
    completed = 0

    for ticket_id in ticket_ids:
        ticket = summarizer.fetch_ticket_details(ticket_id)
        if ticket:
            summary = summarizer.summarize_ticket_with_agent(ticket)
            result = {
                "ticket_id": ticket["ticket_id"],
                "ticket_title": ticket["title"],
                "summary": summary,
            }
        else:
            result = {
                "ticket_id": ticket_id,
                "ticket_title": "Unable to fetch ticket",
                "summary": "Unable to generate summary",
            }

        results.append(result)
        completed += 1
        _set_job_state(job_id, completed=completed, results=results)

    _set_job_state(job_id, status="done", completed=completed, results=results)


@app.get("/")
def index():
    return render_template("index.html", results=None, ticket_ids_text="", error=None, job_id="")


@app.get("/job/<job_id>")
def job_view(job_id: str):
    with JOBS_LOCK:
        job = JOBS.get(job_id)

    if not job:
        return render_template("index.html", results=None, ticket_ids_text="", error="Job not found.", job_id="")

    return render_template(
        "index.html",
        results=None,
        ticket_ids_text=job.get("ticket_ids_text", ""),
        error=None,
        job_id=job_id,
    )


@app.get("/job_status/<job_id>")
def job_status(job_id: str):
    with JOBS_LOCK:
        job = JOBS.get(job_id)

    if not job:
        return jsonify({"error": "Job not found."}), 404

    total = int(job.get("total", 0))
    completed = int(job.get("completed", 0))
    progress_pct = int((completed / total) * 100) if total else 0

    return jsonify(
        {
            "status": job.get("status", "queued"),
            "total": total,
            "completed": completed,
            "progress_pct": progress_pct,
            "error": job.get("error"),
            "results": job.get("results", []),
            "source_name": job.get("source_name", ""),
            "source_path": job.get("source_path", ""),
        }
    )


@app.post("/summarize")
def summarize():
    mode = request.form.get("mode", "manual")
    ticket_ids_text = request.form.get("ticket_ids", "")

    try:
        summarizer = _build_summarizer()
    except Exception as exc:
        return render_template("index.html", results=None, ticket_ids_text=ticket_ids_text, error=str(exc))

    try:
        source_name = ""
        source_path = ""

        if mode == "excel":
            uploaded = request.files.get("ticket_file")
            if not uploaded or not uploaded.filename:
                raise ValueError("Please choose an Excel file.")

            # Save upload to server so the exact file path can be displayed in UI.
            safe_name = Path(uploaded.filename).name
            stored_name = f"{uuid.uuid4().hex}_{safe_name}"
            stored_path = UPLOAD_DIR / stored_name
            uploaded.save(stored_path)

            source_name = safe_name
            source_path = str(stored_path.resolve())

            df = pd.read_excel(stored_path)
            if df.empty:
                raise ValueError("Uploaded Excel file is empty.")

            ticket_col = None
            for col in ["ticket_id", "Ticket ID", "ticket", "Ticket", "ID", "id"]:
                if col in df.columns:
                    ticket_col = col
                    break
            if ticket_col is None:
                ticket_col = df.columns[0]

            ticket_ids = [str(v).strip().upper() for v in df[ticket_col].dropna().tolist() if str(v).strip()]
        else:
            ticket_ids = _parse_manual_ticket_ids(ticket_ids_text)
            source_name = "Manual input"
            source_path = "N/A"

        if not ticket_ids:
            raise ValueError("No valid ticket IDs found.")

        job_id = _create_job(
            ticket_ids=ticket_ids,
            ticket_ids_text=ticket_ids_text,
            mode=mode,
            source_name=source_name,
            source_path=source_path,
        )
        worker = threading.Thread(target=_run_job, args=(job_id,), daemon=True)
        worker.start()

        return redirect(url_for("job_view", job_id=job_id))
    except Exception as exc:
        return render_template(
            "index.html",
            results=None,
            ticket_ids_text=ticket_ids_text,
            error=str(exc),
            job_id="",
        )


@app.post("/download")
def download_report():
    payload = request.form.get("results_json", "")
    if not payload:
        return "No report data found.", 400

    try:
        records = json.loads(payload)
    except json.JSONDecodeError:
        return "Invalid report payload.", 400

    if not isinstance(records, list) or not records:
        return "No valid report rows found.", 400

    df = pd.DataFrame(records)

    # Keep output columns predictable for downstream users.
    for col in ["ticket_id", "ticket_title", "summary"]:
        if col not in df.columns:
            df[col] = ""
    df = df[["ticket_id", "ticket_title", "summary"]]

    output_stream = BytesIO()
    with pd.ExcelWriter(output_stream, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Tickets", index=False)
    output_stream.seek(0)

    return send_file(
        output_stream,
        as_attachment=True,
        download_name="ticket_summary_from_ui.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
