from celery import shared_task
import yfinance as yf
from .models import DailyPrice
from apps.core.models import Instrument
from datetime import date

@shared_task
def update_daily_prices():
    instruments = Instrument.objects.all()
    today = date.today()
    for inst in instruments:
        try:
            tick = yf.Ticker(inst.ticker)
            hist = tick.history(period='1d')
            if not hist.empty:
                close = hist['Close'].iloc[-1]
                DailyPrice.objects.update_or_create(
                    instrument=inst,
                    date=today,
                    defaults={'close': close}
                )
        except Exception as e:
            print(f"Error updating {inst.ticker}: {e}")
    return f"Updated {instruments.count()} instruments"
