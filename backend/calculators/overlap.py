from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Pre-built overlap database for common Indian MF stocks
# Based on typical large/mid cap holdings as of 2024
TYPICAL_FUND_HOLDINGS = {
    '118989': {  # Mirae Asset Large Cap
        'name': 'Mirae Asset Large Cap Fund',
        'holdings': [
            {'company': 'HDFC Bank', 'weight': 9.8},
            {'company': 'ICICI Bank', 'weight': 8.2},
            {'company': 'Reliance Industries', 'weight': 7.5},
            {'company': 'Infosys', 'weight': 6.9},
            {'company': 'TCS', 'weight': 5.8},
            {'company': 'Axis Bank', 'weight': 4.2},
            {'company': 'L&T', 'weight': 3.8},
            {'company': 'Kotak Mahindra Bank', 'weight': 3.5},
            {'company': 'HUL', 'weight': 3.1},
            {'company': 'Bharti Airtel', 'weight': 2.9},
            {'company': 'Maruti Suzuki', 'weight': 2.5},
            {'company': 'Bajaj Finance', 'weight': 2.3},
            {'company': 'Asian Paints', 'weight': 2.0},
            {'company': 'Sun Pharma', 'weight': 1.9},
            {'company': 'Titan Company', 'weight': 1.8},
        ]
    },
    '118560': {  # HDFC Mid Cap
        'name': 'HDFC Mid-Cap Opportunities Fund',
        'holdings': [
            {'company': 'HDFC Bank', 'weight': 4.5},
            {'company': 'Cholamandalam Investment', 'weight': 4.2},
            {'company': 'Persistent Systems', 'weight': 3.9},
            {'company': 'Voltas', 'weight': 3.5},
            {'company': 'Indian Hotels', 'weight': 3.2},
            {'company': 'Max Financial', 'weight': 3.0},
            {'company': 'ICICI Bank', 'weight': 2.8},
            {'company': 'Crompton Greaves', 'weight': 2.6},
            {'company': 'Reliance Industries', 'weight': 2.5},
            {'company': 'Suzlon Energy', 'weight': 2.3},
            {'company': 'Delhivery', 'weight': 2.1},
            {'company': 'Kaveri Seed', 'weight': 1.9},
            {'company': 'Infosys', 'weight': 1.8},
            {'company': 'TCS', 'weight': 1.6},
            {'company': 'Bharti Airtel', 'weight': 1.5},
        ]
    },
    '125354': {  # SBI Small Cap
        'name': 'SBI Small Cap Fund',
        'holdings': [
            {'company': 'Finolex Industries', 'weight': 3.8},
            {'company': 'Lemon Tree Hotels', 'weight': 3.5},
            {'company': 'Blue Star', 'weight': 3.2},
            {'company': 'HDFC Bank', 'weight': 2.9},
            {'company': 'Reliance Industries', 'weight': 2.6},
            {'company': 'Cosmo Films', 'weight': 2.4},
            {'company': 'Hawkins Cookers', 'weight': 2.2},
            {'company': 'ICICI Bank', 'weight': 2.0},
            {'company': 'Infosys', 'weight': 1.9},
            {'company': 'Vinati Organics', 'weight': 1.8},
            {'company': 'Inox Leisure', 'weight': 1.7},
            {'company': 'Repco Home Finance', 'weight': 1.6},
            {'company': 'TCS', 'weight': 1.4},
            {'company': 'Axis Bank', 'weight': 1.3},
            {'company': 'Bharti Airtel', 'weight': 1.2},
        ]
    },
    '120586': {  # ICICI Flexi Cap
        'name': 'ICICI Prudential Flexi Cap Fund',
        'holdings': [
            {'company': 'HDFC Bank', 'weight': 8.9},
            {'company': 'ICICI Bank', 'weight': 7.8},
            {'company': 'Reliance Industries', 'weight': 6.5},
            {'company': 'Infosys', 'weight': 5.8},
            {'company': 'TCS', 'weight': 4.9},
            {'company': 'Axis Bank', 'weight': 3.8},
            {'company': 'Bharti Airtel', 'weight': 3.4},
            {'company': 'L&T', 'weight': 3.1},
            {'company': 'Sun Pharma', 'weight': 2.9},
            {'company': 'Maruti Suzuki', 'weight': 2.7},
            {'company': 'Bajaj Finance', 'weight': 2.5},
            {'company': 'Kotak Mahindra Bank', 'weight': 2.2},
            {'company': 'HUL', 'weight': 2.0},
            {'company': 'Asian Paints', 'weight': 1.8},
            {'company': 'Titan Company', 'weight': 1.6},
        ]
    },
    '115592': {  # Axis ELSS
        'name': 'Axis Long Term Equity Fund',
        'holdings': [
            {'company': 'HDFC Bank', 'weight': 8.2},
            {'company': 'Avenue Supermarts', 'weight': 6.8},
            {'company': 'Bajaj Finance', 'weight': 5.9},
            {'company': 'TCS', 'weight': 5.2},
            {'company': 'Infosys', 'weight': 4.8},
            {'company': 'Reliance Industries', 'weight': 4.5},
            {'company': 'ICICI Bank', 'weight': 4.1},
            {'company': 'Titan Company', 'weight': 3.8},
            {'company': 'Kotak Mahindra Bank', 'weight': 3.5},
            {'company': 'Pidilite Industries', 'weight': 3.2},
            {'company': 'Bharti Airtel', 'weight': 2.9},
            {'company': 'SBI', 'weight': 2.6},
            {'company': 'Asian Paints', 'weight': 2.3},
            {'company': 'L&T', 'weight': 2.0},
            {'company': 'Axis Bank', 'weight': 1.8},
        ]
    },
    '122639': {  # Parag Parikh Flexi Cap
        'name': 'Parag Parikh Flexi Cap Fund',
        'holdings': [
            {'company': 'HDFC Bank', 'weight': 7.5},
            {'company': 'ITC', 'weight': 6.9},
            {'company': 'Coal India', 'weight': 5.8},
            {'company': 'Alphabet (Google)', 'weight': 5.2},
            {'company': 'Microsoft', 'weight': 4.8},
            {'company': 'Power Grid', 'weight': 4.5},
            {'company': 'ICICI Bank', 'weight': 4.2},
            {'company': 'Meta Platforms', 'weight': 3.9},
            {'company': 'Reliance Industries', 'weight': 3.6},
            {'company': 'Bajaj Holdings', 'weight': 3.3},
            {'company': 'Berkshire Hathaway', 'weight': 3.0},
            {'company': 'Amazon', 'weight': 2.7},
            {'company': 'Infosys', 'weight': 2.4},
            {'company': 'TCS', 'weight': 2.1},
            {'company': 'Axis Bank', 'weight': 1.8},
        ]
    },
    '100444': {  # HDFC Liquid
        'name': 'HDFC Liquid Fund',
        'holdings': [
            {'company': 'T-Bills 91 Day', 'weight': 35.0},
            {'company': 'T-Bills 182 Day', 'weight': 25.0},
            {'company': 'RBI Repo', 'weight': 20.0},
            {'company': 'HDFC Bank CD', 'weight': 10.0},
            {'company': 'Axis Bank CD', 'weight': 10.0},
        ]
    },
}


