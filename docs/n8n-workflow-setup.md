# LeadGen AI — n8n Workflow Setup Guide

This guide details how to import, configure, and activate the complete automation pipeline inside **n8n**.

---

## 🚀 Step 1: Start n8n

You can run n8n locally via npm or Docker:

```powershell
# Quick local run with npx
npx n8n
```
Or with Docker:
```powershell
docker run -it --rm --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n n8nio/n8n
```
Access the n8n web editor at: `http://localhost:5678`

---

## 📥 Step 2: Import Workflow JSON

1. In n8n, navigate to **Workflows**.
2. Click the top-right menu icon (**...**) ➔ Click **Import from File**.
3. Select `automation/n8n_leadgen_workflow.json` from this project directory.
4. The workflow will appear on your canvas with all 8 interconnected nodes.

---

## ⚙️ Step 3: Configure Nodes & Credentials

### 1. Google Sheets Trigger
- **Credential**: Connect your Google Sheets OAuth credential.
- **Document**: Select the Google Sheet created in the Google API Setup Guide.
- **Sheet**: `Form Responses 1`.
- **Trigger**: New row added.

### 2. Validate Lead & Check Duplicates (Code Node)
- Validates that `Name` and a RFC-5322 compliant `Email` exist.
- Checks if `Status` is already set to `Sent` or `Processing` to guarantee duplicate prevention.

### 3. LeadGen AI / Gemini Processing (HTTP Request Node)
- **URL**: `http://127.0.0.1:8000/api/automation/webhook` (or `http://host.docker.internal:8000/api/automation/webhook` if n8n runs in Docker).
- **Method**: `POST`.
- Sends the sanitized prospect JSON.
- Receives the evaluated priority, priority explanation, and generated email response.

### 4. Gmail Send Email (Gmail Node)
- **Credential**: Connect your Gmail OAuth credential.
- **To**: `={{ $json.email }}`.
- **Subject**: `={{ $json.email_subject }}`.
- **Message**: `={{ $json.email_body }}`.

### 5. Update Sheets - Success Log (Google Sheets Node)
- **Operation**: Update row.
- **Columns Updated**:
  - `Status`: `Sent`
  - `AI Priority`: `={{ $json.priority }}`
  - `Processed At`: `={{ $now.toISO() }}`
  - `Email Subject`: `={{ $json.email_subject }}`

---

## 🧪 Step 4: Testing the Workflow

1. Click **Test Workflow** in n8n.
2. Submit a new response via your Google Form or append a row in Google Sheets.
3. Observe n8n:
   - Green checks will light up sequentially across Trigger ➔ Validation ➔ Gemini ➔ Gmail ➔ Sheets.
   - The prospect will receive a personalized email in their inbox within seconds.
   - The CRM dashboard at `http://localhost:5173/leads` will immediately reflect the new lead.

