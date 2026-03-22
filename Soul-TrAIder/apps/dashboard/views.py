from decimal import Decimal

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from apps.core.models import Instrument, Transaction
from apps.marketdata.utils import fetch_live_price, get_latest_price
from apps.theses.models import HypotheticalTrade, Prediction, PredictionAccuracy


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

def predictions_llm(request):
    """Show LLM-generated predictions."""
    predictions = Prediction.objects.filter(source='llm').order_by('-created_date')
    return render(request, 'dashboard/predictions_llm.html', {'predictions': predictions})


def accuracy_stats(request):
    """Show per-instrument accuracy stats."""
    stats = PredictionAccuracy.objects.all().order_by('-date', 'instrument__ticker')
    return render(request, 'dashboard/accuracy_stats.html', {'stats': stats})


def hypothetical_portfolio(request):
    """Show hypothetical trades (open and closed)."""
    trades = HypotheticalTrade.objects.select_related('instrument', 'thesis', 'prediction').order_by('-entry_date')
    return render(request, 'dashboard/hypothetical_portfolio.html', {'trades': trades})


def trading_journal(request):
    transactions = Transaction.objects.select_related('instrument', 'portfolio', 'thesis').order_by('-buy_date')
    # Compute win rate (closed trades with exit_reason='target')
    closed_trades = transactions.filter(exit_reason__isnull=False)
    total_closed = closed_trades.count()
    wins = closed_trades.filter(exit_reason='target').count()
    win_rate = (wins / total_closed * 100) if total_closed else 0
    context = {
        'transactions': transactions,
        'win_rate': win_rate,
        'total_closed': total_closed,
        'wins': wins,
    }
    return render(request, 'dashboard/trading_journal.html', context)

def portfolio_value(request):
    """Return total portfolio value and breakdown (for charts later)."""
    # Implementation for future charting
    pass