def calculate_overlap(funds: List[Dict]) -> Dict[str, Any]:
    """
    Calculate stock-level overlap across all funds in the portfolio.
    Returns unique stocks, concentration, and top holdings.
    """
    combined_holdings: Dict[str, float] = {}
    fund_details = []

    total_portfolio_value = sum(f.get('current_value', 0) for f in funds)
    if total_portfolio_value == 0:
        return _empty_overlap_result()

    equity_funds = [f for f in funds if f.get('category') not in ('Liquid', 'Debt')]
    equity_value = sum(f.get('current_value', 0) for f in equity_funds)

    for fund in equity_funds:
        fund_weight_in_portfolio = fund.get('current_value', 0) / total_portfolio_value
        fund_key = fund.get('scheme_code', '')
        holdings_data = TYPICAL_FUND_HOLDINGS.get(fund_key, _generate_generic_holdings(fund))

        fund_detail = {
            'name': fund['name'],
            'portfolio_weight': round(fund_weight_in_portfolio * 100, 1),
        }
        fund_details.append(fund_detail)

        for holding in holdings_data.get('holdings', []):
            company = holding['company']
            # Weight in combined portfolio = fund weight * stock weight in fund
            combined_weight = fund_weight_in_portfolio * holding['weight']

            if company in combined_holdings:
                combined_holdings[company] += combined_weight
            else:
                combined_holdings[company] = combined_weight

    # Sort by total weight
    sorted_holdings = sorted(combined_holdings.items(), key=lambda x: x[1], reverse=True)

    unique_stocks = len(combined_holdings)
    top_10 = [{'company': c, 'weight': round(w, 2)} for c, w in sorted_holdings[:10]]
    top_3_concentration = sum(w for _, w in sorted_holdings[:3])
    top_5_concentration = sum(w for _, w in sorted_holdings[:5])

    # Calculate overlap score (higher = more overlapping/less diversified)
    overlap_score = _calculate_overlap_score(equity_funds, combined_holdings)

    return {
        'unique_stocks': unique_stocks,
        'top_holdings': top_10,
        'top_3_concentration': round(top_3_concentration, 1),
        'top_5_concentration': round(top_5_concentration, 1),
        'overlap_score': overlap_score,
        'num_funds': len(equity_funds),
        'fund_details': fund_details,
        'verdict': _get_diversification_verdict(unique_stocks, top_3_concentration, overlap_score),
    }


