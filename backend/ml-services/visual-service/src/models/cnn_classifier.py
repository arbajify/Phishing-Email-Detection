"""CNN classifier for visual phishing / brand impersonation"""
import io
import os
from typing import Dict

import torch
import torch.nn as nn
from PIL import Image
from torchvision import transforms

from src.utils.logger import logger


class PhishingCNN(nn.Module):
    """Must match scripts/create_pretrained_model.py"""

    def __init__(self, num_classes: int = 2):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d((7, 7)),
        )
        self.classifier = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(256 * 7 * 7, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(512, num_classes),
        )

    def forward(self, x):
        x = self.features(x)
        x = x.view(x.size(0), -1)
        return self.classifier(x)


class CNNBrandClassifier:
    def __init__(self, model_path: str, device: str = "cpu"):
        self.model_path = model_path
        self.device = device
        self.model = None
        self.trained = False
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        self._load()

    def _weights_file(self) -> str:
        if os.path.isdir(self.model_path):
            return os.path.join(self.model_path, "model.pth")
        return self.model_path

    def _load(self):
        path = self._weights_file()
        if not os.path.exists(path):
            logger.warning(f"CNN model not found at {path}")
            return
        try:
            checkpoint = torch.load(path, map_location=self.device)
            state = checkpoint.get("model_state_dict", checkpoint) if isinstance(checkpoint, dict) else checkpoint
            num_classes = 2
            if isinstance(checkpoint, dict):
                num_classes = checkpoint.get("model_config", {}).get("num_classes", 2)
            model = PhishingCNN(num_classes=num_classes)
            model.load_state_dict(state)
            model.to(self.device)
            model.eval()
            self.model = model
            # Predictions are only trusted if a marker file says the weights were trained
            self.trained = os.path.exists(os.path.join(os.path.dirname(path), "trained.flag"))
            logger.info(f"CNN model loaded (trained={self.trained})")
        except Exception as e:
            logger.warning(f"Could not load CNN model: {e}")
            self.model = None

    def predict(self, screenshot_bytes: bytes) -> Dict:
        if self.model is None or not self.trained:
            return {
                "brand_id": -1,
                "confidence": 0.0,
                "is_impersonation": False,
                "model_loaded": False,
            }
        image = Image.open(io.BytesIO(screenshot_bytes)).convert("RGB")
        tensor = self.transform(image).unsqueeze(0).to(self.device)
        with torch.no_grad():
            probs = torch.softmax(self.model(tensor), dim=-1)[0]
        cls = int(torch.argmax(probs))
        conf = float(probs[cls])
        return {
            "brand_id": cls,
            "confidence": conf,
            "is_impersonation": cls == 1 and conf > 0.5,
            "model_loaded": True,
        }
