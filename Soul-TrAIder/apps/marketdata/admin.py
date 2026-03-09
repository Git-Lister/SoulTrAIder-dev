from django.contrib import admin

from .models import DailyPrice


@admin.register(DailyPrice)
class DailyPriceAdmin(admin.ModelAdmin):
    list_display = ('instrument', 'date', 'close', 'volume')
    list_filter = ('instrument', 'date')