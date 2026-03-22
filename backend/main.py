"""
MF Portfolio X-Ray — FastAPI Backend
Endpoints:
  POST /api/analyze        - Upload CAMS PDF → full analysis
  POST /api/analyze/demo   - Load demo portfolio
  POST /api/chat           - AI chat about portfolio (Groq)
  GET  /api/nav/{code}     - Live NAV lookup
  GET  /health             - Health check
"""
import os
import uuid
import logging
import tempfile
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# ── Internal modules ──────────────────────────────────────
from parsers.cams_parser import parse_cams_statement, _get_demo_data
from calculators.xirr import calculate_xirr, estimate_groww_return, calculate_gap_in_rupees
from calculators.overlap import calculate_overlap
from calculators.expense import calculate_expense_drain
from calculators.tax_harvest import find_tax_harvesting_opportunities
from calculators.goal_planner import calculate_goal_probability
from data_fetchers.mfapi_client import enrich_funds_with_live_nav, get_fund_nav, get_nifty50_returns
from ai.gemini_insights import generate_portfolio_insights, chat_with_portfolio

# ── App Setup ─────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MF Portfolio X-Ray API",
    description="AI-powered mutual fund portfolio analyzer",
    version="1.0.0",
)

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:3000", "https://*.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store (replace with Redis for production)
_session_store: Dict[str, Dict] = {}


# ── Pydantic Models ───────────────────────────────────────
class GoalInput(BaseModel):
    goal_name: str = "Retirement"
    target_amount: float = 5000000
    years_to_goal: int = 10
    monthly_sip: float = 10000


class ChatRequest(BaseModel):
    session_id: str
    message: str
    history: Optional[List[Dict]] = []


# ── Helper ────────────────────────────────────────────────
def _run_full_analysis(parsed: Dict, goal: GoalInput) -> Dict:
    """Run all calculators on parsed portfolio data and return full analysis."""
    transactions = parsed["transactions"]
    funds = parsed["funds"]
    total_value = parsed["total_value"]

    # 1. Enrich with live NAV
    funds = enrich_funds_with_live_nav(funds)
    total_value = sum(f.get("current_value", 0) for f in funds)

    # 2. XIRR
    xirr_pct, simple_return = calculate_xirr(transactions, total_value)
    apparent_return = estimate_groww_return(xirr_pct)
    total_invested = sum(t["amount"] for t in transactions if t.get("type") in ("Purchase", "Switch In"))
    xirr_gap_rupees = calculate_gap_in_rupees(xirr_pct, apparent_return, total_invested, 5)

    # 3. Overlap / Diversification
    overlap = calculate_overlap(funds)

    # 4. Expense drain
    expense = calculate_expense_drain(funds, horizon_years=10)

    # 5. Tax harvesting
    tax = find_tax_harvesting_opportunities(transactions, funds)

    # 6. Goal planning
    equity_value = sum(f.get("current_value", 0) for f in funds if f.get("category") not in ("Liquid", "Debt"))
    equity_pct = (equity_value / total_value) if total_value > 0 else 0.8

    goal_result = calculate_goal_probability(
        current_portfolio_value=total_value,
        monthly_sip=goal.monthly_sip,
        target_amount=goal.target_amount,
        years_to_goal=goal.years_to_goal,
        current_equity_pct=equity_pct,
    )

    # 7. Nifty 50 benchmark
    benchmark = get_nifty50_returns(5)

    analysis = {
        "investor": parsed.get("investor", {}),
        "total_value": round(total_value, 2),
        "total_invested": round(total_invested, 2),
        "num_funds": parsed["num_funds"],
        "funds": funds,
        "xirr": xirr_pct,
        "simple_return": simple_return,
        "apparent_return": apparent_return,
        "xirr_gap_rupees": xirr_gap_rupees,
        "overlap": overlap,
        "expense": expense,
        "tax": tax,
        "goal": {**goal_result, "goal_name": goal.goal_name},
        "benchmark": benchmark,
        "is_demo": parsed.get("is_demo", False),
    }

    # 8. AI insights (Gemini Flash)
    insights = generate_portfolio_insights(analysis)
    analysis["insights"] = insights

    return analysis


# ── Routes ────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "service": "MF Portfolio X-Ray API"}


@app.post("/api/analyze")
async def analyze_portfolio(
    file: UploadFile = File(...),
    goal_name: str = Form("Retirement"),
    target_amount: float = Form(5000000),
    years_to_goal: int = Form(10),
    monthly_sip: float = Form(10000),
):
    """
    Upload a CAMS PDF statement and get full portfolio analysis.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    goal = GoalInput(
        goal_name=goal_name,
        target_amount=target_amount,
        years_to_goal=years_to_goal,
        monthly_sip=monthly_sip,
    )

    # Save PDF to temp file
    suffix = f"_{uuid.uuid4().hex[:8]}.pdf"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        parsed = parse_cams_statement(tmp_path)
        result = _run_full_analysis(parsed, goal)
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

    # Store result in session
    session_id = uuid.uuid4().hex
    _session_store[session_id] = result
    result["session_id"] = session_id

    return JSONResponse(content=result)


@app.post("/api/analyze/demo")
async def analyze_demo(goal: GoalInput = None):
    """
    Load the pre-built demo portfolio for instant demo without PDF upload.
    """
    if goal is None:
        goal = GoalInput()

    try:
        parsed = _get_demo_data()
        result = _run_full_analysis(parsed, goal)
        result["is_demo"] = True
    except Exception as e:
        logger.error(f"Demo analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Demo analysis failed: {str(e)}")

    session_id = uuid.uuid4().hex
    _session_store[session_id] = result
    result["session_id"] = session_id

    return JSONResponse(content=result)


@app.post("/api/chat")
async def portfolio_chat(req: ChatRequest):
    """
    Live AI chat about the portfolio using Groq Llama 3.3.
    """
    session_data = _session_store.get(req.session_id, {})
    if not session_data:
        return {"reply": "Session not found. Please re-analyze your portfolio first."}

    reply = chat_with_portfolio(
        user_message=req.message,
        portfolio_context=session_data,
        chat_history=req.history or [],
    )
    return {"reply": reply, "model": "groq-llama-3.3"}


@app.get("/api/nav/{scheme_code}")
def get_nav(scheme_code: str):
    """Fetch live NAV for any fund scheme code."""
    nav = get_fund_nav(scheme_code)
    if nav is None:
        raise HTTPException(status_code=404, detail=f"NAV not found for scheme {scheme_code}")
    return {"scheme_code": scheme_code, "nav": nav}


@app.get("/api/benchmark/nifty50")
def nifty50_benchmark(years: int = 5):
    """Get Nifty 50 benchmark returns."""
    return get_nifty50_returns(years)
