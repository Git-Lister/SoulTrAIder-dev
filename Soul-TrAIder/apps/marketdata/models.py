from django.db import models
from apps.core.models import Instrument

class DailyPrice(models.Model):
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE)
    date = models.DateField()
    close = models.DecimalField(max_digits=10, decimal_places=4)
    volume = models.BigIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('instrument', 'date')

    def __str__(self):
        return f"{self.instrument.ticker} - {self.date}"
