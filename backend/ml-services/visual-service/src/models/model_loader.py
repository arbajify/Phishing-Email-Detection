"""Loads and holds the visual models"""
from typing import Optional

from src.config import settings
from src.models.cnn_classifier import CNNBrandClassifier
from src.utils.logger import logger


class ModelLoader:
    def __init__(self):
        self.brand_classifier: Optional[CNNBrandClassifier] = None

    async def load_all_models(self):
        self.brand_classifier = CNNBrandClassifier(
            model_path=settings.cnn_model_path,
            device=settings.inference_device,
        )
        logger.info(f"Visual models loaded: {self.is_loaded()}")

    async def unload_all_models(self):
        self.brand_classifier = None

    def is_loaded(self) -> bool:
        return self.brand_classifier is not None and self.brand_classifier.model is not None


model_loader = ModelLoader()
