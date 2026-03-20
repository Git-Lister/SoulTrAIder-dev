from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models


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
    ACCOUNT_TYPES = [
        ('isa', 'ISA'),
        ('gia', 'General Investment Account'),
        ('sipp', 'SIPP'),
    ]
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPES, default='gia')
    created_at = models.DateTimeField(auto_now_add=True)
    instruments = models.ManyToManyField(Instrument, through='Transaction')

    def __str__(self):
        return f"{self.name} ({self.get_account_type_display()})"

class Transaction(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE)
    buy_date = models.DateField()
    shares = models.DecimalField(max_digits=12, decimal_places=6)
    price_per_share = models.DecimalField(max_digits=10, decimal_places=4)
    fees = models.DecimalField(max_digits=8, decimal_places=4, default=0)
    notes = models.TextField(blank=True)
    thesis = models.ForeignKey('theses.Thesis', on_delete=models.SET_NULL, null=True, blank=True)
    exit_date = models.DateField(null=True, blank=True)
    exit_price = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    exit_reason = models.CharField(max_length=50, choices=[
        ('target', 'Target Hit'),
        ('stop', 'Stop Loss'),
        ('manual', 'Manual'),
    ], blank=True)

    def __str__(self):
        return f"{self.portfolio} - {self.instrument} - {self.buy_date}"


class PortfolioSettings(models.Model):
    portfolio = models.OneToOneField('core.Portfolio', on_delete=models.CASCADE, related_name='settings')
    total_capital = models.DecimalField(max_digits=12, decimal_places=2, help_text="Total capital allocated to this portfolio")
    max_risk_per_trade_pct = models.FloatField(default=2.0, help_text="Maximum % of total capital to risk on a single trade")
    max_sector_allocation_pct = models.FloatField(default=20.0, help_text="Maximum % of total capital in a single sector")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.portfolio.name} settings"


class RiskAllocation(models.Model):
    portfolio = models.ForeignKey('core.Portfolio', on_delete=models.CASCADE, related_name='risk_allocations')
    instrument = models.ForeignKey('core.Instrument', on_delete=models.CASCADE)
    target_allocation_pct = models.FloatField(help_text="Target % of total capital")
    current_allocation_pct = models.FloatField(blank=True, null=True)
    rebalance_threshold = models.FloatField(default=5.0, help_text="Trigger rebalance if deviation exceeds this %")

    class Meta:
        unique_together = ('portfolio', 'instrument')

    def __str__(self):
        return f"{self.portfolio.name} - {self.instrument.ticker}: target {self.target_allocation_pct}%"
