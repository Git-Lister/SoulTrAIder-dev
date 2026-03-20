import logging

from django.utils import timezone

from apps.marketdata.models import DailyPrice

from .models import HypotheticalTrade, Prediction

logger = logging.getLogger(__name__)


def create_trade_from_prediction(prediction: Prediction, quantity=1):
    """
    Create a hypothetical trade based on a prediction.
    For direction 'up' -> long, 'down' -> short.
    Entry price is the latest DailyPrice on or before prediction created_date.
    Returns the created HypotheticalTrade or None if price not found.
    """
    if prediction.prediction_type != 'price_target' or prediction.direction not in ['up', 'down']:
        logger.warning(f"Prediction {prediction.id} not suitable for hypothetical trade")
        return None

    direction = 'long' if prediction.direction == 'up' else 'short'
    # Get price on or before created_date
    price = DailyPrice.objects.filter(
        instrument=prediction.instrument,
        date__lte=prediction.created_date
    ).order_by('-date').first()
    if not price:
        logger.warning(f"No price found for {prediction.instrument} on or before {prediction.created_date}")
        return None

    trade = HypotheticalTrade.objects.create(
        thesis=prediction.thesis,
        instrument=prediction.instrument,
        entry_date=prediction.created_date,
        entry_price=price.close,
        quantity=quantity,
        direction=direction,
        prediction=prediction,
        status='open'
    )
    logger.info(f"Created hypothetical trade {trade.id} from prediction {prediction.id}")
    return trade


def close_trade(trade: HypotheticalTrade, exit_date, exit_price):
    """
    Close an open hypothetical trade and calculate profit/loss.
    """
    if trade.status != 'open':
        logger.warning(f"Trade {trade.id} is already closed")
        return None

    trade.exit_date = exit_date
    trade.exit_price = exit_price
    profit = (exit_price - trade.entry_price) * trade.quantity
    if trade.direction == 'short':
        profit = -profit
    trade.profit_loss = profit
    trade.status = 'closed'
    trade.save()
    logger.info(f"Closed trade {trade.id} with P/L {profit}")
    return trade
