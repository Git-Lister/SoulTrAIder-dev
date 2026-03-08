import yfinance as yf
from .models import DailyPrice

def get_latest_price(ticker):
    # Try DB first
    latest = DailyPrice.objects.filter(instrument__ticker=ticker).order_by('-date').first()
    if latest:
        return latest.close
    # Otherwise fetch live
    try:
        tick = yf.Ticker(ticker)
        data = tick.history(period='1d')
        if not data.empty:
            return data['Close'].iloc[-1]
    except Exception:
        pass
    return None