def _calculate_overlap_score(funds: List[Dict], holdings: Dict[str, float]) -> int:
    """Score 0-100: higher = more overlapping."""
    total_weight = sum(holdings.values())
    if total_weight == 0:
        return 0
    # Herfindahl–Hirschman Index (HHI) normalized
    hhi = sum((w / total_weight * 100) ** 2 for w in holdings.values())
    # Normalize to 0-100 scale
    score = min(100, int(hhi / 50))
    return score


def _get_diversification_verdict(unique_stocks: int, top_3_pct: float, overlap_score: int) -> Dict:
    if unique_stocks < 40 and top_3_pct > 20:
        return {
            'level': 'HIGH_OVERLAP',
            'color': 'red',
            'message': '⚠️ Critical Overlap Detected',
            'detail': f'Your {unique_stocks} "diversified" funds are really just {unique_stocks} stocks in disguise. Top 3 stocks = {top_3_pct:.1f}% of portfolio.',
        }
    elif unique_stocks < 60 or top_3_pct > 15:
        return {
            'level': 'MODERATE_OVERLAP',
            'color': 'amber',
            'message': '📊 Moderate Overlap',
            'detail': f'Some diversification exists but top holdings are concentrated.',
        }
    else:
        return {
            'level': 'LOW_OVERLAP',
            'color': 'green',
            'message': '✅ Well Diversified',
            'detail': 'Your portfolio has good diversification across sectors.',
        }


def _generate_generic_holdings(fund: Dict) -> Dict:
    """Generate typical holdings for unknown funds based on category."""
    category = fund.get('category', 'Equity')
    default_holdings = [
        {'company': 'HDFC Bank', 'weight': 8.5},
        {'company': 'ICICI Bank', 'weight': 7.2},
        {'company': 'Reliance Industries', 'weight': 6.8},
        {'company': 'Infosys', 'weight': 5.9},
        {'company': 'TCS', 'weight': 5.1},
        {'company': 'Axis Bank', 'weight': 4.3},
        {'company': 'L&T', 'weight': 3.7},
        {'company': 'Bharti Airtel', 'weight': 3.2},
        {'company': 'Bajaj Finance', 'weight': 2.9},
        {'company': 'Maruti Suzuki', 'weight': 2.5},
    ]
    return {'holdings': default_holdings}


def _empty_overlap_result() -> Dict:
    return {
        'unique_stocks': 0,
        'top_holdings': [],
        'top_3_concentration': 0,
        'top_5_concentration': 0,
        'overlap_score': 0,
        'num_funds': 0,
        'fund_details': [],
        'verdict': {'level': 'UNKNOWN', 'color': 'gray', 'message': 'No data', 'detail': ''},
    }
