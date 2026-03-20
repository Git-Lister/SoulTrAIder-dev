import logging
from decimal import Decimal

from celery import shared_task
from django.db.models import Sum

from apps.core.models import Instrument, Portfolio, RiskAllocation, Transaction
from apps.marketdata.models import DailyPrice

logger = logging.getLogger(__name__)


@shared_task
def check_risk_allocation():
    """
    For each portfolio with settings, calculate current allocation per instrument and per sector.
    Compare to target allocations and thresholds. Log warnings if exceeded.
    """
    portfolios = Portfolio.objects.all()
    for portfolio in portfolios:
        settings = getattr(portfolio, 'settings', None)
        if not settings:
            continue

        # Calculate current total portfolio value
        # Sum all transactions: shares * current price (need latest price)
        # For simplicity, we'll use the latest price from DailyPrice.
        instruments = Instrument.objects.all()
        current_values = {}
        total_value = Decimal('0')
        for inst in instruments:
            latest_price = DailyPrice.objects.filter(instrument=inst).order_by('-date').first()
            if latest_price:
                # Get total shares from transactions for this portfolio and instrument
                total_shares = Transaction.objects.filter(portfolio=portfolio, instrument=inst).aggregate(
                    total=Sum('shares')
                )['total'] or Decimal('0')
                value = total_shares * latest_price.close
                current_values[inst.id] = value
                total_value += value

        if total_value == 0:
            continue

        # Check per-instrument allocations
        allocations = RiskAllocation.objects.filter(portfolio=portfolio)
        for alloc in allocations:
            current_val = current_values.get(alloc.instrument.id, Decimal('0'))
            current_pct = float((current_val / total_value) * 100) if total_value else 0
            alloc.current_allocation_pct = current_pct
            alloc.save(update_fields=['current_allocation_pct'])

            deviation = abs(current_pct - alloc.target_allocation_pct)
            if deviation > alloc.rebalance_threshold:
                logger.warning(
                    f"Portfolio {portfolio.name}: {alloc.instrument.ticker} allocation {current_pct:.1f}% "
                    f"deviates from target {alloc.target_allocation_pct:.1f}% by {deviation:.1f}% "
                    f"(threshold {alloc.rebalance_threshold}%)"
                )

        # Optionally check sector allocations (requires sector mapping)
        # For now, we skip sector-level checks.

    return "Risk allocation check completed"


@shared_task
def generate_rebalance_suggestions():
    """
    For each portfolio with risk allocations, compute current allocations and
    create RebalanceSuggestion records when deviation exceeds threshold.
    """
    from apps.alerts.models import RebalanceSuggestion
    from apps.core.models import Portfolio, RiskAllocation, Transaction
    from apps.marketdata.models import DailyPrice
    suggestions_created = 0

    portfolios = Portfolio.objects.all()
    for portfolio in portfolios:
        settings = getattr(portfolio, 'settings', None)
        if not settings:
            continue

        instruments = Instrument.objects.all()
        current_values = {}
        total_value = Decimal('0')
        for inst in instruments:
            latest_price = DailyPrice.objects.filter(instrument=inst).order_by('-date').first()
            if latest_price:
                total_shares = Transaction.objects.filter(portfolio=portfolio, instrument=inst).aggregate(
                    total=Sum('shares')
                )['total'] or Decimal('0')
                value = total_shares * latest_price.close
                current_values[inst.id] = value
                total_value += value

        if total_value == 0:
            continue

        allocations = RiskAllocation.objects.filter(portfolio=portfolio)
        for alloc in allocations:
            current_val = current_values.get(alloc.instrument.id, Decimal('0'))
            current_pct = float((current_val / total_value) * 100) if total_value else 0
            alloc.current_allocation_pct = current_pct
            alloc.save(update_fields=['current_allocation_pct'])

            deviation = abs(current_pct - alloc.target_allocation_pct)
            if deviation > alloc.rebalance_threshold:
                # Determine suggested action
                if current_pct > alloc.target_allocation_pct:
                    # sell
                    target_pct = Decimal(str(alloc.target_allocation_pct / 100))
                    target_val = target_pct * total_value
                    excess = current_val - target_val
                    latest_price = DailyPrice.objects.filter(instrument=alloc.instrument).order_by('-date').first()
                    if latest_price and latest_price.close > 0:
                        qty = (excess / latest_price.close).quantize(Decimal('0.000001'))
                        if qty > 0:
                            RebalanceSuggestion.objects.create(
                                portfolio=portfolio,
                                instrument=alloc.instrument,
                                current_allocation=current_pct,
                                target_allocation=alloc.target_allocation_pct,
                                suggested_action='sell',
                                suggested_quantity=qty
                            )
                            suggestions_created += 1
                else:
                    # buy
                    target_pct = Decimal(str(alloc.target_allocation_pct / 100))
                    deficit = target_pct * total_value - current_val
                    latest_price = DailyPrice.objects.filter(instrument=alloc.instrument).order_by('-date').first()
                    if latest_price and latest_price.close > 0:
                        qty = (deficit / latest_price.close).quantize(Decimal('0.000001'))
                        if qty > 0:
                            RebalanceSuggestion.objects.create(
                                portfolio=portfolio,
                                instrument=alloc.instrument,
                                current_allocation=current_pct,
                                target_allocation=alloc.target_allocation_pct,
                                suggested_action='buy',
                                suggested_quantity=qty
                            )
                            suggestions_created += 1

    logger.info(f"Generated {suggestions_created} rebalance suggestions")
    return f"Generated {suggestions_created} rebalance suggestions"
