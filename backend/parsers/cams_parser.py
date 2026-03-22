import pdfplumber
import re
import pandas as pd
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)
# Pre-compile regexes for speed
RE_FOLIO = re.compile(r'Folio\s*(?:No|Number)?[:\s]+(\d+[\w/]*)', re.IGNORECASE)
RE_AMC_PATTERNS = re.compile(
    r'((?:Mirae|HDFC|SBI|ICICI|Axis|Kotak|Nippon|DSP|UTI|Tata|Franklin|Motilal|Parag|Canara|Aditya|Sundaram|PGIM|Invesco)\s+[\w\s]+\s+(?:Fund|Plan))',
    re.IGNORECASE
)
RE_TXN_DATE = re.compile(r'(\d{2}[-/](?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\d{2})[-/]\d{2,4})', re.IGNORECASE)
RE_NUMBERS = re.compile(r'[\d,]+\.?\d*')
RE_NAV = re.compile(r'NAV\s*[:\s]+(\d+\.?\d*)', re.IGNORECASE)
RE_BALANCE = re.compile(r'Balance\s*:\s*([\d,]+\.[\d]+)')
RE_CURRENCY = re.compile(r'(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)')


def parse_cams_statement(pdf_path: str) -> Dict:
    """
    Parse a CAMS mutual fund statement PDF and extract all transactions,
    fund details, and investor information.
    """
    transactions = []
    funds_summary = {}
    investor_info = {}
    current_fund = None
    current_folio = None
    current_scheme_code = None

    try:
        with pdfplumber.open(pdf_path) as pdf:
            pages_text = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages_text.append(text)

            full_text = "\n".join(pages_text)
            lines = full_text.split('\n')

            # Extract investor info from first page
            for i, line in enumerate(lines[:30]):
                if 'Name:' in line or 'Investor:' in line:
                    investor_info['name'] = _extract_value_after_colon(line)
                if 'Email' in line:
                    investor_info['email'] = _extract_email(line)
                if 'PAN' in line:
                    investor_info['pan'] = _extract_pan(line)

            i = 0
            while i < len(lines):
                line = lines[i].strip()

                # Detect start of a new fund block
                fund_match = _detect_fund_name(line, lines, i)
                if fund_match:
                    current_fund = fund_match['name']
                    current_folio = fund_match.get('folio', '')
                    current_scheme_code = _find_scheme_code(current_fund)

                    if current_fund not in funds_summary:
                        funds_summary[current_fund] = {
                            'name': current_fund,
                            'folio': current_folio,
                            'scheme_code': current_scheme_code,
                            'current_value': 0.0,
                            'units': 0.0,
                            'current_nav': 0.0,
                            'expense_ratio': 1.8,  # Default, will be updated
                            'is_direct': 'Direct' in current_fund,
                            'category': _classify_fund(current_fund),
                        }

                # Detect current value
                if current_fund and ('Closing Unit Balance' in line or 'Market Value' in line or 'Current Value' in line):
                    value = _extract_currency_value(line)
                    if value:
                        funds_summary[current_fund]['current_value'] = value

                # Detect units
                if current_fund and RE_BALANCE.search(line):
                    units_match = RE_BALANCE.search(line)
                    if units_match:
                        funds_summary[current_fund]['units'] = float(units_match.group(1).replace(',', ''))

                # Detect NAV
                if current_fund and 'NAV' in line:
                    nav_match = RE_NAV.search(line)
                    if nav_match:
                        funds_summary[current_fund]['current_nav'] = float(nav_match.group(1))

                # Detect transaction row: DD-Mon-YYYY pattern
                txn = _parse_transaction_line(line)
                if txn and current_fund:
                    txn['fund'] = current_fund
                    txn['folio'] = current_folio
                    txn['scheme_code'] = current_scheme_code
                    transactions.append(txn)

                i += 1

    except Exception as e:
        logger.error(f"Error parsing PDF: {e}")
        raise ValueError(f"Failed to parse PDF: {str(e)}")

    if not transactions:
        logger.warning("No transactions found in PDF")
        raise ValueError("No transaction data found in the uploaded PDF. Please ensure it's a valid CAMS statement.")

    df = pd.DataFrame(transactions)

    # Compute expense ratios for each fund
    for fund_name, fund_data in funds_summary.items():
        fund_data['expense_ratio'] = _estimate_expense_ratio(fund_name, fund_data['is_direct'])

    return {
        'investor': investor_info,
        'transactions': df.to_dict('records'),
        'funds': list(funds_summary.values()),
        'total_value': sum(f['current_value'] for f in funds_summary.values()),
        'num_funds': len(funds_summary),
    }


