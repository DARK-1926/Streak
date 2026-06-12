import os
import numpy as np
import torch
from PIL import Image

def download_weights(url, cache_dir):
    """Simulates downloading weights for reproducibility in this demo."""
    os.makedirs(os.path.expanduser(cache_dir), exist_ok=True)
    weight_path = os.path.join(os.path.expanduser(cache_dir), "model_weights.pth")
    if not os.path.exists(weight_path):
        # Create a dummy weight file for the sake of the demo
        torch.save({"state_dict": {}}, weight_path)
    return weight_path

def create_synthetic_image(size=(512, 512, 3)):
    """Generates a synthetic microscopy-like RGB image."""
    img = np.random.randint(0, 256, size, dtype=np.uint8)
    # Add some 'cells' (blobs)
    for _ in range(5):
        center = np.random.randint(0, size[0], 2)
        rr, cc = np.ogrid[:size[0], :size[1]]
        mask = (rr - center[0])**2 + (cc - center[1])**2 <= 20**2
        img[mask] = [200, 200, 200]
    return img