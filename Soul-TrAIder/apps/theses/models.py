from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

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
    confidence = models.DecimalField(max_digits=3, decimal_places=2)
    rationale = models.TextField()
    status = models.CharField(max_length=20, default='active', choices=STATUS)

    def __str__(self):
        return f"{self.instrument} - {self.created_date}"
