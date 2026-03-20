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


@shared_task
def update_technical_indicators(days_back=90):
    """
    Compute technical indicators for all instruments for the last `days_back` days.
    Uses pandas to calculate RSI, SMA, etc.
    """
    import numpy as np
    import pandas as pd

    from apps.marketdata.models import TechnicalIndicator

    instruments = Instrument.objects.all()
    for inst in instruments:
        prices_qs = DailyPrice.objects.filter(instrument=inst).order_by('date')[:days_back]
        if prices_qs.count() < 20:
            logger.warning(f"Insufficient data for {inst.ticker} (need at least 20 days)")
            continue

        data = pd.DataFrame(list(prices_qs.values('date', 'close', 'volume')))
        if data.empty:
            continue
        data = data.set_index('date')
        close = data['close'].astype(float)

        sma_20 = None
        sma_50 = None
        rsi = None

        if len(close) >= 20:
            sma_20 = close.rolling(window=20).mean()
        if len(close) >= 50:
            sma_50 = close.rolling(window=50).mean()

        if len(close) >= 15:
            delta = close.diff()
            gain = delta.where(delta > 0, 0).rolling(window=14).mean()
            loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))

        for date_idx, row in data.iterrows():
            TechnicalIndicator.objects.update_or_create(
                instrument=inst,
                date=date_idx,
                defaults={
                    'rsi': float(rsi.get(date_idx)) if rsi is not None and date_idx in rsi.index else None,
                    'sma_20': float(sma_20.get(date_idx)) if sma_20 is not None and date_idx in sma_20.index else None,
                    'sma_50': float(sma_50.get(date_idx)) if sma_50 is not None and date_idx in sma_50.index else None,
                    'volume': int(row.get('volume')) if 'volume' in row and row.get('volume') is not None else None,
                }
            )

    logger.info(f"Updated technical indicators for {instruments.count()} instruments")
    return f"Updated technical indicators for {instruments.count()} instruments"


@shared_task
def update_correlation_matrix(period_days=90):
    """
    Compute correlation matrix for all instruments using daily returns.
    Stores as JSON in CorrelationMatrix.
    """
    import pandas as pd
    from django.utils import timezone

    from apps.marketdata.models import CorrelationMatrix

    instruments = Instrument.objects.all()
    if not instruments:
        return "No instruments found"

    cutoff = timezone.now().date() - timezone.timedelta(days=period_days)
    prices = DailyPrice.objects.filter(date__gte=cutoff).select_related('instrument')
    if not prices:
        return "No price data for period"

    data = {}
    for p in prices:
        ticker = p.instrument.ticker
        if ticker not in data:
            data[ticker] = {}
        data[ticker][p.date] = float(p.close)

    df = pd.DataFrame(data)
    if df.empty:
        return "No data after pivot"

    returns = df.pct_change().dropna()
    if returns.empty:
        return "Insufficient data for returns"

    corr_matrix = returns.corr()
    corr_dict = corr_matrix.to_dict()

    CorrelationMatrix.objects.create(
        matrix=corr_dict,
        method='pearson',
        period_days=period_days
    )
    logger.info("Correlation matrix updated")
    return "Correlation matrix updated"