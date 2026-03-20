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


class TechnicalIndicator(models.Model):
    instrument = models.ForeignKey('core.Instrument', on_delete=models.CASCADE)
    date = models.DateField()
    rsi = models.FloatField(null=True, blank=True)
    sma_20 = models.FloatField(null=True, blank=True)
    sma_50 = models.FloatField(null=True, blank=True)
    volume = models.BigIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('instrument', 'date')

    def __str__(self):
        return f"{self.instrument.ticker} - {self.date}"


class CorrelationMatrix(models.Model):
    date = models.DateField(auto_now_add=True)
    matrix = models.JSONField(help_text="Correlation coefficients between instruments")
    method = models.CharField(max_length=20, default='pearson')
    period_days = models.IntegerField(default=90)

    def __str__(self):
        return f"Correlation as of {self.date} ({self.method}, {self.period_days}d)"
