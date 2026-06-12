import json
import pathlib
from typing import List, Dict
import torch
from PIL import Image
from .preprocess import transform

class DummyNet(torch.nn.Module):
    """Very small network that returns deterministic logits for demonstration.
    In a real system this would be replaced by a TorchScript model loaded from disk.
    """
    def __init__(self, num_classes: int = 6):
        super().__init__()
        self.linear = torch.nn.Linear(224 * 224 * 3, num_classes)
        # Initialise weights to produce a predictable output (all zeros -> equal probs)
        torch.nn.init.constant_(self.linear.weight, 0.0)
        torch.nn.init.constant_(self.linear.bias, 0.0)

    def forward(self, x):
        # x shape: (B, C, H, W)
        x = x.view(x.size(0), -1)
        return self.linear(x)

class Detector:
    """Singleton‑style wrapper around the model.
    Provides a simple ``predict`` method used by the Flask routes and tests.
    """
    _model = None
    _categories = None
    _device = torch.device('cpu')

    def __init__(self, model_path: str = None, categories_path: str = None):
        # Load categories mapping
        base_dir = pathlib.Path(__file__).parent
        cat_path = pathlib.Path(categories_path) if categories_path else base_dir / 'categories.json'
        with open(cat_path, 'r') as f:
            self._categories = json.load(f)

        # Load model – if a TorchScript file is supplied we attempt to load it,
        # otherwise we fall back to the DummyNet defined above.
        if model_path and pathlib.Path(model_path).exists():
            try:
                self._model = torch.jit.load(model_path, map_location=self._device)
            except Exception:
                # If loading fails we still want the app to start; fall back.
                self._model = DummyNet(num_classes=len(self._categories)).to(self._device)
        else:
            self._model = DummyNet(num_classes=len(self._categories)).to(self._device)
        self._model.eval()

    def predict(self, image: Image.Image, top_k: int = 3) -> List[Dict]:
        """Run inference on a PIL image and return top‑k predictions.
        Returns a list of dicts: ``[{"label": str, "confidence": float}, ...]``.
        """
        with torch.no_grad():
            tensor = transform(image).unsqueeze(0).to(self._device)  # (1, C, H, W)
            logits = self._model(tensor)
            probs = torch.softmax(logits, dim=1).squeeze(0)  # (num_classes,)
            top_probs, top_idx = torch.topk(probs, k=min(top_k, probs.size(0)))
            results = []
            for prob, idx in zip(top_probs.tolist(), top_idx.tolist()):
                label = self._categories.get(str(idx), 'unknown')
                results.append({"label": label, "confidence": prob})
            return results
