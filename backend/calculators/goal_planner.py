from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)

EQUITY_RETURN = 0.12  # 12% equity historical
DEBT_RETURN = 0.07    # 7% debt
MONTHLY_EQUITY = EQUITY_RETURN / 12
MONTHLY_DEBT = DEBT_RETURN / 12


def calculate_goal_probability(
    current_portfolio_value: float,
    monthly_sip: float,
    target_amount: float,
    years_to_goal: int,
    current_equity_pct: float,  # 0.0 to 1.0
) -> Dict:
    """
    Calculate probability of reaching a financial goal and
    generate rebalancing recommendations.
    """
    blended_annual = (current_equity_pct * EQUITY_RETURN + (1 - current_equity_pct) * DEBT_RETURN)
    monthly_rate = blended_annual / 12
    n_months = years_to_goal * 12

    # Future value of existing corpus
    fv_lumpsum = current_portfolio_value * ((1 + blended_annual) ** years_to_goal)

    # Future value of ongoing SIPs
    if monthly_rate > 0:
        fv_sip = monthly_sip * (((1 + monthly_rate) ** n_months - 1) / monthly_rate) * (1 + monthly_rate)
    else:
        fv_sip = monthly_sip * n_months

    total_fv = fv_lumpsum + fv_sip
    probability = min(110.0, (total_fv / target_amount) * 100) if target_amount > 0 else 0

    # Optimal equity allocation for this goal horizon
    optimal_equity = _optimal_equity_for_horizon(years_to_goal)
    optimal_blended = (optimal_equity * EQUITY_RETURN + (1 - optimal_equity) * DEBT_RETURN)
    optimal_monthly_rate = optimal_blended / 12

    fv_optimal_lumpsum = current_portfolio_value * ((1 + optimal_blended) ** years_to_goal)
    if optimal_monthly_rate > 0:
        fv_optimal_sip = monthly_sip * (((1 + optimal_monthly_rate) ** n_months - 1) / optimal_monthly_rate) * (1 + optimal_monthly_rate)
    else:
        fv_optimal_sip = monthly_sip * n_months
    total_fv_optimized = fv_optimal_lumpsum + fv_optimal_sip
    probability_optimized = min(110.0, (total_fv_optimized / target_amount) * 100) if target_amount > 0 else 0

    # Required monthly SIP to hit goal
    if monthly_rate > 0:
        remaining_needed = max(0, target_amount - fv_lumpsum)
        sip_needed = remaining_needed * monthly_rate / (((1 + monthly_rate) ** n_months - 1) * (1 + monthly_rate))
    else:
        sip_needed = target_amount / max(n_months, 1)

    gap = max(0, target_amount - total_fv)

    return {
        'total_future_value': round(total_fv, 0),
        'total_future_value_optimized': round(total_fv_optimized, 0),
        'probability': round(probability, 1),
        'probability_optimized': round(probability_optimized, 1),
        'target_amount': target_amount,
        'years_to_goal': years_to_goal,
        'gap': round(gap, 0),
        'monthly_sip_needed': round(sip_needed, 0),
        'sip_increase_needed': round(max(0, sip_needed - monthly_sip), 0),
        'current_equity_pct': round(current_equity_pct * 100, 1),
        'optimal_equity_pct': round(optimal_equity * 100, 1),
        'blended_return': round(blended_annual * 100, 2),
        'rebalancing_actions': _generate_rebalancing_actions(current_equity_pct, optimal_equity, current_portfolio_value),
        'verdict': _goal_verdict(probability, probability_optimized),
    }


def _optimal_equity_for_horizon(years: int) -> float:
    """Recommend equity allocation based on time horizon."""
    if years >= 10:
        return 0.90
    elif years >= 7:
        return 0.80
    elif years >= 5:
        return 0.70
    elif years >= 3:
        return 0.55
    elif years >= 1:
        return 0.40
    else:
        return 0.20


def _generate_rebalancing_actions(current_equity: float, optimal_equity: float, portfolio_value: float) -> list:
    actions = []
    diff = optimal_equity - current_equity

    if abs(diff) < 0.05:
        actions.append({
            'type': 'MAINTAIN',
            'priority': 'LOW',
            'action': 'Your equity-debt allocation is on track. No changes needed.',
        })
    elif diff > 0:
        shift_amount = round(portfolio_value * diff, 0)
        actions.append({
            'type': 'INCREASE_EQUITY',
            'priority': 'HIGH',
            'action': f'Move ₹{shift_amount:,.0f} from Debt/Liquid funds to Equity funds',
            'amount': shift_amount,
        })
    else:
        shift_amount = round(portfolio_value * abs(diff), 0)
        actions.append({
            'type': 'INCREASE_DEBT',
            'priority': 'HIGH',
            'action': f'Move ₹{shift_amount:,.0f} from Equity to Debt/Liquid funds',
            'amount': shift_amount,
        })

    # Always suggest switching regular to direct
    actions.append({
        'type': 'SWITCH_TO_DIRECT',
        'priority': 'HIGH',
        'action': 'Switch all Regular plan funds to Direct plans to save ~1% p.a.',
    })

    return actions


def _goal_verdict(prob: float, prob_optimized: float) -> Dict:
    if prob >= 100:
        return {
            'color': 'green',
            'icon': '🎯',
            'status': 'ON_TRACK',
            'headline': 'You\'re on track!',
            'message': f'Current trajectory is {prob:.0f}% of your goal. Keep it up!',
        }
    elif prob_optimized >= 100:
        return {
            'color': 'amber',
            'icon': '⚡',
            'status': 'REBALANCE_NEEDED',
            'headline': 'Rebalancing can get you there',
            'message': f'Current trajectory: {prob:.0f}%. After rebalancing: {prob_optimized:.0f}%. Small changes, big impact.',
        }
    elif prob >= 75:
        return {
            'color': 'amber',
            'icon': '📈',
            'status': 'CLOSE',
            'headline': 'Almost there — increase SIP',
            'message': f'You\'ll reach {prob:.0f}% of your goal. A small SIP bump will close the gap.',
        }
    else:
        return {
            'color': 'red',
            'icon': '⚠️',
            'status': 'ACTION_REQUIRED',
            'headline': 'Goal at risk — action needed',
            'message': f'Current trajectory: {prob:.0f}%. Significant SIP increase or timeline extension needed.',
        }
