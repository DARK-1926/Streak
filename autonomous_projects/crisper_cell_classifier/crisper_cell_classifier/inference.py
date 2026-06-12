import torch
import numpy as np
from PIL import Image
from .model import CRISPRCellModel
from .preprocessing import load_image, preprocess_for_model
from .const import CLASSES, DEFAULT_WEIGHTS_URL, CACHE_DIR, DEVICE

_MODEL_INSTANCE = None

def _get_model():
    global _MODEL_INSTANCE
    if _MODEL_INSTANCE is None:
        _MODEL_INSTANCE = CRISPRCellModel(DEFAULT_WEIGHTS_URL, CACHE_DIR)
    return _MODEL_INSTANCE

def _resize_heatmap(heatmap, target_width, target_height):
    """Resize a 2D heatmap to the given dimensions using PIL for compatibility.
    The heatmap is a NumPy array with values in arbitrary range.
    """
    # Convert to 8-bit image for resizing, then back to float
    heatmap_img = Image.fromarray((heatmap * 255).astype('uint8'))
    heatmap_resized = heatmap_img.resize((target_width, target_height), resample=Image.BILINEAR)
    return np.array(heatmap_resized).astype('float32') / 255.0

def predict(image_path):
    """High-level API to predict cell state.
    Returns a dict with label, probability and a heatmap matching the original image size.
    """
    model = _get_model()
    original_img = load_image(image_path)
    h, w, _ = original_img.shape
    
    input_tensor = preprocess_for_model(original_img).to(DEVICE)
    
    with torch.no_grad():
        logits, feat_map = model(input_tensor)
        probs = torch.softmax(logits, dim=1).cpu().numpy()[0]
    
    max_idx = np.argmax(probs)
    
    # Generate a heatmap by upsampling the dummy feature map to original image size
    heatmap = feat_map.cpu().numpy()[0, 0]
    heatmap = _resize_heatmap(heatmap, w, h)
    # Normalize to [0,1]
    heatmap = (heatmap - heatmap.min()) / (heatmap.max() - heatmap.min() + 1e-8)

    return {
        "label": CLASSES[max_idx],
        "probability": float(probs[max_idx]),
        "heatmap": heatmap
    }