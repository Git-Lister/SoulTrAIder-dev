import logging
from datetime import date

import yfinance as yf
from celery import shared_task

from apps.core.models import Instrument

from .models import DailyPrice

logger = logging.getLogger(__name__)

@shared_task
def update_daily_prices():
    """
    Fetch latest closing prices for all instruments and store in DailyPrice.
    """
    instruments = Instrument.objects.all()
    today = date.today()
    updated_count = 0
    errors = []

    for instrument in instruments:
        try:
            ticker = yf.Ticker(instrument.ticker)
            hist = ticker.history(period='1d')
            if not hist.empty:
                close = hist['Close'].iloc[-1]
                DailyPrice.objects.update_or_create(
                    instrument=instrument,
                    date=today,
                    defaults={'close': close, 'volume': hist['Volume'].iloc[-1] if 'Volume' in hist else None}
                )
                updated_count += 1
            else:
                logger.warning(f"No data for {instrument.ticker} on {today}")
        except Exception as e:
            errors.append(f"{instrument.ticker}: {str(e)}")
            logger.error(f"Error updating {instrument.ticker}: {e}")

    return {
        'updated': updated_count,
        'total': instruments.count(),
        'errors': errors
    }

@shared_task
def backfill_prices(days=30):
    """
    Backfill historical prices for all instruments.
    """
    instruments = Instrument.objects.all()
    # ... implementation for backfill if needed