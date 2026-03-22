from django.contrib import admin

from .models import EscalationAssessment, EscalationLevel


@admin.register(EscalationLevel)
class EscalationLevelAdmin(admin.ModelAdmin):
    list_display = ('level', 'name', 'probability', 'is_active')
    list_editable = ('probability', 'is_active')


@admin.register(EscalationAssessment)
class EscalationAssessmentAdmin(admin.ModelAdmin):
    list_display = ('date', 'current_level')
