"""
AI Insights Module
- Portfolio insights + rebalancing advice: Google Gemini Flash (Free)
- Live chat: Groq Llama 3.3 (Free)
"""
import os
import logging
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────
# GEMINI FLASH — Portfolio Analysis & Insights
# ─────────────────────────────────────────────────────
def generate_portfolio_insights(portfolio_analysis: Dict) -> Dict:
    """
    Use Gemini Flash to generate personalized portfolio insights
    and rebalancing recommendations.
    """
    try:
        import google.generativeai as genai

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY not set, using fallback insights")
            return _fallback_insights(portfolio_analysis)

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = _build_insights_prompt(portfolio_analysis)
        response = model.generate_content(prompt)
        text = response.text

        # Parse structured sections from response
        return {
            "summary": _extract_section(text, "SUMMARY", 300),
            "key_findings": _extract_section(text, "KEY FINDINGS", 400),
            "rebalancing": _extract_section(text, "REBALANCING", 400),
            "action_items": _extract_action_items(text),
            "raw": text,
            "model": "gemini-1.5-flash",
        }

    except Exception as e:
        logger.error(f"Gemini insights failed: {e}")
        return _fallback_insights(portfolio_analysis)


def _build_insights_prompt(analysis: Dict) -> str:
    xirr = analysis.get("xirr", 0)
    apparent = analysis.get("apparent_return", 0)
    total_value = analysis.get("total_value", 0)
    num_funds = analysis.get("num_funds", 0)
    unique_stocks = analysis.get("overlap", {}).get("unique_stocks", 0)
    expense_drain = analysis.get("expense", {}).get("total_drain_over_horizon", 0)
    tax_saving = analysis.get("tax", {}).get("total_tax_saving", 0)
    goal_prob = analysis.get("goal", {}).get("probability", 0)
    goal_prob_opt = analysis.get("goal", {}).get("probability_optimized", 0)
    investor_name = analysis.get("investor", {}).get("name", "the investor")
    num_regular = analysis.get("expense", {}).get("num_regular_plans", 0)

    return f"""You are a senior Indian mutual fund advisor. Analyze this portfolio and provide insights.

PORTFOLIO DATA:
- Investor: {investor_name}
- Total Portfolio Value: ₹{total_value:,.0f}
- True XIRR (actual returns): {xirr:.1f}%
- App-Shown Returns (inflated): {apparent:.1f}%
- Return Gap: {apparent - xirr:.1f}%
- Number of Funds: {num_funds}
- Unique Stocks Across All Funds: {unique_stocks}
- Regular Plans (paying commission): {num_regular}
- 10-Year Expense Drain (Regular vs Direct): ₹{expense_drain:,.0f}
- Tax Harvesting Opportunity: ₹{tax_saving:,.0f}
- Goal Achievement Probability (current): {goal_prob:.0f}%
- Goal Probability After Rebalancing: {goal_prob_opt:.0f}%

Respond in exactly this format:

SUMMARY:
[2-3 sentences, direct and honest assessment of the portfolio health. Use Indian financial context. No fluff.]

KEY FINDINGS:
[3 bullet points, each starting with an emoji. Focus on the most impactful issues: XIRR gap, diversification illusion, or expense drain. Be specific with numbers.]

REBALANCING:
[2-3 specific, actionable rebalancing steps. Mention moving from liquid/debt to equity if goal probability is below 95%. Suggest direct plan switch if on regular plans.]

ACTION ITEMS:
1. [Most urgent action with estimated impact in rupees]
2. [Second priority action]
3. [Third priority action]

Keep the tone conversational, direct, and helpful. Do not give generic financial advice. Use rupee symbols. Be honest about problems."""


def _extract_section(text: str, section: str, max_chars: int) -> str:
    """Extract a named section from the AI response."""
    try:
        start = text.upper().find(section + ":")
        if start == -1:
            return ""
        start = text.find(":", start) + 1
        # Find next section
        next_section = -1
        for kw in ["SUMMARY:", "KEY FINDINGS:", "REBALANCING:", "ACTION ITEMS:"]:
            pos = text.upper().find(kw, start)
            if pos > start and (next_section == -1 or pos < next_section):
                next_section = pos
        end = next_section if next_section > -1 else len(text)
        return text[start:end].strip()[:max_chars]
    except Exception:
        return ""


def _extract_action_items(text: str) -> List[str]:
    """Extract numbered action items."""
    items = []
    try:
        section = _extract_section(text, "ACTION ITEMS", 600)
        lines = section.split('\n')
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                # Remove leading number/dash
                clean = line.lstrip('0123456789.-) ').strip()
                if clean:
                    items.append(clean)
    except Exception:
        pass
    return items[:3]


