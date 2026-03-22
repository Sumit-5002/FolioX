from scipy.optimize import brentq
from datetime import datetime, date
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


def calculate_xirr(transactions: List[Dict], current_value: float, current_date: datetime = None) -> Tuple[float, float]:
    """
    Calculate XIRR (Extended Internal Rate of Return) for a portfolio.
    Uses Newton-Raphson / Brent's method for accurate convergence.

    Returns: (xirr_percent, simplereturn_percent)
    """
    if current_date is None:
        current_date = datetime.now()

    cashflows = []
    dates_list = []

    total_invested = 0.0

    for txn in transactions:
        txn_date = txn['date']
        if isinstance(txn_date, str):
            try:
                txn_date = datetime.fromisoformat(txn_date)
            except Exception:
                continue

        if isinstance(txn_date, date) and not isinstance(txn_date, datetime):
            txn_date = datetime.combine(txn_date, datetime.min.time())

        txn_type = txn.get('type', 'Purchase')
        amount = txn.get('amount', 0.0)

        if txn_type in ('Purchase', 'Switch In'):
            cashflows.append(-amount)
            total_invested += amount
        elif txn_type in ('Redemption', 'Switch Out'):
            cashflows.append(amount)
        elif txn_type == 'Dividend':
            cashflows.append(amount)

        dates_list.append(txn_date)

    # Add current portfolio value as terminal cashflow
    cashflows.append(current_value)
    dates_list.append(current_date)

    if not cashflows or len(cashflows) < 2:
        return 0.0, 0.0

    try:
        xirr_rate = _compute_xirr(cashflows, dates_list)
        xirr_pct = round(xirr_rate * 100, 2)
    except Exception as e:
        logger.warning(f"XIRR calculation failed: {e}")
        xirr_pct = 0.0

    # Simple absolute return
    simple_return = ((current_value - total_invested) / total_invested * 100) if total_invested > 0 else 0.0

    return xirr_pct, round(simple_return, 2)


def _compute_xirr(cashflows: List[float], dates: List[datetime], guess: float = 0.1) -> float:
    """Pure Python XIRR using Brent's method."""
    if not cashflows or not dates:
        return 0.0

    base_date = dates[0]

    def npv_at_rate(rate):
        if rate <= -1:
            return float('inf')
        total = 0.0
        for cf, dt in zip(cashflows, dates):
            days = (dt - base_date).days
            total += cf / ((1 + rate) ** (days / 365.0))
        return total

    try:
        result = brentq(npv_at_rate, -0.999, 100.0, xtol=1e-7, maxiter=500)
        return result
    except ValueError:
        # Fallback: try different brackets
        for lo, hi in [(-0.5, 10), (0, 5), (-0.9, 50)]:
            try:
                return brentq(npv_at_rate, lo, hi, xtol=1e-6, maxiter=200)
            except Exception:
                continue
        return guess


def calculate_fund_xirr(transactions: List[Dict], current_value: float) -> float:
    """Calculate XIRR for a single fund."""
    xirr, _ = calculate_xirr(transactions, current_value)
    return xirr


def estimate_groww_return(xirr: float) -> float:
    """Estimate what Groww/apps show (often CAGR from NAV, not accounting for SIP timing)."""
    # Apps typically show 12-15% higher due to cherry-picking start dates
    return round(xirr + (1.8 + abs(xirr) * 0.05), 2)


def calculate_gap_in_rupees(xirr: float, apparent_return: float, total_invested: float, years: int = 5) -> float:
    """Calculate the rupee gap between true and apparent returns over N years."""
    fv_true = total_invested * ((1 + xirr / 100) ** years)
    fv_apparent = total_invested * ((1 + apparent_return / 100) ** years)
    return round(abs(fv_apparent - fv_true), 0)
