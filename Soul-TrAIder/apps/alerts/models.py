from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

from apps.core.models import Instrument
from apps.theses.models import Prediction


class Alert(models.Model):
    ALERT_TYPES = [
        ('target', 'Target'),
        ('stop_loss', 'Stop Loss'),
        ('news', 'News'),
    ]
    STATUS = [
        ('active', 'Active'),
        ('hit', 'Hit'),
        ('missed', 'Missed'),
        ('expired', 'Expired'),
    ]
    SOURCE_TYPES = [
        ('user', 'User-Defined'),
        ('llm', 'LLM-Generated'),
        ('hybrid', 'Hybrid'),
    ]

    thesis = models.ForeignKey(Thesis, on_delete=models.CASCADE, null=True, blank=True)
    instrument = models.ForeignKey('core.Instrument', on_delete=models.CASCADE)
    created_date = models.DateField(auto_now_add=True)
    target_date = models.DateField(null=True, blank=True)
    prediction_type = models.CharField(max_length=20, choices=PREDICTION_TYPES)
    direction = models.CharField(max_length=10, choices=DIRECTION, blank=True)
    target_value = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    confidence = models.DecimalField(max_digits=3, decimal_places=2)  # 0.00 to 1.00
    rationale = models.TextField()
    status = models.CharField(max_length=20, default='active', choices=STATUS)

    # New fields
    source = models.CharField(max_length=10, choices=SOURCE_TYPES, default='user')
    source_detail = models.CharField(max_length=100, blank=True)  # e.g., 'llama3-8b', 'prompt-v2'
    triggered_by_article = models.ForeignKey('news.NewsArticle', on_delete=models.SET_NULL, null=True, blank=True)
    actual_outcome_value = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    accuracy_score = models.FloatField(null=True, blank=True)

    def evaluate(self, actual_price):
        """Update status based on actual price."""
        if self.status != 'active':
            return
        self.actual_outcome_value = actual_price
        if self.prediction_type == 'price_target' and self.target_value is not None:
            if self.direction == 'up' and actual_price >= self.target_value:
                self.status = 'hit'
                self.accuracy_score = 1.0
            elif self.direction == 'down' and actual_price <= self.target_value:
                self.status = 'hit'
                self.accuracy_score = 1.0
            else:
                self.status = 'missed'
                # Calculate partial accuracy (how close it got)
                if self.direction == 'up':
                    self.accuracy_score = min(float(actual_price) / float(self.target_value), 1.0)
                else:
                    self.accuracy_score = min(float(self.target_value) / float(actual_price), 1.0)
        elif self.prediction_type == 'direction':
            # For direction-only, we need start price – we'll handle in evaluation task
            pass
        self.save()

    def __str__(self):
        return f"{self.instrument} - {self.alert_type}"


class RebalanceSuggestion(models.Model):
    portfolio = models.ForeignKey('core.Portfolio', on_delete=models.CASCADE)
    instrument = models.ForeignKey('core.Instrument', on_delete=models.CASCADE)
    current_allocation = models.FloatField()
    target_allocation = models.FloatField()
    suggested_action = models.CharField(max_length=10, choices=[('buy', 'Buy'), ('sell', 'Sell')])
    suggested_quantity = models.DecimalField(max_digits=12, decimal_places=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.portfolio.name} - {self.instrument.ticker}: {self.suggested_action} {self.suggested_quantity}"
