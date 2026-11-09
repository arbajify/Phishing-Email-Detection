"""Transformer-based phishing text classifier"""
import os
from typing import Dict

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from src.utils.logger import logger


class PhishingClassifier:
    def __init__(self, model_path: str, device: str = "cpu", max_length: int = 256):
        self.model_path = model_path
        self.device = device
        self.max_length = max_length
        self.model = None
        self.tokenizer = None
        self.phishing_index = 1
        self._load()

    def _load(self):
        if not os.path.isdir(self.model_path):
            logger.warning(f"Phishing model not found at {self.model_path}")
            return
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_path)
            self.model.to(self.device)
            self.model.eval()
            id2label = getattr(self.model.config, "id2label", {}) or {}
            for idx, name in id2label.items():
                if any(k in str(name).lower() for k in ("phish", "spam", "malicious")):
                    self.phishing_index = int(idx)
            logger.info(f"Phishing model loaded from {self.model_path}")
        except Exception as e:
            logger.warning(f"Could not load phishing model: {e}")
            self.model = None
            self.tokenizer = None

    def predict(self, text: str) -> Dict:
        if self.model is None or self.tokenizer is None:
            return {
                "phishing_probability": 0.0,
                "legitimate_probability": 1.0,
                "confidence": 0.0,
                "prediction": "unknown",
            }
        inputs = self.tokenizer(
            text, truncation=True, max_length=self.max_length,
            padding=True, return_tensors="pt",
        ).to(self.device)
        with torch.no_grad():
            probs = torch.softmax(self.model(**inputs).logits, dim=-1)[0]
        phishing = float(probs[self.phishing_index])
        legitimate = 1.0 - phishing
        return {
            "phishing_probability": phishing,
            "legitimate_probability": legitimate,
            "confidence": abs(phishing - legitimate),
            "prediction": "phishing" if phishing > 0.5 else "legitimate",
        }
