from django.contrib import admin

from .models import Instrument, Portfolio, Transaction


@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'name', 'asset_type', 'currency', 'sector')
    search_fields = ('ticker', 'name')

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('name', 'platform', 'created_at')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'instrument', 'buy_date', 'shares', 'price_per_share')
    list_filter = ('portfolio', 'instrument', 'buy_date')