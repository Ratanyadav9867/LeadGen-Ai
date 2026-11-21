# LeadGen AI — Testing & Verification Guide

This guide details how to verify every layer of the LeadGen AI system, from automated unit test suites to end-to-end webhook simulation.

---

## 🧪 1. Backend Automated Test Suite (Pytest)

The backend includes comprehensive test coverage for health, lead ingestion, Gemini AI scoring, status transitions, webhook deduplication, and integration checks.

```powershell
cd backend
.\venv\Scripts\Activate.ps1
pytest -v
```

### Expected Output:
```text
tests/test_health.py::test_root_endpoint PASSED                          [ 12%]
tests/test_health.py::test_health_endpoint PASSED                        [ 25%]
tests/test_leads.py::test_create_and_get_leads PASSED                    [ 37%]
tests/test_leads.py::test_ai_generation_endpoint PASSED                  [ 50%]
tests/test_leads.py::test_lead_status_update PASSED                      [ 62%]
tests/test_leads.py::test_automation_webhook_and_deduplication PASSED    [ 75%]
tests/test_leads.py::test_integrations_status PASSED                     [ 87%]
tests/test_leads.py::test_email_history PASSED                           [100%]
======================== 8 passed in ~1.5s =========================
```

---

## ⚛️ 2. Frontend Build Verification (TypeScript & Vite)

Verify that the frontend builds cleanly with zero TypeScript errors or broken imports:

```powershell
cd frontend
npm run build
```

### Expected Output:
```text
✓ 2151 modules transformed.
dist/index.html                   0.45 kB
dist/assets/index-C0FSxp2T.css   35.94 kB
dist/assets/index-DiahdUk0.js   349.82 kB
✓ built in ~1.4s
```

---

## 🔄 3. Live Server & Endpoint Verification

Run the automated live health check script:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\verify_health_live.ps1
```

### Manual Live Endpoint Verification:

```powershell
# 1. Health check
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/health"

# 2. Lead statistics
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/leads/stats"

# 3. Integration credentials status
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/integrations/status"

# 4. Trigger test webhook
$body = @{
    name = "Test Lead"
    company = "Testing Corp"
    email = "test@example.com"
    service = "AI Workflow Automation"
    budget = "$15,000 - $30,000"
    description = "Test inquiry"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/automation/webhook" -Method Post -Body $body -ContentType "application/json"
```

---

## 🖥️ 4. CRM Dashboard Interactive UI Testing

1. Open `http://localhost:5173` in your browser.
2. **Overview Page**:
   - Verify KPI cards (Total Leads, New Leads, Contacted Leads, High Priority Leads, Failed Email Count).
   - Check the live latency and Backend Connected pill in the header.
3. **All Leads & High Priority**:
   - Type in the search box to filter by company or name.
   - Click "View Details" to open the Lead Inspection & AI Qualification modal.
   - Click "Re-run Gemini AI" to observe real-time AI scoring updates.
   - Click "Mark Status" (Sent / Pending / Failed) to test live status mutations.
4. **Automation Page**:
   - Scroll to the "Pipeline Ingestion & AI Qualification Tester".
   - Click "Trigger Test Inbound Webhook" and observe the live qualification response rendered instantly.
