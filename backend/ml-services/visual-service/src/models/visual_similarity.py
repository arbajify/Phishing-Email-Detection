"""Screenshot similarity comparison"""
import io
from typing import Dict, List

import numpy as np
from PIL import Image


class VisualSimilarity:
    """Compare two screenshots using pixel difference on downscaled images."""

    SIZE = (128, 128)

    def _to_array(self, data: bytes) -> np.ndarray:
        img = Image.open(io.BytesIO(data)).convert("L").resize(self.SIZE)
        return np.asarray(img, dtype=np.float32) / 255.0

    def compare(self, image1: bytes, image2: bytes) -> Dict:
        a = self._to_array(image1)
        b = self._to_array(image2)
        diff = np.abs(a - b)
        score = float(1.0 - diff.mean())

        differences: List[Dict] = []
        h, w = diff.shape
        grid = 4
        for gy in range(grid):
            for gx in range(grid):
                block = diff[gy * h // grid:(gy + 1) * h // grid,
                             gx * w // grid:(gx + 1) * w // grid]
                if block.mean() > 0.25:
                    differences.append({
                        "region": f"row{gy}_col{gx}",
                        "difference": round(float(block.mean()), 3),
                    })

        return {"similarity_score": round(score, 4), "differences": differences}
