# LeadGen AI — Three-Minute Assessment Video Script

> **Purpose:** Script for recording a concise, high-impact 3-minute video demonstration of the LeadGen AI project for internship evaluation.

---

## ⏱️ Video Timeline Breakdown

| Timestamp | Section | Visual Scene | Spoken Narration |
|---|---|---|---|
| **0:00 - 0:30** | Introduction & Problem Statement | Camera on presenter / Title slide showing LeadGen AI architecture diagram | "Hello! Today I'm excited to present **LeadGen AI**, an autonomous lead management and follow-up CRM developed for the AI Automation Internship assessment. Traditional lead intake suffers from delayed response times and manual qualification bottlenecks. LeadGen AI bridges Google Forms, Google Sheets, and Gmail through n8n orchestration and Google Gemini AI, ensuring every prospect receives an intelligent, personalized follow-up in under two minutes." |
| **0:30 - 1:10** | End-to-End Automation Pipeline | Screen share of Google Form and n8n Workflow Editor | "Here is our complete automation flow. An inbound prospect fills out our Google Form specifying their service needs and budget. As soon as the response is appended to Google Sheets, our n8n pipeline triggers. It validates the contact info, checks for duplicates, and forwards the payload to our FastAPI backend. Google Gemini evaluates the scope, determines commercial priority—High, Medium, or Low—and crafts a customized business email. The email is automatically dispatched via Gmail, and the spreadsheet is updated with the delivery status and timestamp." |
| **1:10 - 2:00** | Live CRM Dashboard & Lead Inspection | Screen share of React CRM Dashboard (`http://localhost:5173`) | "Now let's explore our CRM dashboard. Built with React, Vite, TypeScript, and Tailwind CSS, it offers an executive view of our pipeline. We see live metrics: Total Leads, New Leads, Contacted Leads, and High Priority inquiries. In the Lead Management table, we can search, filter by priority tier, or sort by date. When we inspect a lead, we see full contact details, project scope, Gemini's qualification reasoning, and the exact email draft." |
| **2:00 - 2:35** | Interactive Testing & Webhook Simulator | Screen share of Automation page ➔ Webhook Simulator | "On our Automation page, we have a live Pipeline Ingestion Tester. Let's trigger a test lead right now for Elena at Mystic Tech. When we click 'Trigger Test Inbound Webhook', it posts directly to our FastAPI endpoint. Instantly, we see the lead qualified as High Priority due to its $15K enterprise budget, and Gemini generates a bespoke response. If we navigate back to our Overview, our metrics and recent lead table update in real time." |
| **2:35 - 3:00** | Architecture, Security & Conclusion | Screen share showing VS Code tests passing (`pytest -v`) and Settings page | "Under the hood, LeadGen AI uses a FastAPI backend with SQLite persistence, strictly enforcing zero-client secrets by isolating API keys on the server. Our test suite verifies 100% of our health, deduplication, and qualification endpoints. Thank you for watching, and I look forward to taking this automation architecture to the next level!" |

---

## 💡 Presenter Tips

1. **Resolution**: Record at 1080p (1920x1080) at 60fps.
2. **Audio**: Use a dedicated microphone with low background noise.
3. **Pacing**: Speak at an energetic, conversational, professional pace.
4. **Browser**: Have both `http://localhost:5173` and `http://127.0.0.1:8000/docs` pre-opened in Chrome tabs before starting.
