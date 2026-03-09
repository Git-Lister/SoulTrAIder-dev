from django.contrib import admin

from .models import Alert


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('instrument', 'alert_type', 'threshold', 'triggered')
    list_filter = ('alert_type', 'triggered')