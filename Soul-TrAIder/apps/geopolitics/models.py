from django.db import models


class EscalationLevel(models.Model):
    level = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    key_triggers = models.TextField(help_text="Events that would trigger this level")
    expected_market_impact = models.TextField()
    probability = models.FloatField(default=0.0, help_text="Current estimated probability (0-1)")
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ['level']

    def __str__(self):
        return f"Level {self.level}: {self.name}"


class EscalationAssessment(models.Model):
    date = models.DateField(auto_now_add=True)
    current_level = models.ForeignKey(EscalationLevel, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    # Optional: link to news articles that prompted this assessment
    articles = models.ManyToManyField('news.NewsArticle', blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Assessment {self.date} - Level {self.current_level.level if self.current_level else '?'}"
