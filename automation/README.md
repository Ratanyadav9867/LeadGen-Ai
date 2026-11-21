# LeadGen AI — n8n Lead Capture, Gemini AI & Gmail Delivery Pipeline (Phase 6)

This directory contains the production-ready, importable n8n workflow orchestrating the complete end-to-end lifecycle: **inbound capture from Google Sheets, validation, duplicate prevention, Google Gemini AI personalization, draft persistence, duplicate-send prevention, Gmail OAuth dispatch, and dual-system status synchronization**.

Workflow file: `automation/workflows/lead-capture-workflow.json` (22 nodes, 17 connections)

---

## 🏗️ End-to-End Pipeline Architecture

```
[Google Form Submission]
         │
         ▼
[Google Sheets New Row Appended]
         │
         ▼
[Node 1: Google Sheets Trigger]
         │
         ▼
[Node 2: Normalize Lead Data] (Trims spaces, lowercases email, preserves row #)
         │
         ▼
[Node 3 & 4: Validate Lead] 
         ├── (Invalid) ────► [Node 22: Google Sheets Update (Invalid)]
         │
         ▼ (Valid)
[Node 5 & 6: Check Duplicate in FastAPI] (GET /api/leads/check-duplicate?email=...)
         ├── (Duplicate) ──► [Node 21: Google Sheets Update (Duplicate / Skipped)]
         │
         ▼ (New Lead)
[Node 7: FastAPI Ingestion] (POST /api/automation/lead-capture)
         │
         ▼
[Node 8: Gemini AI Generation] (POST https://generativelanguage.googleapis.com/...:generateContent)
         │
         ▼
[Node 9: Validate Structured JSON] (Strict subject, body, summary check)
         │
         ▼
[Node 10: Is AI Response Valid?]
         ├── (Invalid AI) ─► [Node 20: Google Sheets Update (AI Failed)]
         │
         ▼ (Valid AI)
[Node 11: Save Draft in FastAPI] (POST /api/leads/{id}/ai-response)
         │
         ▼
[Node 12 & 13: Check Email Eligibility] (Recipients RFC-5322 check & draft verification)
         │
         ▼
[Node 14: Gmail Dispatcher (Send Email)] (Gmail OAuth2 API)
         │
         ▼
[Node 15: Evaluate Gmail Response] (Classifies Sent vs Failed vs Delivery Unknown)
         │
         ▼
[Node 16: Record Delivery in FastAPI] (POST /api/leads/{id}/record-send)
         │
         ▼
[Node 17: Is Sent Confirmed?]
         ├── (Confirmed) ──► [Node 18: Google Sheets Update (Sent Success)]
         │                   - Email Status: Sent
         │                   - Processing Status: Completed
         │                   - Gmail Message ID recorded
         │
         └── (Rejected) ───► [Node 19: Google Sheets Update (Send Failed)]
                             - Email Status: Failed
                             - Error Message recorded
```

---

## 🛡️ Duplicate-Send Protection & Safety Mechanisms

1. **Pre-Send Eligibility Lock:**
   - Evaluates recipient email syntax, non-empty subject, non-empty body, and verifies `email_status != 'Sent'`.
2. **Idempotency Protection:**
   - Retries with the same `gmail_message_id` return `200 OK (idempotent)`.
   - Repeated attempts to send to an already-contacted lead return `HTTP 409 Conflict`.
3. **Ambiguous Result Isolation (`Delivery Unknown`):**
   - Network or gateway timeouts are marked `Delivery Unknown` and halt automatic retries until manually audited.

---

## 📥 How to Import and Activate the Workflow

1. Start your local n8n instance:
   ```powershell
   $env:GEMINI_API_KEY="your_actual_gemini_api_key_here"
   $env:GEMINI_MODEL="gemini-1.5-flash"
   npx n8n
   ```
2. Open `http://localhost:5678` in your browser.
3. In the left navigation, click **Workflows** → **Add Workflow** → **Import from File**.
4. Select `automation/workflows/lead-capture-workflow.json`.
5. Connect your credentials:
   - **Google Sheets OAuth2 API** on Nodes 1, 18, 19, 20, 21, 22.
   - **Gmail OAuth2 API** on Node 14 (`Gmail Dispatcher`).
6. Click **Save** and toggle the workflow to **Active**.

---

## 📊 Google Sheets Columns & Field Mappings

Ensure your linked Google Form response spreadsheet includes:

| Column Header | Updated By | Description |
|---|---|---|
| `Timestamp` | Google Forms | Form submission timestamp |
| `Full Name` | Google Forms | Contact name |
| `Email Address` | Google Forms | Prospect email |
| `Company / Organization` | Google Forms | Company name |
| `Phone Number` | Google Forms | Contact phone |
| `Service Required` | Google Forms | Inquiry category |
| `Estimated Budget` | Google Forms | Budget tier |
| `Project Scope / Description` | Google Forms | Client scope description |
| `AI Subject` | n8n / Gemini | Personalized email subject line |
| `AI Response` | n8n / Gemini | Consultative outreach email body |
| `Lead Priority` | FastAPI | Deterministic priority (`High`, `Medium`, `Low`) |
| `Processing Status` | n8n | `Completed`, `Failed`, or `Duplicate / Skipped` |
| `Email Status` | n8n | `Sent`, `Draft`, `Failed`, or `Delivery Unknown` |
| `Gmail Message ID` | n8n / Gmail | Confirmed message identifier from Gmail API |
| `Lead ID` | FastAPI | SQLite record identifier |
| `Error Message` | n8n | Error diagnostics on failure or timeout |
| `Processed At` | n8n | ISO execution timestamp |

---

## ⚡ Verification & Testing

Run all 36 automated tests covering the entire system:
```powershell
cd "c:\Users\R\OneDrive\Desktop\Lead Gen Ai\backend"
.\venv\Scripts\python -m pytest -v
```
All 12 Phase 6 Gmail delivery tests pass (100% pass rate).
