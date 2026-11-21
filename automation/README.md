# LeadGen AI — n8n Lead Capture & Gemini AI Automation (Phase 5)

This directory contains the production-ready n8n workflow for **capturing inbound leads from Google Sheets, validating fields, enforcing duplicate prevention, generating personalized email drafts via Google Gemini AI, and updating Google Sheets with Draft / Not Sent status**.

Workflow file: `automation/workflows/lead-capture-workflow.json`

---

## 🏗️ Architecture

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
         ├── (Invalid) ────► [Node 15: Google Sheets Update (Invalid)]
         │
         ▼ (Valid)
[Node 5 & 6: Check Duplicate in FastAPI] (GET /api/leads/check-duplicate?email=...)
         ├── (Duplicate) ──► [Node 14: Google Sheets Update (Duplicate / Skipped)]
         │
         ▼ (New Lead)
[Node 7: FastAPI Ingestion] (POST /api/automation/lead-capture)
         │
         ▼
[Node 8: Gemini AI Generation] (POST https://generativelanguage.googleapis.com/...:generateContent)
         │
         ▼
[Node 9: Validate Structured JSON] (Strict subject, body, summary string check)
         │
         ▼
[Node 10: Is AI Response Valid?]
         ├── (Valid AI) ───► [Node 11: Save Draft in FastAPI] (POST /api/leads/{id}/ai-response)
         │                          │
         │                          ▼
         │                   [Node 12: Google Sheets Update (Success)]
         │                   - Status: Completed
         │                   - Email Status: Draft / Not Sent
         │                   - AI Subject & AI Response
         │
         └── (Invalid AI) ─► [Node 13: Google Sheets Update (AI Failed)]
                             - Status: Failed
                             - Email Status: Failed / Not Sent
                             - Error Reason logged
```

> **Important:** In accordance with Phase 5 specifications, generated emails remain in **Draft / Not Sent** status. **No emails are transmitted in this phase.** Gmail delivery is strictly scheduled for Phase 6.

---

## 📥 How to Import the Workflow into n8n

1. Start your local n8n instance:
   ```powershell
   $env:GEMINI_API_KEY="your_actual_gemini_api_key_here"
   $env:GEMINI_MODEL="gemini-1.5-flash"
   npx n8n
   ```
2. Open your browser at `http://localhost:5678`.
3. In the left navigation, click **Workflows**.
4. Click **Add Workflow** (or the **+** button).
5. In the top-right corner, click the **...** (three dots) menu and select **Import from File**.
6. Select `automation/workflows/lead-capture-workflow.json` from this repository.
7. Click **Save** to persist the workflow.

---

## 🔑 Credentials Configuration

### 1. Google Sheets OAuth2 API
- Configured on **Google Sheets Trigger** (Node 1) and all update nodes (Nodes 12, 13, 14, 15).
- Follow instructions in [docs/google-api-setup.md](../docs/google-api-setup.md).

### 2. Google Gemini API
- Configured via environment variable `GEMINI_API_KEY` (and `GEMINI_MODEL`) in n8n or via HTTP Header Auth.
- See detailed guide: [docs/GEMINI_SETUP.md](../docs/GEMINI_SETUP.md).

---

## 📊 Spreadsheet Setup & Required Columns

| Column Header | Type | Purpose | Updated By |
|---|---|---|---|
| `Timestamp` | DateTime | Google Form submission time | Google Forms |
| `Full Name` | Text | Required lead contact name | Google Forms |
| `Email Address` | Text | Required lead email (validated RFC 5322) | Google Forms |
| `Company / Organization` | Text | Prospect company or organization name | Google Forms |
| `Phone Number` | Text | Optional contact phone | Google Forms |
| `Service Required` | Text | Category of inquiry | Google Forms |
| `Estimated Budget` | Text | Budget tier | Google Forms |
| `Project Scope / Description` | Text | Inbound inquiry description | Google Forms |
| `AI Subject` | Text | Generated email subject line | n8n / Gemini |
| `AI Response` | Text | Generated personalized email body | n8n / Gemini |
| `Lead Priority` | Text | Deterministic priority (`High`, `Medium`, `Low`) | FastAPI |
| `Processing Status` | Text | `Completed`, `Failed`, or `Duplicate / Skipped` | n8n |
| `Email Status` | Text | `Draft / Not Sent` | n8n |
| `Lead ID` | Integer | SQLite database record ID | FastAPI |
| `Error Reason` | Text | Populated on validation or AI generation failure | n8n |
| `Processed At` | DateTime | ISO timestamp of pipeline execution | n8n |

---

## ⚡ Verification & Testing

Verify end-to-end functionality using the automated test suite:
```powershell
cd "c:\Users\R\OneDrive\Desktop\Lead Gen Ai\backend"
.\venv\Scripts\python -m pytest tests/test_gemini_integration.py -v
```
All 11 test cases pass, validating prompt engineering, untrusted input protection, error fallback, rate limit retry, idempotency, draft persistence, and non-transmission during Phase 5.
