import json
import logging
from typing import List, Optional

from apps.theses.hypothetical import create_trade_from_prediction
from django.utils import timezone

try:
    from apps.core.models import Instrument
except Exception:
    Instrument = None
try:
    from apps.news.models import NewsArticle
except Exception:
    NewsArticle = None
try:
    from apps.theses.models import Prediction
except Exception:
    Prediction = None

logger = logging.getLogger(__name__)


class LLMPredictor:
    def __init__(self, model="llama3", base_url=None):
        self.model = model
        try:
            import ollama
            self.client = ollama.Client(host=base_url) if base_url else ollama
        except ImportError:
            logger.error("ollama library not installed. Please install it.")
            self.client = None

    def get_accuracy_for_instrument(self, instrument):
        """Retrieve recent accuracy stats for LLM-generated predictions for this instrument."""
        try:
            from apps.theses.models import PredictionAccuracy
            acc = PredictionAccuracy.objects.filter(
                instrument=instrument,
                source='llm'
            ).order_by('-date').first()
            if acc and acc.total_predictions > 0:
                return f"Recent prediction accuracy for {instrument.ticker}: {acc.avg_accuracy:.1%} over {acc.total_predictions} predictions."
            else:
                return "No recent accuracy data available."
        except Exception as e:
            logger.exception(f"Error getting accuracy for {instrument}: {e}")
            return "Accuracy data unavailable."

    def build_prompt(self, instrument: Instrument, recent_articles: List[NewsArticle]) -> str:
        articles_text = "\n\n".join([
            f"Title: {a.title}\nPublished: {a.published_at}\nSummary: {a.content[:500]}"
            for a in recent_articles
        ])
        accuracy_info = self.get_accuracy_for_instrument(instrument)
        prompt = f"""
You are a geopolitical investment analyst. Based on recent news, predict the short-term (1-4 week) price movement for {instrument.ticker} ({instrument.name}).

Instrument sector: {instrument.sector}
Thesis context: {getattr(instrument, 'thesis', 'None')}

{accuracy_info}

Recent news:
{articles_text}

Provide a prediction in JSON format with these fields:
- direction: "up", "down", or "neutral"
- confidence: a number between 0.0 and 1.0
- target_price: a numerical target price in {getattr(instrument, 'currency', 'USD')} (optional, only if direction is not neutral)
- timeframe_days: number of days (1-30)
- rationale: a brief explanation
- triggered_by_article_id: the ID of the most relevant article (if any)

Return only the JSON, no other text.
"""
        return prompt

    def predict(self, instrument: Instrument, recent_articles: List[NewsArticle]) -> Optional[dict]:
        if not self.client:
            logger.error("Ollama client not available.")
            return None
        try:
            prompt = self.build_prompt(instrument, recent_articles)
            response = self.client.generate(model=self.model, prompt=prompt)
            # response may be dict-like or string depending on client
            text = response.get('response') if isinstance(response, dict) else str(response)
            if text is None:
                text = ''
            text = text.strip()
            start = text.find('{')
            end = text.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = text[start:end]
                data = json.loads(json_str)
                return data
            else:
                logger.error(f"No JSON found in response: {text}")
                return None
        except Exception as e:
            logger.exception(f"LLM prediction failed for {getattr(instrument, 'ticker', instrument)}: {e}")
            return None

    def generate_predictions_for_all(self, days_lookback=7):
        """Generate predictions for all active instruments using recent news."""
        cutoff = timezone.now() - timezone.timedelta(days=days_lookback)
        articles = NewsArticle.objects.filter(published_at__gte=cutoff).order_by('-published_at')[:50]

        predictions_created = []
        instruments = Instrument.objects.all()
        for instrument in instruments:
            data = self.predict(instrument, articles)
            if data:
                target_date = timezone.now().date() + timezone.timedelta(days=int(data.get('timeframe_days', 14)))
                pred = Prediction.objects.create(
                    instrument=instrument,
                    prediction_type='price_target' if data.get('target_price') else 'direction',
                    direction=data.get('direction', 'neutral'),
                    target_value=data.get('target_price'),
                    confidence=data.get('confidence', 0.5),
                    rationale=data.get('rationale', ''),
                    source='llm',
                    source_detail=self.model,
                    target_date=target_date,
                )
                # optionally set triggered_by_article
                try:
                    aid = data.get('triggered_by_article_id')
                    if aid:
                        article = NewsArticle.objects.filter(id=aid).first()
                        if article:
                            pred.triggered_by_article = article
                            pred.save()
                except Exception:
                    pass
                predictions_created.append(pred)
                # Optionally create a hypothetical trade for this prediction
                try:
                    if data.get('direction') in ['up', 'down'] and data.get('target_price'):
                        try:
                            create_trade_from_prediction(pred, quantity=1)
                        except Exception as e:
                            logger.exception(f"Failed to create hypothetical trade for prediction {pred.id}: {e}")
                except Exception:
                    # swallow any errors related to optional trade creation
                    pass
        return predictions_created
