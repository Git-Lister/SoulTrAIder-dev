from django.contrib import admin

from .models import Prediction, Thesis, ThesisInstrument


@admin.register(Thesis)
class ThesisAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'created_at')

@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ('instrument', 'created_date', 'target_date', 'prediction_type', 'status')
    list_filter = ('status', 'instrument')