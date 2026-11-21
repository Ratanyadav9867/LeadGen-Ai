# Google Gemini AI Integration & Setup Guide (Phase 5)

## Overview
In **Phase 5**, LeadGen AI integrates Google Gemini to analyze inbound customer requirements and generate tailored, high-converting follow-up email drafts. 

### Key Architectural Tenets
1. **Separation of Concerns:** 
   - Authoritative lead priority (`High`, `Medium`, `Low`) is computed **deterministically in FastAPI** based on objective commercial rules (budget and scope).
   - Gemini is focused strictly on consultative synthesis: generating a personalized **subject line**, structured **email body**, and a concise **requirement summary**.
2. **Untrusted Input Protection:**
   - The prospective lead's project description is treated as untrusted user input.
   - Guardrails prevent role overrides, system instruction leaks, or prompt injections.
3. **Strict Structured Output:**
   - Gemini returns validated JSON (`subject`, `body`, `summary`).
   - Empty fields or malformed JSON are rejected before reaching the database.
4. **Draft-Only Status (No Outbound Dispatches):**
   - Generated outreach records are stored with `status = "Draft"` / `email_status = "Draft"`.
   - **No emails are transmitted in Phase 5.** Gmail integration is strictly reserved for Phase 6.

---

## 1. Obtaining a Google Gemini API Key

1. Navigate to [Google AI Studio](https://aistudio.google.com/).
2. Sign in with your Google account.
3. Click **Get API key** from the left navigation panel.
4. Click **Create API key** (create in a new or existing Google Cloud project).
5. Copy your generated API key.
   > **Security Warning:** Never commit your actual API key to version control or share it in issue reports.

---

## 2. Secure Configuration in LeadGen AI

### Backend (`backend/.env` and root `.env`)
Add your key and desired model to your local `.env` file (copied from `.env.example`):

```bash
# Google Gemini AI Configuration
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash
```

Supported model configurations include:
- `gemini-1.5-flash` (recommended for low latency and high reliability)
- `gemini-1.5-pro` (for deep context analysis)

### Offline Fallback Mode
If `GEMINI_API_KEY` is omitted or left as the placeholder `your_gemini_api_key_here`, LeadGen AI automatically switches to **deterministic BDR fallback mode**. This allows the entire pipeline, test suite, and local CRM UI to function cleanly without an internet connection or external API billing.

---

## 3. Configuring Gemini in n8n

The n8n workflow (`automation/workflows/lead-capture-workflow.json`) supports two authentication methods for Gemini:

### Method A: Environment Variables (Recommended)
When launching n8n, pass the environment variables:
```powershell
$env:GEMINI_API_KEY="your_actual_gemini_api_key_here"
$env:GEMINI_MODEL="gemini-1.5-flash"
npx n8n
```

### Method B: n8n Header Auth or Generic Credential
1. Open n8n at `http://localhost:5678`.
2. Go to **Credentials** → **New Credential** → **Header Auth** (or **Google Gemini / PaLM** if installed).
3. Name the credential `Gemini API Key`.
4. In **Gemini AI Generation** (Node 8), bind the credential to the query parameter `key`.

---

## 4. Pipeline Execution Sequence

```
1. Google Sheets Trigger
   └─ Triggers on new row appended via Google Form
2. Normalize Lead Data
   └─ Trims whitespace, lowercases email, preserves spreadsheet row #
3. Validate Lead
   └─ Validates RFC-5322 email & prospect name
4. Duplicate Check (FastAPI)
   └─ GET /api/leads/check-duplicate?email=...
5. FastAPI Ingestion
   └─ POST /api/automation/lead-capture (Stores lead & assigns deterministic priority)
6. Gemini AI Generation
   └─ POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent
7. Validate Structured JSON
   └─ Strict validation of subject, body, and summary
8. Save Generated Draft (FastAPI)
   └─ POST /api/leads/{id}/ai-response (Saves EmailRecord in Draft status)
9. Google Sheets Update (Success)
   └─ Writes AI Subject, AI Response, Lead Priority, Processing Status: Completed, Email Status: Draft / Not Sent
```

---

## 5. Testing Generated Emails

### Automated Testing (Pytest)
Run the automated test suite covering all 11 Phase 5 test criteria:
```powershell
cd "c:\Users\R\OneDrive\Desktop\Lead Gen Ai\backend"
.\venv\Scripts\python -m pytest tests/test_gemini_integration.py -v
```

### CRM Dashboard UI Inspection
1. Start the backend:
   ```powershell
   cd "c:\Users\R\OneDrive\Desktop\Lead Gen Ai\backend"
   .\venv\Scripts\Activate.ps1
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```
2. Start the frontend:
   ```powershell
   cd "c:\Users\R\OneDrive\Desktop\Lead Gen Ai\frontend"
   npm run dev
   ```
3. Open `http://localhost:5173` in your browser.
4. Click on any lead to open the **Lead Inspection & AI Qualification** modal.
5. Review the **Google Gemini AI Lead Scoring Analysis** and **Personalized Follow-Up Email Response** preview.
6. Click **Re-run Gemini AI** to test on-demand live generation via `POST /api/leads/{id}/generate-ai`.

---

## 6. Troubleshooting Common Issues

| Issue | Cause | Solution |
|---|---|---|
| **HTTP 429: Resource Exhausted** | Gemini API quota limit reached | The backend automatically backs off with exponential delay. Upgrade your quota tier or switch model to `gemini-1.5-flash`. |
| **HTTP 400: API Key Invalid** | Incorrect or expired API key | Verify key in [Google AI Studio](https://aistudio.google.com/app/apikey) and update `.env`. |
| **Connection Timeout** | Network latency to Google endpoints | The backend retries up to 2 times with a 15-second timeout, then smoothly engages the deterministic BDR fallback. |
| **Malformed JSON Response** | AI returned markdown or conversational text | Handled by `responseMimeType: "application/json"` and validated by `validate_ai_response()`. Malformed outputs are safely rejected. |
| **HTTP 409 Conflict on Save** | Lead outreach has already been marked `Sent` | Designed safeguard: LeadGen AI forbids overwriting emails that have already been transmitted to customers. |