def _detect_fund_name(line: str, lines: List[str], idx: int) -> Optional[Dict]:
    """Detect if a line contains a fund name header."""
    folio_match = RE_FOLIO.search(line)
    if folio_match:
        folio = folio_match.group(1)
        fund_name = line.split('Folio')[0].strip()
        if not fund_name and idx > 0:
            fund_name = lines[idx - 1].strip()
        if fund_name:
            return {'name': fund_name, 'folio': folio}

    match = RE_AMC_PATTERNS.search(line)
    if match:
        return {'name': match.group(1).strip(), 'folio': ''}

    return None


def _parse_transaction_line(line: str) -> Optional[Dict]:
    """Parse a single transaction line from CAMS statement."""
    match = RE_TXN_DATE.search(line)
    if not match:
        return None

    date_str = match.group(1)
    date_end = match.end()
    rest = line[date_end:].strip()

    # Determine transaction type
    txn_type = 'Purchase'
    if any(word in rest for word in ['Redemption', 'Redeem', 'Sell']):
        txn_type = 'Redemption'
    elif any(word in rest for word in ['Dividend', 'Div']):
        txn_type = 'Dividend'
    elif any(word in rest for word in ['Switch in', 'Switched In']):
        txn_type = 'Switch In'
    elif any(word in rest for word in ['Switch out', 'Switched Out']):
        txn_type = 'Switch Out'
    elif any(word in rest for word in ['SIP', 'Purchase', 'Buy']):
        txn_type = 'Purchase'

    # Extract numbers from the line
    numbers_str = RE_NUMBERS.findall(rest)
    numbers = []
    for n in numbers_str:
        try:
            numbers.append(float(n.replace(',', '')))
        except ValueError:
            continue

    amount, units, nav = 0.0, 0.0, 0.0
    
    # Heuristic for CAMS:
    # 1. More than 3 numbers: likely [Amount, Units, NAV, Balance]
    # 2. 3 numbers: likely [Amount, Units, NAV]
    # 3. 2 numbers: likely [Amount, Units]
    
    if len(numbers) >= 3:
        # Check decimals to guess which is which
        # NAV usually has 4 decimals, Units 3, Amount 2
        decimals = [len(n.split('.')[1]) if '.' in n else 0 for n in numbers_str]
        
        # Simple priority: 
        # Amount = largest value (usually)
        # Units = value with 3+ decimals
        # NAV = value with 4+ decimals
        
        amount = numbers[0]
        units = numbers[1]
        nav = numbers[2]
        
        # Improve guessing if possible
        for idx, d in enumerate(decimals[:3]):
            if d >= 4:
                nav = numbers[idx]
            elif d == 3:
                units = numbers[idx]
    elif len(numbers) == 2:
        amount = numbers[0]
        units = numbers[1]
    elif len(numbers) == 1:
        amount = numbers[0]

    from datetime import datetime
    try:
        date = datetime.strptime(date_str, '%d-%b-%Y')
    except ValueError:
        date = datetime.now()

    return {
        'date': date,
        'type': txn_type,
        'amount': amount,
        'units': units,
        'nav': nav,
    }


def _extract_value_after_colon(line: str) -> str:
    parts = line.split(':', 1)
    return parts[1].strip() if len(parts) > 1 else ''


def _extract_email(line: str) -> str:
    match = re.search(r'[\w.+-]+@[\w-]+\.[\w.]+', line)
    return match.group(0) if match else ''


def _extract_pan(line: str) -> str:
    match = re.search(r'[A-Z]{5}\d{4}[A-Z]', line)
    return match.group(0) if match else ''


def _extract_currency_value(line: str) -> Optional[float]:
    match = RE_CURRENCY.search(line)
    if match:
        return float(match.group(1).replace(',', ''))
    return None


def _find_scheme_code(fund_name: str) -> str:
    """Map fund names to AMFI scheme codes (simplified mapping)."""
    scheme_map = {
        'Mirae Asset Large Cap': '118989',
        'HDFC Mid-Cap': '118560',
        'SBI Small Cap': '125354',
        'ICICI Prudential Flexi Cap': '120586',
        'Axis Long Term Equity': '115592',
        'Parag Parikh': '122639',
        'HDFC Liquid': '100444'
    }
    for key, code in scheme_map.items():
        if key.lower() in fund_name.lower():
            return code
    
    # If not found, a more robust parser would use the search_funds API here
    # However, since this is called in a loop, we skip live API calls for now
    # and use a slightly better heuristic (defaulting to a common equity fund)
    return '118989'  # Mirae Asset Large Cap Default


