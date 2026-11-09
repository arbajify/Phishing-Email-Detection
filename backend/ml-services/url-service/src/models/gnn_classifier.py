"""Domain GNN classifier wrapper"""
import os
import sys
from typing import Dict

import torch
import torch.nn as nn

from src.utils.logger import logger


class DomainGNN(nn.Module):
    """Must match the architecture saved by scripts/create_gnn_model.py"""

    def __init__(self, in_channels: int = 8, hidden_channels: int = 32, num_classes: int = 2):
        super().__init__()
        self.mlp = nn.Sequential(
            nn.Linear(in_channels, hidden_channels),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_channels, hidden_channels),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_channels, num_classes),
        )

    def forward(self, data):
        x = data.x
        if x.dim() == 1:
            x = x.unsqueeze(0)
        h = x.mean(dim=0, keepdim=True)
        return self.mlp(h)


class DomainGNNClassifier:
    """Loads the domain model and predicts malicious probability."""

    def __init__(self, model_path: str, device: str = "cpu"):
        self.model_path = model_path
        self.device = device
        self.model = None
        self.trained = False
        self._load()

    def _weights_file(self) -> str:
        if os.path.isdir(self.model_path):
            return os.path.join(self.model_path, "model.pth")
        return self.model_path

    def _load(self):
        path = self._weights_file()
        if not os.path.exists(path):
            logger.warning(f"GNN model not found at {path}. Running without it.")
            return
        try:
            # The setup script pickled the whole model from __main__,
            # so the class must be visible there for torch.load to work.
            main_module = sys.modules.get("__main__")
            if main_module is not None and not hasattr(main_module, "DomainGNN"):
                setattr(main_module, "DomainGNN", DomainGNN)

            loaded = torch.load(path, map_location=self.device)
            if isinstance(loaded, nn.Module):
                model = loaded
            else:
                model = DomainGNN()
                model.load_state_dict(loaded.get("model_state_dict", loaded))
            model.to(self.device)
            model.eval()
            self.model = model
            # Only trust predictions if a trained model was saved with a marker file
            self.trained = os.path.exists(
                os.path.join(os.path.dirname(path), "trained.flag")
            )
            logger.info(f"GNN model loaded (trained={self.trained})")
        except Exception as e:
            logger.warning(f"Could not load GNN model: {e}")
            self.model = None

    def predict(self, graph_data) -> Dict:
        # Neutral output if the model is missing or still untrained
        if self.model is None or not self.trained:
            return {"malicious_probability": 0.5, "legitimate_probability": 0.5}
        with torch.no_grad():
            logits = self.model(graph_data.to(self.device))
            probs = torch.softmax(logits, dim=-1)[0]
        return {
            "legitimate_probability": float(probs[0]),
            "malicious_probability": float(probs[1]),
        }
