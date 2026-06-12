import torch

IMAGE_SIZE = 224
CLASSES = ["unedited", "edited"]
DEFAULT_WEIGHTS_URL = "https://example.com/weights.pth"  # Placeholder
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
CACHE_DIR = "~/.crisper_cell_classifier"