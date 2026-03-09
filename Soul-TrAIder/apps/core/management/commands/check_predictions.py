from apps.alerts.models import Alert
from apps.marketdata.utils import get_latest_price
from apps.theses.models import Prediction
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Check active predictions against current prices and trigger alerts'

    def handle(self, *args, **options):
        active = Prediction.objects.filter(status='active')
        for pred in active:
            price, _ = get_latest_price(pred.instrument.id)
            if price is None:
                continue
            
            if pred.prediction_type == 'price_target':
                if pred.direction == 'above' and price >= pred.target_value:
                    pred.status = 'hit'
                    pred.save()
                    Alert.objects.create(
                        instrument=pred.instrument,
                        prediction=pred,
                        alert_type='target',
                        threshold=pred.target_value,
                        message=f"{pred.instrument.ticker} hit target {pred.target_value} at {price}"
                    )
                elif pred.direction == 'below' and price <= pred.target_value:
                    pred.status = 'hit'
                    pred.save()
                    Alert.objects.create(...)
        
        self.stdout.write(f"Checked {active.count()} predictions")