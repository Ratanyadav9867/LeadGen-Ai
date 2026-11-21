# Google Workspace & Cloud OAuth Setup Guide

This guide provides instructions for configuring **Google Forms**, **Google Sheets**, and **Google Cloud OAuth 2.0 Credentials** for use with n8n and the LeadGen AI automation pipeline.

---

## 1. Create the Google Form

1. Go to [Google Forms](https://forms.google.com/) and create a new blank form.
2. Form Title: `LeadGen AI — Inbound Client Inquiry`
3. Add the following questions in order:
   - **Full Name** (Short answer, Required)
   - **Email Address** (Short answer, Required, Enable response validation: Text ➔ Email)
   - **Company / Organization** (Short answer, Required)
   - **Phone Number** (Short answer, Optional)
   - **Service Required** (Dropdown/Multiple choice, Required):
     - `AI Workflow Automation`
     - `CRM Lead Scoring & Ingestion`
     - `Automated Client Follow-Ups`
     - `Google Workspace Integration`
   - **Estimated Budget** (Dropdown, Required):
     - `$3,000 - $5,000`
     - `$5,000 - $10,000`
     - `$15,000 - $30,000`
     - `$30,000+`
   - **Project Scope / Description** (Paragraph, Optional)

---

## 2. Link Form Responses to Google Sheets

1. In your Google Form, click the **Responses** tab.
2. Click **Link to Sheets** (the green Sheets icon).
3. Select **Create a new spreadsheet** named `LeadGen AI Inbound Responses`.
4. Click **Create**.
5. Once the spreadsheet opens in a new tab:
   - Note the **Spreadsheet ID** from the URL:
     `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID_HERE/edit`
   - Note the sheet name at the bottom tab (usually `Form Responses 1`).
6. Append the following column headers to row 1 starting in Column I:
   - Column I: `Processing Status`
   - Column J: `Lead ID`
   - Column K: `Error Reason`
   - Column L: `Processed At`

---

## 3. Configure Google Cloud OAuth Credentials for n8n

To allow n8n to read new rows and update processing statuses securely:

### Step 1: Create a Google Cloud Project
1. Open the [Google Cloud Console](https://console.cloud.google.com/).
2. Click **Select a project** ➔ **New Project**.
3. Name: `LeadGen-AI-Automation` ➔ Click **Create**.

### Step 2: Enable Google Sheets & Drive APIs
1. Navigate to **APIs & Services** ➔ **Library**.
2. Search for and enable:
   - **Google Sheets API**
   - **Google Drive API**

### Step 3: Configure OAuth Consent Screen
1. Go to **APIs & Services** ➔ **OAuth consent screen**.
2. Select **External** ➔ Click **Create**.
3. App name: `LeadGen AI n8n Integration`.
4. User support email: Select your account.
5. Developer contact information: Enter your email address.
6. Scopes:
   - Add `https://www.googleapis.com/auth/spreadsheets`
   - Add `https://www.googleapis.com/auth/drive.readonly`
7. Test Users: Add your Google account email.
8. Click **Save and Continue**.

### Step 4: Create OAuth 2.0 Client ID
1. Navigate to **APIs & Services** ➔ **Credentials**.
2. Click **Create Credentials** ➔ **OAuth client ID**.
3. Application type: **Web application**.
4. Name: `n8n OAuth Credential`.
5. **Authorized redirect URIs**:
   - If running n8n locally: `http://localhost:5678/rest/oauth2-credential/callback`
   - If running on a domain: `https://your-n8n-domain/rest/oauth2-credential/callback`
6. Click **Create**.
7. Copy the **Client ID** and **Client Secret**.

---

## 4. Link Credentials Inside n8n

1. In n8n, go to **Credentials** ➔ **Add Credential**.
2. Search for **Google Sheets OAuth2 API**.
3. Paste the **Client ID** and **Client Secret**.
4. Click **Connect my account** (or **Sign in with Google**).
5. Grant permissions to view and edit Google Spreadsheets.
6. Once connected, open `automation/workflows/lead-capture-workflow.json` in n8n.
7. Set your credential on the **Google Sheets Trigger** node and the update nodes.
8. Enter your Spreadsheet ID and select `Form Responses 1`.

