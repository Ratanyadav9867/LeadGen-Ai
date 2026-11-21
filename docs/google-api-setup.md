# LeadGen AI — Google APIs & Workspace Setup Guide

This guide explains how to connect **Google Forms**, **Google Sheets**, **Google Gemini AI**, and **Gmail** to the LeadGen AI pipeline.

---

## 1. Google Forms & Sheets Response Ingestion

### Step 1: Create the Inbound Google Form
1. Navigate to [Google Forms](https://forms.google.com) and create a new form titled **LeadGen AI Prospect Intake**.
2. Add the following fields:
   - **Full Name** (Short answer, Required)
   - **Company / Organization** (Short answer, Required)
   - **Email Address** (Short answer, Required, Email validation enabled)
   - **Phone Number** (Short answer, Optional)
   - **Service Required** (Dropdown/Multiple choice: `AI Workflow Automation`, `CRM Lead Scoring & Ingestion`, `Automated Client Follow-Ups`, `Google Workspace Integration`)
   - **Estimated Budget** (Dropdown: `$3,000 - $5,000`, `$5,000 - $10,000`, `$15,000 - $30,000`, `$30,000+`)
   - **Project Scope / Description** (Paragraph, Required)

### Step 2: Link Form to Google Sheets
1. In Google Forms, go to the **Responses** tab.
2. Click **Link to Sheets** ➔ Create a new spreadsheet named **LeadGen AI Inbound Responses**.
3. In the generated sheet, add four tracking columns to the header row:
   - Column H: `Status` (Default empty; n8n updates to `Sent` or `Failed`)
   - Column I: `AI Priority` (n8n updates to `High`, `Medium`, `Low`)
   - Column J: `Processed At` (Timestamp of automation execution)
   - Column K: `Email Subject` (Subject line synthesized by Gemini)

---

## 2. Google Gemini API Setup

1. Open [Google AI Studio](https://aistudio.google.com/).
2. Sign in with your Google account.
3. Click **Get API key** in the left navigation sidebar.
4. Click **Create API key** ➔ Select or create a Google Cloud Project.
5. Copy the generated API key (`AIzaSy...`).
6. Paste the key into `backend/.env`:
   ```ini
   GEMINI_API_KEY=AIzaSyYourActualKeyHere
   GEMINI_MODEL=gemini-1.5-flash
   ```

---

## 3. Google Cloud OAuth & Gmail Configuration

To allow n8n to send outreach emails via Gmail:

1. Open [Google Cloud Console](https://console.cloud.google.com/).
2. Create a project named **LeadGen-AI-Automation**.
3. Navigate to **APIs & Services** ➔ **Library**:
   - Enable **Gmail API**.
   - Enable **Google Sheets API**.
   - Enable **Google Drive API**.
4. Go to **APIs & Services** ➔ **OAuth consent screen**:
   - User Type: **External** ➔ Click Create.
   - App name: `LeadGen AI n8n Integration`.
   - User support email: Select your email.
   - Developer contact information: Your email.
   - Scopes: Add `https://mail.google.com/` and `https://www.googleapis.com/auth/spreadsheets`.
   - Test Users: Add the Gmail address you will use for testing.
5. Go to **Credentials** ➔ **Create Credentials** ➔ **OAuth client ID**:
   - Application type: **Web application**.
   - Name: `n8n OAuth Client`.
   - Authorized redirect URIs: Enter the redirect URI provided by your n8n instance (e.g. `https://your-n8n.app/rest/oauth2-credential/callback` or `http://localhost:5678/rest/oauth2-credential/callback`).
6. Copy the **Client ID** and **Client Secret** into your n8n Gmail and Google Sheets credentials.

