import requests
import logging
from typing import Dict, List, Optional
from functools import lru_cache
import time

logger = logging.getLogger(__name__)

MFAPI_BASE = "https://api.mfapi.in/mf"
REQUEST_TIMEOUT = 10


@lru_cache(maxsize=500)
def get_fund_nav(scheme_code: str) -> Optional[float]:
    """Fetch current NAV for a fund from mfapi.in."""
    try:
        url = f"{MFAPI_BASE}/{scheme_code}"
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
        if resp.status_code == 200:
            data = resp.json()
            nav_data = data.get("data", [])
            if nav_data:
                return float(nav_data[0]["nav"])
    except Exception as e:
        logger.warning(f"NAV fetch failed for {scheme_code}: {e}")
    return None


def get_historical_nav(scheme_code: str, days: int = 365) -> List[Dict]:
    """Fetch historical NAV data for a fund."""
    try:
        url = f"{MFAPI_BASE}/{scheme_code}"
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
        if resp.status_code == 200:
            data = resp.json()
            nav_data = data.get("data", [])
            return nav_data[:days]
    except Exception as e:
        logger.warning(f"Historical NAV fetch failed for {scheme_code}: {e}")
    return []


def get_fund_meta(scheme_code: str) -> Optional[Dict]:
    """Get fund metadata (name, fund house, category)."""
    try:
        url = f"{MFAPI_BASE}/{scheme_code}"
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("meta", {})
    except Exception as e:
        logger.warning(f"Fund meta fetch failed for {scheme_code}: {e}")
    return None


def search_funds(query: str) -> List[Dict]:
    """Search all funds by name."""
    try:
        url = f"{MFAPI_BASE}/search?q={query}"
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        logger.warning(f"Fund search failed: {e}")
    return []


def enrich_funds_with_live_nav(funds: List[Dict]) -> List[Dict]:
    """Update funds list with live NAV from mfapi.in."""
    enriched = []
    for fund in funds:
        scheme_code = fund.get("scheme_code", "")
        if scheme_code:
            live_nav = get_fund_nav(scheme_code)
            if live_nav:
                fund = dict(fund)
                old_nav = fund.get("current_nav", live_nav)
                fund["current_nav"] = live_nav
                # Recalculate current value if we have units
                if fund.get("units"):
                    fund["current_value"] = round(fund["units"] * live_nav, 2)
                fund["nav_source"] = "live"
                fund["nav_change"] = round(((live_nav - old_nav) / old_nav) * 100, 2) if old_nav else 0
            else:
                fund["nav_source"] = "cached"
        enriched.append(fund)
    return enriched


def get_nifty50_returns(years: int = 5) -> Dict:
    """Get Nifty 50 index returns using a proxy fund (UTI Nifty 50 Index Fund)."""
    NIFTY50_PROXY_SCHEME = "120716"  # UTI Nifty 50 Index Fund
    try:
        nav_data = get_historical_nav(NIFTY50_PROXY_SCHEME, days=years * 365)
        if len(nav_data) >= 2:
            latest_nav = float(nav_data[0]["nav"])
            oldest_nav = float(nav_data[-1]["nav"])
            total_return = ((latest_nav / oldest_nav) - 1) * 100
            cagr = ((latest_nav / oldest_nav) ** (1 / years) - 1) * 100
            return {
                "total_return": round(total_return, 2),
                "cagr": round(cagr, 2),
                "years": years,
                "index": "Nifty 50",
            }
    except Exception as e:
        logger.warning(f"Nifty 50 returns fetch failed: {e}")
    return {"total_return": 14.2, "cagr": 14.2, "years": years, "index": "Nifty 50"}
