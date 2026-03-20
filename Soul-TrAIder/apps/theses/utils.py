import logging

from django.db import models
from django.utils import timezone

from .models import Prediction, PredictionAccuracy

logger = logging.getLogger(__name__)


def update_accuracy_stats(instrument=None, source=None):
    """
    Update PredictionAccuracy for the last 30 days.
    Optionally filter by instrument and/or source.
    """
    cutoff = timezone.now().date() - timezone.timedelta(days=30)
    qs = Prediction.objects.filter(created_date__gte=cutoff, status__in=['hit', 'missed'])
    if instrument:
        qs = qs.filter(instrument=instrument)
    if source:
        qs = qs.filter(source=source)
    stats = qs.values('instrument', 'source').annotate(
        total=models.Count('id'),
        hits=models.Count('id', filter=models.Q(status='hit')),
        avg_conf=models.Avg('confidence'),
        avg_acc=models.Avg('accuracy_score')
    )
    for stat in stats:
        # Get or create record for today
        record, created = PredictionAccuracy.objects.update_or_create(
            instrument_id=stat['instrument'],
            source=stat['source'],
            date=timezone.now().date(),
            defaults={
                'total_predictions': stat['total'],
                'hits': stat['hits'],
                'avg_confidence': stat['avg_conf'],
                'avg_accuracy': stat['avg_acc'],
            }
        )
    logger.info(f"Updated accuracy stats for {len(stats)} instrument/source combinations")
    return stats