def _fallback_insights(analysis: Dict) -> Dict:
    """Fallback insights when API is unavailable."""
    xirr = analysis.get("xirr", 0)
    apparent = analysis.get("apparent_return", 0)
    total_value = analysis.get("total_value", 0)
    expense_drain = analysis.get("expense", {}).get("total_drain_over_horizon", 0)
    num_regular = analysis.get("expense", {}).get("num_regular_plans", 0)
    tax_saving = analysis.get("tax", {}).get("total_tax_saving", 0)
    unique_stocks = analysis.get("overlap", {}).get("unique_stocks", 0)
    num_funds = analysis.get("num_funds", 0)

    gap = apparent - xirr

    return {
        "summary": (
            f"Your portfolio of ₹{total_value:,.0f} has a true XIRR of {xirr:.1f}%, "
            f"while your investment app shows {apparent:.1f}% — a gap of {gap:.1f}%. "
            f"Several optimization opportunities exist that can significantly improve your returns."
        ),
        "key_findings": (
            f"• 📉 Return Gap: Your real returns are {gap:.1f}% lower than what apps show — "
            f"this equals a significant sum over your investment horizon.\n"
            f"• 🎭 Diversification Illusion: {num_funds} funds but only {unique_stocks} unique stocks. "
            f"You have more overlap than you think.\n"
            f"• 💸 Fee Drain: {num_regular} Regular Plans are costing you ₹{expense_drain:,.0f} over 10 years in unnecessary commissions."
        ),
        "rebalancing": (
            f"Switch {num_regular} Regular plan funds to Direct plans immediately — "
            f"this alone saves ₹{expense_drain:,.0f} over a decade. "
            f"Consider consolidating overlapping large cap funds into a single Nifty 50 index. "
            f"Allocate freed capital to your highest-conviction mid/small cap conviction."
        ),
        "action_items": [
            f"Switch to Direct Plans → saves ₹{expense_drain:,.0f} over 10 years",
            f"Tax harvest losses → saves ₹{tax_saving:,.0f} this financial year" if tax_saving > 0 else "Review fund overlap and consolidate duplicates",
            "Review and adjust SIP amount to align with your goal timeline",
        ],
        "raw": "",
        "model": "fallback",
    }


# ─────────────────────────────────────────────────────
# GROQ LLAMA 3.3 — Live Portfolio Chat
# ─────────────────────────────────────────────────────
def chat_with_portfolio(
    user_message: str,
    portfolio_context: Dict,
    chat_history: Optional[List[Dict]] = None,
) -> str:
    """
    Use Groq Llama 3.3 to answer user questions about their portfolio.
    This powers the live "ask anything" chat feature.
    """
    try:
        from groq import Groq

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return _fallback_chat(user_message, portfolio_context)

        client = Groq(api_key=api_key)

        system_prompt = _build_chat_system_prompt(portfolio_context)

        messages = [{"role": "system", "content": system_prompt}]

        # Add conversation history (last 6 turns)
        if chat_history:
            for msg in chat_history[-6:]:
                messages.append({"role": msg["role"], "content": msg["content"]})

        messages.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=512,
            temperature=0.7,
        )

        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Groq chat failed: {e}")
        return _fallback_chat(user_message, portfolio_context)


def _build_chat_system_prompt(analysis: Dict) -> str:
    investor = analysis.get("investor", {})
    name = investor.get("name", "the investor")
    total_value = analysis.get("total_value", 0)
    xirr = analysis.get("xirr", 0)
    num_funds = analysis.get("num_funds", 0)
    expense_drain = analysis.get("expense", {}).get("total_drain_over_horizon", 0)
    tax_saving = analysis.get("tax", {}).get("total_tax_saving", 0)
    goal_prob = analysis.get("goal", {}).get("probability", 0)
    unique_stocks = analysis.get("overlap", {}).get("unique_stocks", 0)

    funds_list = ""
    for f in analysis.get("funds", [])[:6]:
        funds_list += f"\n  - {f.get('name', '')[:40]}: ₹{f.get('current_value', 0):,.0f} ({f.get('category', '')})"

    return f"""You are a smart, friendly Indian mutual fund advisor chatbot analyzing {name}'s portfolio.

PORTFOLIO SUMMARY:
- Total Value: ₹{total_value:,.0f}
- True XIRR: {xirr:.1f}%
- Number of Funds: {num_funds}
- Unique Stocks: {unique_stocks}
- 10-Year Expense Drain: ₹{expense_drain:,.0f}
- Tax Harvesting Opportunity: ₹{tax_saving:,.0f}
- Goal Probability: {goal_prob:.0f}%

FUNDS HELD:{funds_list}

INSTRUCTIONS:
- Answer questions about THIS specific portfolio
- Be concise (2-4 sentences max per response)
- Use Indian financial context, rupee amounts
- Reference actual portfolio numbers when relevant
- If asked something outside the portfolio scope, politely redirect
- Don't give generic advice — be specific to their portfolio
- Use casual, friendly tone like a knowledgeable friend"""


def _fallback_chat(message: str, analysis: Dict) -> str:
    """Fallback chat when Groq API is unavailable."""
    msg_lower = message.lower()
    total_value = analysis.get("total_value", 0)
    xirr = analysis.get("xirr", 0)
    expense_drain = analysis.get("expense", {}).get("total_drain_over_horizon", 0)

    if any(w in msg_lower for w in ["xirr", "return", "return"]):
        return f"Your true XIRR is {xirr:.1f}%. This accounts for the exact timing and amount of each SIP, giving you the real picture of your returns."
    elif any(w in msg_lower for w in ["expense", "fee", "cost", "regular", "direct"]):
        return f"Switching to Direct plans can save you ₹{expense_drain:,.0f} over 10 years. That's real money you're currently paying as advisor commission."
    elif any(w in msg_lower for w in ["portfolio", "total", "value", "worth"]):
        return f"Your total portfolio is valued at ₹{total_value:,.0f}. Upload your latest CAMS statement for the most accurate analysis."
    else:
        return "Great question! Please set up your GROQ_API_KEY in the .env file to enable full AI-powered chat. I can answer questions about returns, fees, tax harvesting, and goal planning."
