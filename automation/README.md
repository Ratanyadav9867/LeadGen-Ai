# LeadGen AI — n8n Lead Capture Automation (Phase 4)

This directory contains the production-ready n8n workflow for **capturing inbound leads from Google Sheets, validating fields, enforcing duplicate prevention, and securely ingesting records into the FastAPI backend**.

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
         ├── (Invalid) ────► [Node 10: Google Sheets Update (Invalid)]
         │
         ▼ (Valid)
[Node 5 & 6: Check Duplicate in FastAPI] (GET /api/leads/check-duplicate?email=...)
         ├── (Duplicate) ──► [Node 9: Google Sheets Update (Duplicate / Skipped)]
         │
         ▼ (New Lead)
[Node 7: FastAPI Ingestion] (POST /api/automation/lead-capture)
         │
         ▼
[Node 8: Google Sheets Update (Success)] (Status: Processing, Lead ID: #)
```

> **Important:** In accordance with Phase 4 specifications, Gemini AI scoring and Gmail outreach will be wired in later phases. **No emails are dispatched in this phase.**

---

## 📥 How to Import the Workflow into n8n

1. Start your local n8n instance:
   ```powershell
   npx n8n
   ```
   Or run via Docker:
   ```powershell
   docker run -it --rm --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n n8nio/n8n
   ```
2. Open your browser at `http://localhost:5678`.
3. In the left navigation, click **Workflows**.
4. Click **Add Workflow** (or the **+** button).
5. In the top-right corner, click the **...** (three dots) menu and select **Import from File**.
6. Select `automation/workflows/lead-capture-workflow.json` from this repository.
7. Click **Save** to persist the workflow.

---

## 🔑 How to Configure Google Sheets Credentials

1. In n8n, click on the **Google Sheets Trigger** node (Node 1).
2. Under **Credential to connect with**, click **Create New Credential**.
3. Choose **Google Sheets OAuth2 API**.
4. Provide your **Client ID** and **Client Secret** (see [docs/GOOGLE_SETUP.md](../docs/GOOGLE_SETUP.md) for how to obtain these from Google Cloud Console).
5. Click **Sign in with Google** and complete the consent flow.
6. The same credential can be selected for **Node 8**, **Node 9**, and **Node 10**.

---

## 📊 Spreadsheet Setup & Required Columns

Link your Google Form to a Google Spreadsheet named **LeadGen AI Inbound Responses**. Ensure your sheet has the following columns:

| Column Header | Type | Purpose |
|---|---|---|
| `Timestamp` | DateTime | Google Form submission time |
| `Full Name` | Text | Required lead contact name |
| `Email Address` | Text | Required lead email (validated RFC 5322) |
| `Company / Organization` | Text | Prospect company or organization name |
| `Phone Number` | Text | Optional contact phone |
| `Service Required` | Text | Category of inquiry |
| `Estimated Budget` | Text | Budget tier |
| `Project Scope / Description` | Text | Inbound inquiry description |
| `Processing Status` | Text | Updated by n8n: `Processing`, `Duplicate / Skipped`, or `Failed / Invalid` |
| `Lead ID` | Integer | Updated by n8n with SQLite database ID |
| `Error Reason` | Text | Populated on validation failure |
| `Processed At` | DateTime | Timestamp of n8n execution |

---

## ⚡ How to Activate & Test the Workflow

### 1. Ensure FastAPI Backend is Running
In PowerShell:
```powershell
cd "C:\Users\R\OneDrive\Desktop\Lead Gen Ai\backend"
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 2. Test Execution in n8n
1. In n8n, click **Test workflow** (bottom bar).
2. Open your Google Form and submit a test entry:
   - **Name**: `Alexander Wright`
   - **Email**: `alex@wrightarch.design`
   - **Company**: `Wright Architecture Lab`
   - **Service**: `AI Workflow Automation`
   - **Budget**: `$15,000 - $30,000`
3. Observe n8n:
   - Node 1 triggers on the new row.
   - Node 2 normalizes the email to lowercase (`alex@wrightarch.design`).
   - Node 3 validates the name and email.
   - Node 5 queries `GET /api/leads/check-duplicate?email=alex@wrightarch.design`.
   - Node 7 posts to `POST /api/automation/lead-capture` and receives `status: "Processing"` and `lead_id`.
   - Node 8 updates the Google Sheet row with `Processing Status = Processing` and `Lead ID`.
4. Open the CRM Dashboard at `http://localhost:5173/leads` to see the captured lead live in SQLite!

### 3. Activate for Continuous Polling
Toggle the workflow switch from **Inactive** to **Active** in the top-right corner of the n8n canvas.

---

## 🛠️ Common Errors & Solutions

| Error | Root Cause | Solution |
|---|---|---|
| `ECONNREFUSED 127.0.0.1:8000` | FastAPI server is not running, or n8n is running in Docker where `127.0.0.1` refers to the container itself. | Start FastAPI with `uvicorn app.main:app`. If running n8n in Docker, use `http://host.docker.internal:8000/api/automation/lead-capture`. |
| `Invalid email address format` | Form respondent submitted a malformed email. | The workflow routes to Node 10 and marks `Processing Status = Failed / Invalid` with the error reason without crashing. |
| `Duplicate / Skipped` | Email already exists in the SQLite database or was submitted previously. | Expected behavior. Prevents duplicate lead records and prevents duplicate spam. |
| `Google Sheets API 403 Forbidden` | OAuth scope missing or expired consent. | Re-authenticate Google Sheets OAuth in n8n with `https://www.googleapis.com/auth/spreadsheets` scope. |
