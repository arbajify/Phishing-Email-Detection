"""AI-generated text detector"""
import os
from typing import Dict

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from src.utils.logger import logger


class AIGeneratedDetector:
    def __init__(self, model_path: str, device: str = "cpu", max_length: int = 256):
        self.model_path = model_path
        self.device = device
        self.max_length = max_length
        self.model = None
        self.tokenizer = None
        self.ai_index = 1
        self._load()

    def _load(self):
        if not os.path.isdir(self.model_path):
            logger.warning(f"AI detector model not found at {self.model_path}")
            return
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_path)
            self.model.to(self.device)
            self.model.eval()
            id2label = getattr(self.model.config, "id2label", {}) or {}
            for idx, name in id2label.items():
                if any(k in str(name).lower() for k in ("ai", "fake", "generated", "machine")):
                    self.ai_index = int(idx)
            logger.info(f"AI detector loaded from {self.model_path}")
        except Exception as e:
            logger.warning(f"Could not load AI detector: {e}")
            self.model = None
            self.tokenizer = None

    def detect(self, text: str) -> Dict:
        if self.model is None or self.tokenizer is None:
            return {
                "ai_generated_probability": 0.0,
                "human_written_probability": 1.0,
                "is_ai_generated": False,
                "confidence": 0.0,
                "model_loaded": False,
            }
        inputs = self.tokenizer(
            text, truncation=True, max_length=self.max_length,
            padding=True, return_tensors="pt",
        ).to(self.device)
        with torch.no_grad():
            probs = torch.softmax(self.model(**inputs).logits, dim=-1)[0]
        ai = float(probs[self.ai_index])
        human = 1.0 - ai
        return {
            "ai_generated_probability": ai,
            "human_written_probability": human,
            "is_ai_generated": ai > 0.5,
            "confidence": abs(ai - human),
            "model_loaded": True,
        }
