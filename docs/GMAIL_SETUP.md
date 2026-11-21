# Gmail Integration & Automated Email Delivery Setup Guide (Phase 6)

## Overview
In **Phase 6**, LeadGen AI completes the end-to-end follow-up cycle by dispatching Gemini-generated personalized outreach emails through **Gmail OAuth2**.

```
[Inbound Lead] ──► [FastAPI / Gemini AI] ──► [Draft Saved] ──► [Eligibility & Duplicate-Send Checks] ──► [Gmail Dispatch] ──► [Status Confirmed: Sent]
```

### Safety & Duplicate-Send Protection Principles
1. **Never Send Without a Valid Draft:**
   - Both `email_subject` and `email_body` must exist and be non-empty strings.
2. **Strict Duplicate-Send Protection:**
   - If an email has already been marked as `Sent`, any re-execution or manual dispatch attempt is rejected with `HTTP 409 Conflict`.
3. **Ambiguous Result Handling (`Delivery Unknown`):**
   - If network latency or a gateway timeout occurs before Gmail acknowledges receipt, the system marks the status as `Delivery Unknown` and halts automated retries until manual review.
4. **No Plaintext Passwords:**
   - Uses OAuth2 scopes (`https://www.googleapis.com/auth/gmail.send`). Access tokens and refresh tokens are never hardcoded or exposed in logs.
5. **No Blind Bulk Outreach:**
   - Outreach messages are individual 1-to-1 follow-ups triggered strictly by valid inbound inquiries.

---

## 1. Google Cloud Console: Gmail OAuth Setup

1. Open [Google Cloud Console](https://console.cloud.google.com/).
2. Select your project (e.g. `leadgen-ai-project`).
3. Enable the **Gmail API**:
   - Navigate to **APIs & Services** → **Library**.
   - Search for **Gmail API** and click **Enable**.
4. Configure the **OAuth Consent Screen**:
   - User Type: **External** (or Internal for Google Workspace domains).
   - App Name: `LeadGen AI CRM`.
   - Add User Support Email and Developer Contact Info.
   - Scopes: Add `https://www.googleapis.com/auth/gmail.send`.
   - Test Users: Add your personal/project owner email address.
5. Create **OAuth 2.0 Credentials**:
   - Go to **APIs & Services** → **Credentials**.
   - Click **Create Credentials** → **OAuth client ID**.
   - Application Type: **Web application**.
   - Name: `LeadGen AI n8n Client`.
   - Authorized Redirect URIs:
     - For local n8n: `http://localhost:5678/rest/oauth2-credential/callback`
   - Click **Create** and safely note your **Client ID** and **Client Secret**.

---

## 2. Configuring Gmail Credentials in n8n

1. Start n8n:
   ```powershell
   npx n8n
   ```
2. Navigate to `http://localhost:5678` in your browser.
3. In the left navigation, click **Credentials** → **Add Credential**.
4. Select **Gmail OAuth2 API**.
5. Fill in:
   - **Client ID**: Your Google Cloud OAuth Client ID.
   - **Client Secret**: Your Google Cloud OAuth Client Secret.
6. Click **Sign in with Google** and approve the `gmail.send` consent screen.
7. Save the credential as `Gmail OAuth Account`.
8. In the workflow (`lead-capture-workflow.json`), open **Node 14: Gmail Dispatcher (Send Email)** and select your saved `Gmail OAuth Account` credential.

---

## 3. Backend Environment Configuration

Update your `.env` (copied from `.env.example`):

```bash
# Gmail Integration
GMAIL_SENDER_ADDRESS=your_verified_sender_email@gmail.com
GMAIL_ACCESS_TOKEN=your_oauth_access_token_here # Optional for direct FastAPI dispatch
```

> **Testing Mode:** If `GMAIL_ACCESS_TOKEN` is left empty or as placeholder, the backend safely simulates successful dispatch with mock message IDs, enabling test suite execution and UI demonstrations without live mail deliveries.

---

## 4. End-to-End Workflow Pipeline

```
1. Google Sheets Trigger
   └─ Reads newly submitted lead row
2. Normalize & Validate Lead Data
   └─ Validates name and RFC-5322 email syntax
3. Check Duplicate in FastAPI
   └─ Avoids re-processing existing leads
4. FastAPI Lead Ingestion
   └─ Stores lead in SQLite and assigns deterministic priority
5. Gemini AI Generation
   └─ Generates personalized subject line, consultative body, and summary
6. Validate Structured JSON
   └─ Confirms non-empty string schema
7. Save Generated Draft in FastAPI
   └─ Persists to EmailRecord with status: 'Draft'
8. Check Email Eligibility
   └─ Validates recipient, draft existence, and verifies lead is not already sent
9. Gmail Dispatcher (Send Email)
   └─ Sends email through authenticated Gmail OAuth
10. Evaluate Gmail Response
   └─ Extracts Gmail message ID; detects failures or ambiguous timeouts
11. Record Delivery in FastAPI (POST /api/leads/{id}/record-send)
   └─ Atomically updates EmailRecord and Lead status
12. Google Sheets Update
   ├─ On Success: Processing Status: Completed, Email Status: Sent, Gmail Message ID
   └─ On Failure: Processing Status: Failed, Email Status: Failed, Error Message
```

---

## 5. Manual Sending & Dashboard Verification

You can also test and trigger follow-up emails directly from the CRM Dashboard:
1. Open the CRM at `http://localhost:5173`.
2. Click on any lead with a generated draft.
3. Review the **Personalized Follow-Up Email Response** preview.
4. Click **Send Follow-Up Email via Gmail**.
5. An explicit confirmation dialog appears:
   > *"Confirm sending email to prospect@example.com via Gmail?"*
6. Click **Confirm & Send**.
7. The button enters a loading state (`Dispatching...`) and locks against multiple clicks.
8. Upon Gmail acceptance:
   - Status badge transitions to **Sent**.
   - The unique **Gmail Message ID** is displayed.
   - The dispatch appears in the **Automated Email History** view.

---

## 6. Troubleshooting Common Issues

| Issue | Cause | Resolution |
|---|---|---|
| **HTTP 409 Conflict** | Lead was already sent an email | Duplicate-send protection in effect. Leads cannot be emailed twice. |
| **HTTP 401 / 403 Unauthorized** | Expired Gmail OAuth token or unapproved scope | Re-authenticate in n8n (Credentials → Gmail OAuth → Reconnect). Ensure `https://www.googleapis.com/auth/gmail.send` is granted. |
| **Delivery Unknown** | Gateway/network timeout while waiting for Gmail response | Inspect lead in CRM; manually reconcile delivery before re-attempting send. |
| **Missing Draft (400 Bad Request)** | Lead has no generated subject/body | Run **Re-run Gemini AI** in the Lead Details modal to produce a draft first. |
| **Invalid Recipient (400 Bad Request)** | Email syntax does not conform to RFC-5322 | Correct the recipient address in the spreadsheet or CRM before sending. |
