from django.db import models
from django.contrib.postgres.fields import ArrayField
from apps.core.models import Instrument

class NewsArticle(models.Model):
    source = models.CharField(max_length=100)
    title = models.CharField(max_length=500)
    url = models.URLField(unique=True)
    published_at = models.DateTimeField()
    fetched_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField(blank=True)
    keywords = ArrayField(models.CharField(max_length=50), blank=True, default=list)

    def __str__(self):
        return self.title

class NewsImpact(models.Model):
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE)
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE)
    sentiment = models.DecimalField(max_digits=3, decimal_places=2)  # -1 to 1
    summary = models.TextField()
    relevant = models.BooleanField(default=True)
    analyzed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('article', 'instrument')
