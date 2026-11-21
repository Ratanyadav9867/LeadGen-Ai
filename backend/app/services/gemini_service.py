import json
import logging
import httpx
from typing import Dict, Any, Optional
from app.config import settings

logger = logging.getLogger("gemini_service")

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

SYSTEM_PROMPT = """You are LeadGen AI's Senior B2B Sales Engineer and Client Intake Specialist.
Your task is to analyze an inbound business lead, qualify its commercial priority, and compose a personalized, professional business follow-up email.

STRICT BUSINESS RULES:
1. Understand the customer's specific service needs, timeline, and budget.
2. Assign a Priority tier: 'High', 'Medium', or 'Low'.
   - High Priority: Enterprise budget ($10,000+), urgent implementation timeframe, or mission-critical workflows.
   - Medium Priority: Mid-market budget ($5,000 - $10,000) or standard scope inquiries.
   - Low Priority: Smaller budget (<$5,000), exploratory/unclear requirements, or casual questions.
3. Provide a clear, objective 'priority_reason' explaining the classification.
4. Craft a tailored, compelling 'email_subject' line.
5. Compose a professional, consultative 'email_body'.
   - Address the prospect by their name.
   - Acknowledge their company and specific project requirements directly.
   - Propose a clear, low-friction next step (e.g. 15-minute discovery consultation).
   - NEVER invent specific fixed pricing, contractual guarantees, or false company capabilities.
6. Return ONLY a valid JSON object matching the requested schema. No markdown formatting outside JSON.

JSON OUTPUT SCHEMA:
{
  "priority": "High" | "Medium" | "Low",
  "priority_reason": "string",
  "email_subject": "string",
  "email_body": "string",
  "key_requirements": ["string"]
}
"""


def _generate_fallback_analysis(lead_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deterministic rule-based fallback when GEMINI_API_KEY is not configured.
    Provides professional, tailored qualification without breaking offline operation.
    """
    budget_raw = str(lead_data.get("budget", "")).lower()
    desc = str(lead_data.get("description", "")).lower()
    service = lead_data.get("service", "Automation Solutions")
    name = lead_data.get("name", "Valued Client")
    company = lead_data.get("company", "Your Organization")

    # Priority determination rules
    if "25,000" in budget_raw or "10,000" in budget_raw or "urgent" in desc or "enterprise" in desc:
        priority = "High"
        reason = f"High-tier investment allocation ({lead_data.get('budget')}) and critical implementation scope for {company}."
    elif "5,000" in budget_raw or "medium" in desc:
        priority = "Medium"
        reason = f"Mid-tier investment scope ({lead_data.get('budget')}) with standard consultative requirements."
    else:
        priority = "Low"
        reason = f"Entry-level budget tier ({lead_data.get('budget')}) or early-stage exploratory inquiry."

    email_subject = f"Optimizing {company}'s {service} Pipeline | LeadGen AI"
    email_body = (
        f"Dear {name},\n\n"
        f"Thank you for contacting LeadGen AI regarding your upcoming {service} initiative for {company}.\n\n"
        f"We have thoroughly reviewed your project scope: \"{lead_data.get('description', 'Client workflow optimization')}\". "
        f"Our AI and workflow automation frameworks are built specifically to handle multi-stage data intake, "
        f"qualification, and rapid customer response sequences while preserving data integrity.\n\n"
        f"Based on your requirements, we would welcome the opportunity to review an architecture outline tailored "
        f"to {company}. Would you be available for a brief 15-minute discovery conversation this week?\n\n"
        f"Best regards,\n"
        f"The LeadGen AI Architecture Team\n"
        f"Intelligent Lead Management & Automation"
    )

    return {
        "priority": priority,
        "priority_reason": reason,
        "email_subject": email_subject,
        "email_body": email_body,
        "key_requirements": [service, f"Budget: {lead_data.get('budget')}"],
        "source": "rule_based_fallback"
    }


async def analyze_and_draft_lead(lead_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes an inbound lead using Google Gemini API.
    Falls back gracefully to rule-based qualification if API key is missing or request fails.
    """
    api_key = settings.GEMINI_API_KEY.strip()

    if not api_key or api_key == "your_gemini_api_key_here":
        logger.info("GEMINI_API_KEY not configured. Utilizing deterministic qualification engine.")
        return _generate_fallback_analysis(lead_data)

    prompt_content = f"""
Prospect Inbound Data:
- Lead Name: {lead_data.get('name')}
- Company: {lead_data.get('company')}
- Email: {lead_data.get('email')}
- Phone: {lead_data.get('phone', 'N/A')}
- Service Requested: {lead_data.get('service')}
- Budget Allocation: {lead_data.get('budget')}
- Project Scope & Description: {lead_data.get('description')}

Evaluate this lead according to the instructions and return the structured JSON output.
"""

    url = GEMINI_API_URL.format(model=settings.GEMINI_MODEL) + f"?key={api_key}"

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": SYSTEM_PROMPT},
                    {"text": prompt_content}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json"
        }
    }

    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            response = await client.post(url, json=payload)

            if response.status_code == 200:
                data = response.json()
                text_response = data["candidates"][0]["content"]["parts"][0]["text"]
                parsed = json.loads(text_response)
                parsed["source"] = f"gemini_{settings.GEMINI_MODEL}"
                return parsed
            else:
                logger.warning(f"Gemini API returned status {response.status_code}: {response.text}")
                fallback = _generate_fallback_analysis(lead_data)
                fallback["error"] = f"Gemini API error ({response.status_code})"
                return fallback

    except Exception as exc:
        logger.error(f"Error calling Gemini API: {exc}")
        fallback = _generate_fallback_analysis(lead_data)
        fallback["error"] = str(exc)
        return fallback
