from datetime import datetime
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Current tax rates (post-2024 budget)
LTCG_RATE = 0.125   # 12.5% LTCG on equity (above ₹1.25L exempt)
STCG_RATE = 0.20    # 20% STCG on equity
LTCG_EXEMPT = 125000  # ₹1.25L annual exemption


def find_tax_harvesting_opportunities(transactions: List[Dict], funds: List[Dict]) -> Dict[str, Any]:
    """
    Scan for unrealized losses that can be booked to save tax.
    Also identify gains that can be harvested within the ₹1.25L exemption.
    """
    today = datetime.now()
    opportunities = []
    gain_harvesting = []

    # Build current NAV map from funds
    nav_map = {}
    for fund in funds:
        nav_map[fund['name']] = fund.get('current_nav', 0)

    # Group transactions by fund
    fund_txns: Dict[str, List[Dict]] = {}
    for txn in transactions:
        fund_name = txn.get('fund', '')
        if fund_name not in fund_txns:
            fund_txns[fund_name] = []
        fund_txns[fund_name].append(txn)

    total_harvestable_loss = 0.0
    total_tax_saving = 0.0
    total_harvestable_gain = 0.0

    for fund_name, txns in fund_txns.items():
        current_nav = nav_map.get(fund_name, 0)
        if current_nav == 0:
            continue

        for txn in txns:
            if txn.get('type') not in ('Purchase', 'Switch In'):
                continue

            txn_date = txn.get('date')
            if isinstance(txn_date, str):
                try:
                    txn_date = datetime.fromisoformat(txn_date)
                except Exception:
                    continue
            if not isinstance(txn_date, datetime):
                continue

            purchase_nav = txn.get('nav', 0)
            units = txn.get('units', 0)
            if purchase_nav == 0 or units == 0:
                continue

            current_value = units * current_nav
            purchase_value = units * purchase_nav
            unrealized_pnl = current_value - purchase_value
            days_held = (today - txn_date).days

            is_long_term = days_held >= 365

            if unrealized_pnl < -500:  # Meaningful loss threshold ₹500
                if is_long_term:
                    loss_type = 'LTCL'
                    tax_rate = LTCG_RATE
                else:
                    loss_type = 'STCL'
                    tax_rate = STCG_RATE

                loss_amount = abs(unrealized_pnl)
                tax_saving = loss_amount * tax_rate

                total_harvestable_loss += loss_amount
                total_tax_saving += tax_saving

                opportunities.append({
                    'fund': _shorten_name(fund_name),
                    'purchase_date': txn_date.strftime('%d %b %Y'),
                    'days_held': days_held,
                    'loss_type': loss_type,
                    'unrealized_loss': round(loss_amount, 0),
                    'tax_saving': round(tax_saving, 0),
                    'units': round(units, 3),
                    'purchase_nav': round(purchase_nav, 2),
                    'current_nav': round(current_nav, 2),
                    'action': 'Redeem now. Reinvest after 30 days to maintain allocation.',
                })

            elif 0 < unrealized_pnl < LTCG_EXEMPT and is_long_term:
                # Gain harvesting within exemption
                gain_harvesting.append({
                    'fund': _shorten_name(fund_name),
                    'unrealized_gain': round(unrealized_pnl, 0),
                    'days_held': days_held,
                    'action': 'Book gain within ₹1.25L exemption, reinvest immediately.',
                })
                total_harvestable_gain += unrealized_pnl

    # Sort by tax saving
    opportunities.sort(key=lambda x: x['tax_saving'], reverse=True)

    # Determine urgency (financial year ends March 31)
    fy_end = datetime(today.year if today.month <= 3 else today.year + 1, 3, 31)
    days_to_fy_end = (fy_end - today).days

    return {
        'opportunities': opportunities[:10],  # Top 10
        'gain_harvesting': gain_harvesting[:5],
        'total_harvestable_loss': round(total_harvestable_loss, 0),
        'total_tax_saving': round(total_tax_saving, 0),
        'total_harvestable_gain': round(total_harvestable_gain, 0),
        'days_to_fy_end': days_to_fy_end,
        'is_urgent': days_to_fy_end <= 60,
        'has_opportunities': len(opportunities) > 0,
        'verdict': _tax_verdict(total_tax_saving, days_to_fy_end),
    }


def _shorten_name(name: str) -> str:
    name = name.replace('- Regular Plan - Growth', '').replace('- Growth', '').strip()
    if len(name) > 30:
        name = name[:28] + '…'
    return name


def _tax_verdict(tax_saving: float, days_left: int) -> Dict:
    if tax_saving > 5000 and days_left <= 90:
        urgency = '🚨 URGENT' if days_left <= 30 else '⚡ Act Soon'
        return {
            'level': 'URGENT',
            'color': 'red',
            'headline': f'{urgency} — Tax Harvesting Opportunity',
            'message': f'FY ends in {days_left} days. Book losses now to offset capital gains.',
        }
    elif tax_saving > 2000:
        return {
            'level': 'MODERATE',
            'color': 'amber',
            'headline': '🎯 Tax Saving Opportunity Found',
            'message': 'You can harvest losses to reduce your tax liability.',
        }
    elif tax_saving > 0:
        return {
            'level': 'LOW',
            'color': 'green',
            'headline': '💡 Minor Harvesting Opportunity',
            'message': 'Small losses available for harvesting.',
        }
    else:
        return {
            'level': 'NONE',
            'color': 'green',
            'headline': '✅ No Losses to Harvest',
            'message': 'Your portfolio is all in profit. Consider gain harvesting within ₹1.25L exemption.',
        }
