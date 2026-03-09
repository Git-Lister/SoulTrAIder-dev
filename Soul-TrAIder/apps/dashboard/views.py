from decimal import Decimal

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from apps.core.models import Instrument, Transaction
from apps.marketdata.utils import fetch_live_price, get_latest_price


def index(request):
    portfolios = Transaction.objects.values('portfolio__name').distinct()
    return render(request, 'dashboard/index.html', {'portfolios': portfolios})

def holdings(request):
    transactions = Transaction.objects.select_related('instrument', 'portfolio').all()
    return render(request, 'dashboard/holdings.html', {'transactions': transactions})

def holdings_table(request):
    transactions = Transaction.objects.select_related('instrument', 'portfolio').all()
    return render(request, 'dashboard/partials/holdings_table.html', {'transactions': transactions})

def price_update(request, instrument_id):
    """
    Return current price for an instrument.
    First try stored daily price, fallback to live.
    """
    instrument = Instrument.objects.get(id=instrument_id)
    price, price_date = get_latest_price(instrument_id)
    source = 'stored'
    
    if price is None:
        price = fetch_live_price(instrument.ticker)
        source = 'live'
    
    if price is None:
        return HttpResponse("N/A")
    
    # Calculate current value and return for this transaction
    transactions = Transaction.objects.filter(instrument=instrument)
    response_data = {
        'price': f"{price:.2f} {instrument.currency}",
        'source': source,
        'date': price_date.strftime('%Y-%m-%d') if price_date else 'today',
    }
    
    # If this is an HTMX request, return a simple string
    if request.headers.get('HX-Request'):
        return HttpResponse(f"{price:.2f} {instrument.currency}")
    
    return JsonResponse(response_data)

def portfolio_value(request):
    """Return total portfolio value and breakdown (for charts later)."""
    # Implementation for future charting
    pass