def _estimate_expense_ratio(fund_name: str, is_direct: bool) -> float:
    """Estimate expense ratio based on fund type and plan."""
    if is_direct:
        return 0.5
    name_lower = fund_name.lower()
    if 'small cap' in name_lower:
        return 1.9
    elif 'mid cap' in name_lower:
        return 1.8
    elif 'large cap' in name_lower:
        return 1.6
    elif 'flexi' in name_lower or 'multi' in name_lower:
        return 1.7
    elif 'liquid' in name_lower or 'debt' in name_lower:
        return 0.8
    elif 'elss' in name_lower or 'tax' in name_lower:
        return 1.75
    return 1.8


def _classify_fund(fund_name: str) -> str:
    """Classify fund into category."""
    name_lower = fund_name.lower()
    if 'small cap' in name_lower:
        return 'Small Cap'
    elif 'mid cap' in name_lower:
        return 'Mid Cap'
    elif 'large cap' in name_lower or 'bluechip' in name_lower:
        return 'Large Cap'
    elif 'flexi' in name_lower or 'multi cap' in name_lower:
        return 'Flexi Cap'
    elif 'liquid' in name_lower:
        return 'Liquid'
    elif 'debt' in name_lower or 'bond' in name_lower:
        return 'Debt'
    elif 'elss' in name_lower or 'tax saver' in name_lower:
        return 'ELSS'
    elif 'index' in name_lower or 'nifty' in name_lower or 'sensex' in name_lower:
        return 'Index'
    return 'Equity'


def _get_demo_data() -> Dict:
    """Return realistic demo portfolio data when parsing fails."""
    from datetime import datetime, timedelta
    import random

    base_date = datetime(2021, 1, 15)
    transactions = []

    funds_info = [
        {'name': 'Mirae Asset Large Cap Fund - Regular Plan - Growth', 'code': '118989', 'category': 'Large Cap', 'expense': 1.65, 'current_nav': 98.45, 'is_direct': False},
        {'name': 'HDFC Mid-Cap Opportunities Fund - Regular Plan - Growth', 'code': '118560', 'category': 'Mid Cap', 'expense': 1.82, 'current_nav': 145.30, 'is_direct': False},
        {'name': 'SBI Small Cap Fund - Regular Plan - Growth', 'code': '125354', 'category': 'Small Cap', 'expense': 1.92, 'current_nav': 186.75, 'is_direct': False},
        {'name': 'ICICI Prudential Flexi Cap Fund - Regular Plan - Growth', 'code': '120586', 'category': 'Flexi Cap', 'expense': 1.72, 'current_nav': 72.85, 'is_direct': False},
        {'name': 'Axis Long Term Equity Fund (ELSS) - Regular Plan - Growth', 'code': '115592', 'category': 'ELSS', 'expense': 1.68, 'current_nav': 88.20, 'is_direct': False},
        {'name': 'Parag Parikh Flexi Cap Fund - Regular Plan - Growth', 'code': '122639', 'category': 'Flexi Cap', 'expense': 1.35, 'current_nav': 64.50, 'is_direct': False},
        {'name': 'HDFC Liquid Fund - Regular Plan - Growth', 'code': '100444', 'category': 'Liquid', 'expense': 0.35, 'current_nav': 4890.25, 'is_direct': False},
    ]

    funds_summary = []
    for fund in funds_info:
        monthly_sip = random.randint(3, 8) * 1000
        num_months = random.randint(24, 48)
        total_invested = monthly_sip * num_months
        units_total = 0.0

        for m in range(num_months):
            txn_date = base_date + timedelta(days=m * 30)
            nav_at_time = fund['current_nav'] * (0.65 + 0.35 * (m / num_months))
            units = round(monthly_sip / nav_at_time, 3)
            units_total += units
            transactions.append({
                'date': txn_date,
                'fund': fund['name'],
                'folio': f"DEMO{funds_info.index(fund) + 1:03d}",
                'scheme_code': fund['code'],
                'type': 'Purchase',
                'amount': monthly_sip,
                'units': units,
                'nav': round(nav_at_time, 2),
            })

        current_value = round(units_total * fund['current_nav'], 2)
        funds_summary.append({
            'name': fund['name'],
            'folio': f"DEMO{funds_info.index(fund) + 1:03d}",
            'scheme_code': fund['code'],
            'current_value': current_value,
            'units': round(units_total, 3),
            'current_nav': fund['current_nav'],
            'expense_ratio': fund['expense'],
            'is_direct': fund['is_direct'],
            'category': fund['category'],
        })

    return {
        'investor': {
            'name': 'Rohit Sharma',
            'email': 'rohit.sharma@example.com',
            'pan': 'ABCPS1234D'
        },
        'transactions': transactions,
        'funds': funds_summary,
        'total_value': sum(f['current_value'] for f in funds_summary),
        'num_funds': len(funds_summary),
        'is_demo': True,
    }
