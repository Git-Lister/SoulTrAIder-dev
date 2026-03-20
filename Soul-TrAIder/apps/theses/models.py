from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Thesis(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class ThesisInstrument(models.Model):
    thesis = models.ForeignKey(Thesis, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to={'model__in': ['instrument']})
    object_id = models.PositiveIntegerField()
    instrument = GenericForeignKey('content_type', 'object_id')
    weight = models.FloatField(default=1.0)

class Prediction(models.Model):
    SOURCE_TYPES = [
        ('user', 'User-Defined'),
        ('llm', 'LLM-Generated'),
        ('hybrid', 'Hybrid'),
    ]
    PREDICTION_TYPES = [
        ('price_target', 'Price Target'),
        ('event', 'Event'),
    ]
    DIRECTION = [
        ('above', 'Above'),
        ('below', 'Below'),
    ]
    STATUS = [
        ('active', 'Active'),
        ('hit', 'Hit'),
        ('missed', 'Missed'),
        ('expired', 'Expired'),
    ]
    thesis = models.ForeignKey(Thesis, on_delete=models.CASCADE, null=True, blank=True)
    instrument = models.ForeignKey('core.Instrument', on_delete=models.CASCADE)
    created_date = models.DateField(auto_now_add=True)
    target_date = models.DateField(null=True, blank=True)
    prediction_type = models.CharField(max_length=20, choices=PREDICTION_TYPES)
    direction = models.CharField(max_length=10, choices=DIRECTION, blank=True)
    target_value = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    source = models.CharField(max_length=10, choices=SOURCE_TYPES, default='user')
    source_detail = models.CharField(max_length=100, blank=True)
    triggered_by_article = models.ForeignKey('news.NewsArticle', on_delete=models.SET_NULL, null=True, blank=True)
    actual_outcome_value = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    confidence = models.DecimalField(max_digits=3, decimal_places=2)
    rationale = models.TextField()
    accuracy_score = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=20, default='active', choices=STATUS)

    def __str__(self):
        return f"{self.instrument} - {self.created_date}"

    def evaluate(self, actual_price):
        """Evaluate prediction against an actual price.

        - Only evaluates if status is 'active'.
        - Sets `actual_outcome_value` and updates `status` and `accuracy_score`.
        """
        if self.status != 'active':
            return

        # store actual observed value
        self.actual_outcome_value = actual_price

        if self.prediction_type == 'price_target' and self.target_value is not None:
            # support both 'up'/'down' and existing 'above'/'below' direction values
            dir_val = (self.direction or '').lower()
            is_up = dir_val in ('up', 'above')
            is_down = dir_val in ('down', 'below')

            try:
                actual = float(actual_price)
                target = float(self.target_value)
            except Exception:
                # if conversion fails, save the observed value and return
                self.save()
                return

            if is_up and actual >= target:
                self.status = 'hit'
                self.accuracy_score = 1.0
            elif is_down and actual <= target:
                self.status = 'hit'
                self.accuracy_score = 1.0
            else:
                self.status = 'missed'
                if is_up:
                    if target != 0:
                        self.accuracy_score = min(actual / target, 1.0)
                    else:
                        self.accuracy_score = 0.0
                elif is_down:
                    if actual != 0:
                        self.accuracy_score = min(target / actual, 1.0)
                    else:
                        self.accuracy_score = 0.0

        self.save()


class PredictionAccuracy(models.Model):
    instrument = models.ForeignKey('core.Instrument', on_delete=models.CASCADE)
    source = models.CharField(max_length=10, choices=Prediction.SOURCE_TYPES)
    date = models.DateField(auto_now_add=True)
    total_predictions = models.IntegerField(default=0)
    hits = models.IntegerField(default=0)
    avg_confidence = models.FloatField(null=True, blank=True)
    avg_accuracy = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ('instrument', 'source', 'date')

    def __str__(self):
        return f"{self.instrument} - {self.source} - {self.date}"


class HypotheticalTrade(models.Model):
    thesis = models.ForeignKey('theses.Thesis', on_delete=models.CASCADE)
    instrument = models.ForeignKey('core.Instrument', on_delete=models.CASCADE)
    entry_date = models.DateField()
    entry_price = models.DecimalField(max_digits=10, decimal_places=4)
    quantity = models.DecimalField(max_digits=12, decimal_places=6)
    direction = models.CharField(max_length=4, choices=[('long', 'Long'), ('short', 'Short')])
    exit_date = models.DateField(null=True, blank=True)
    exit_price = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    prediction = models.ForeignKey(Prediction, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=10, default='open', choices=[('open', 'Open'), ('closed', 'Closed')])
    profit_loss = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)

    def __str__(self):
        return f"{self.instrument} - {self.entry_date} - {self.status}"
