from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

ASSUMED_MARKET_RETURN = 0.12  # 12% p.a. equity return assumption
DIRECT_PLAN_SAVINGS = 1.0     # Direct plans save ~1% in expense ratio


def calculate_expense_drain(funds: List[Dict], horizon_years: int = 10) -> Dict:
    """
    Calculate the total rupee cost of being on Regular plans vs Direct plans.
    Also shows per-fund breakdown.
    """
    results = []
    total_annual_drain = 0.0
    total_decade_drain = 0.0

    for fund in funds:
        if fund.get('category') in ('Liquid', 'Debt'):
            # Liquid/debt plans have smaller direct vs regular gap
            savings_pct = 0.3
        else:
            savings_pct = DIRECT_PLAN_SAVINGS

        current_value = fund.get('current_value', 0)
        regular_expense = fund.get('expense_ratio', 1.8)
        is_direct = fund.get('is_direct', False)

        if is_direct:
            # Already on direct — still show data but no drain
            results.append({
                'fund': _shorten_fund_name(fund['name']),
                'is_direct': True,
                'expense_ratio': regular_expense,
                'annual_drain': 0,
                'drain_over_horizon': 0,
                'current_value': current_value,
                'category': fund.get('category', 'Equity'),
            })
            continue

        direct_expense = max(0.1, regular_expense - savings_pct)

        # Future value under regular plan vs direct
        fv_regular = current_value * ((1 + ASSUMED_MARKET_RETURN - regular_expense / 100) ** horizon_years)
        fv_direct = current_value * ((1 + ASSUMED_MARKET_RETURN - direct_expense / 100) ** horizon_years)
        drain = max(0, fv_direct - fv_regular)
        annual_drain = current_value * savings_pct / 100

        total_annual_drain += annual_drain
        total_decade_drain += drain

        results.append({
            'fund': _shorten_fund_name(fund['name']),
            'is_direct': False,
            'expense_ratio': regular_expense,
            'direct_expense': direct_expense,
            'annual_drain': round(annual_drain, 0),
            'drain_over_horizon': round(drain, 0),
            'current_value': round(current_value, 0),
            'category': fund.get('category', 'Equity'),
        })

    regular_funds = [f for f in results if not f['is_direct']]
    direct_funds = [f for f in results if f['is_direct']]

    return {
        'fund_breakdown': results,
        'total_annual_drain': round(total_annual_drain, 0),
        'total_drain_over_horizon': round(total_decade_drain, 0),
        'horizon_years': horizon_years,
        'num_regular_plans': len(regular_funds),
        'num_direct_plans': len(direct_funds),
        'verdict': _expense_verdict(total_decade_drain, len(regular_funds)),
    }


def _shorten_fund_name(name: str) -> str:
    """Shorten fund name removing plan/option suffixes."""
    name = name.replace('- Regular Plan - Growth', '').replace('- Growth', '').strip()
    name = name.replace('- Direct Plan - Growth', ' (Direct)').strip()
    # Truncate long names
    if len(name) > 32:
        name = name[:30] + '…'
    return name


def _expense_verdict(total_drain: float, num_regular: int) -> Dict:
    if num_regular == 0:
        return {
            'status': 'GOOD',
            'color': 'green',
            'headline': '✅ All Direct Plans',
            'message': 'You are already on direct plans. Great job saving on fees!',
        }
    elif total_drain > 100000:
        return {
            'status': 'CRITICAL',
            'color': 'red',
            'headline': '🚨 Major Fee Leak Detected',
            'message': f'You are on {num_regular} Regular Plans. Your advisor collects commission while your returns bleed.',
        }
    else:
        return {
            'status': 'WARNING',
            'color': 'amber',
            'headline': '⚠️ Paying Unnecessary Fees',
            'message': f'{num_regular} funds are on Regular Plans. Switching to Direct can save significantly.',
        }
