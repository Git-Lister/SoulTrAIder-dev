from django.db import models
from apps.core.models import Instrument
from apps.theses.models import Prediction

class Alert(models.Model):
    ALERT_TYPES = [
        ('target', 'Target'),
        ('stop_loss', 'Stop Loss'),
        ('news', 'News'),
    ]
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE)
    prediction = models.ForeignKey(Prediction, on_delete=models.SET_NULL, null=True, blank=True)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    threshold = models.DecimalField(max_digits=10, decimal_places=4)
    triggered = models.BooleanField(default=False)
    triggered_at = models.DateTimeField(null=True, blank=True)
    message = models.TextField(blank=True)

    def __str__(self):
        return f"{self.instrument} - {self.alert_type}"
