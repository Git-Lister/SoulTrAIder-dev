import logging

from celery import shared_task
from django.utils import timezone

from apps.marketdata.models import DailyPrice

from .models import Prediction

logger = logging.getLogger(__name__)


@shared_task
def evaluate_predictions():
    """
    Check all active predictions with target_date <= today.
    Update status and accuracy based on latest price.
    """
    today = timezone.now().date()
    active = Prediction.objects.filter(status='active', target_date__lte=today)
    evaluated = 0
    for pred in active:
        # Get latest price on or before target_date
        price = DailyPrice.objects.filter(
            instrument=pred.instrument,
            date__lte=pred.target_date
        ).order_by('-date').first()
        if price:
            pred.evaluate(price.close)
            evaluated += 1
    logger.info(f"Evaluated {evaluated} predictions")
    return f"Evaluated {evaluated} predictions"

    # Optionally call update_accuracy_stats() after evaluation
    # from .utils import update_accuracy_stats
    # update_accuracy_stats()
