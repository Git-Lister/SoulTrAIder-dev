from django.shortcuts import render
from django.http import HttpResponse
from apps.core.models import Transaction, Instrument
from apps.marketdata.utils import get_latest_price

def index(request):
    portfolios = Transaction.objects.values('portfolio__name').distinct()
    return render(request, 'dashboard/index.html', {'portfolios': portfolios})

def holdings(request):
    transactions = Transaction.objects.select_related('instrument', 'portfolio').all()
    return render(request, 'dashboard/holdings.html', {'transactions': transactions})

def predictions(request):
    return render(request, 'dashboard/predictions.html')

def news(request):
    return render(request, 'dashboard/news.html')

def holdings_table(request):
    transactions = Transaction.objects.select_related('instrument', 'portfolio').all()
    return render(request, 'dashboard/partials/holdings_table.html', {'transactions': transactions})

def price_update(request, instrument_id):
    instrument = Instrument.objects.get(id=instrument_id)
    price = get_latest_price(instrument.ticker)
    if price is None:
        price = 'N/A'
    return HttpResponse(f"{price} {instrument.currency}")
