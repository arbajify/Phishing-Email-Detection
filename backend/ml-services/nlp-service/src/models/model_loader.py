"""Loads and holds the NLP models"""
from typing import Optional

from src.config import settings
from src.models.phishing_classifier import PhishingClassifier
from src.models.ai_detector import AIGeneratedDetector
from src.utils.logger import logger


class ModelLoader:
    def __init__(self):
        self.phishing_classifier: Optional[PhishingClassifier] = None
        self.ai_detector: Optional[AIGeneratedDetector] = None

    async def load_all_models(self):
        self.phishing_classifier = PhishingClassifier(
            model_path=settings.phishing_model_path,
            device=settings.inference_device,
            max_length=min(settings.max_sequence_length, 512),
        )
        self.ai_detector = AIGeneratedDetector(
            model_path=settings.ai_detector_model_path,
            device=settings.inference_device,
            max_length=min(settings.max_sequence_length, 512),
        )
        logger.info(f"Models loaded: phishing={self.is_phishing_loaded()}, ai={self.is_ai_loaded()}")

    async def unload_all_models(self):
        self.phishing_classifier = None
        self.ai_detector = None

    def is_phishing_loaded(self) -> bool:
        return self.phishing_classifier is not None and self.phishing_classifier.model is not None

    def is_ai_loaded(self) -> bool:
        return self.ai_detector is not None and self.ai_detector.model is not None

    def is_loaded(self) -> bool:
        return self.is_phishing_loaded() or self.is_ai_loaded()


model_loader = ModelLoader()
