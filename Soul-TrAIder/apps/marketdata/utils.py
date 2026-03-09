from datetime import date, timedelta

import yfinance as yf

from .models import DailyPrice


def get_latest_price(instrument_id):
    """
    Get the most recent stored price for an instrument.
    Returns (price, date) tuple.
    """
    try:
        latest = DailyPrice.objects.filter(instrument_id=instrument_id).order_by('-date').first()
        if latest:
            return latest.close, latest.date
    except:
        pass
    return None, None

def fetch_live_price(ticker):
    """
    Fallback: fetch live price directly from yfinance.
    """
    try:
        tick = yf.Ticker(ticker)
        data = tick.history(period='1d')
        if not data.empty:
            return data['Close'].iloc[-1]
    except:
        pass
    return None