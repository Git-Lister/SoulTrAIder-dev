from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

class Instrument(models.Model):
    ASSET_TYPES = [
        ('stock', 'Stock'),
        ('etf', 'ETF'),
        ('bond', 'Bond'),
        ('crypto', 'Cryptocurrency'),
    ]
    ticker = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPES)
    currency = models.CharField(max_length=3)  # e.g., 'GBP', 'USD'
    sector = models.CharField(max_length=50, blank=True)
    thesis = models.TextField(blank=True, help_text="Why you're interested in this instrument")

    def __str__(self):
        return f"{self.ticker} - {self.name}"

class Portfolio(models.Model):
    name = models.CharField(max_length=50)
    platform = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    instruments = models.ManyToManyField(Instrument, through='Transaction')

    def __str__(self):
        return self.name

class Transaction(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE)
    buy_date = models.DateField()
    shares = models.DecimalField(max_digits=12, decimal_places=6)
    price_per_share = models.DecimalField(max_digits=10, decimal_places=4)
    fees = models.DecimalField(max_digits=8, decimal_places=4, default=0)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.portfolio} - {self.instrument} - {self.buy_date}"
