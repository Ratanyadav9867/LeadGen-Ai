# n8n Automation Engine — LeadGen AI Pipeline

This directory provides the end-to-end workflow automation linking **Google Forms**, **Google Sheets**, **LeadGen AI (FastAPI + SQLite)**, **Google Gemini AI**, and **Gmail**.

---

## 🔄 Workflow Diagram

```
[Google Form Submission]
         │
         ▼
[Google Sheets Response Row Appended]
         │
         ▼
[n8n: Google Sheets Trigger] ── (Polls new rows)
         │
         ▼
[n8n: Validate Lead & Check Duplicates]
         │
    ┌────┴────────────────────────┐
    │ (Valid & Not Duplicate)     │ (Invalid / Already Sent)
    ▼                             ▼
[LeadGen AI Webhook]        [Update Sheets: Status = Failed / Skip]
(Gemini AI Scoring)
         │
         ▼
[n8n: Validate AI Response]
         │
         ▼
[n8n: Gmail Send Email] ── (Dispatches personalized follow-up)
         │
         ▼
[n8n: Update Sheets: Status = Sent, AI Priority, Timestamp]
```

---

## 📦 Import Instructions for n8n

1. Launch your local or cloud n8n instance (e.g. `npx n8n` or Docker).
2. Go to **Workflows** ➔ Click **Add Workflow**.
3. Click the three dots menu (**...**) in the top right corner ➔ Select **Import from File**.
4. Choose `automation/n8n_leadgen_workflow.json`.
5. The workflow will render with the 8 configured stages.

---

## 🔑 Credential Configuration (Do Not Invent Credentials)

In accordance with strict application guidelines, no fake or mock credential IDs are hardcoded in the JSON file. You must attach your legitimate accounts:

1. **Google Sheets OAuth2 API**:
   - In the `Google Sheets Trigger` and `Update Sheets` nodes, select **Create New Credential** ➔ Authenticate with Google Workspace.
   - Select your Form Responses spreadsheet from the picker.
2. **Gmail OAuth2 API**:
   - In the `Gmail Send Email` node, select **Create New Credential** ➔ Connect your Google account with `https://mail.google.com/` scope.
3. **LeadGen AI Webhook**:
   - The `LeadGen AI / Gemini Processing` HTTP Request node targets `http://127.0.0.1:8000/api/automation/webhook`.
   - If running n8n inside Docker, use `http://host.docker.internal:8000/api/automation/webhook`.

---

## 🛡️ Reliability & Safety Features

- **Duplicate Prevention**: The code node inspects the existing `Status` column. If marked as `Sent` or `Processing`, the lead is not re-contacted.
- **Email Validation**: RFC 5322 regex checks verify valid email structure before dispatching.
- **AI Response Validation**: Ensures `email_subject` and `email_body` are non-empty before invoking Gmail.
- **Error Logging**: Incomplete or failing records update Google Sheets with a `Failed / Invalid` tag for manual review.
