from django.contrib import admin

from .models import Instrument, Portfolio, Transaction


@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'name', 'asset_type', 'currency', 'sector')
    search_fields = ('ticker', 'name')

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('name', 'platform', 'account_type', 'created_at')
    list_filter = ('platform', 'account_type', 'created_at')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'instrument', 'buy_date', 'shares', 'price_per_share', 'exit_date', 'exit_reason', 'thesis')
    list_filter = ('portfolio', 'instrument', 'buy_date', 'exit_reason')
    search_fields = ('portfolio__name', 'instrument__ticker', 'thesis__name')