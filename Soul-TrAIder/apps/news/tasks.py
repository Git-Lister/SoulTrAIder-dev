import logging

from celery import shared_task

from .llm_predictor import LLMPredictor

logger = logging.getLogger(__name__)


@shared_task
def generate_llm_predictions():
    """Celery task to generate LLM predictions."""
    predictor = LLMPredictor()
    preds = predictor.generate_predictions_for_all()
    logger.info(f"Generated {len(preds)} LLM predictions")
    return f"Generated {len(preds)} predictions"
