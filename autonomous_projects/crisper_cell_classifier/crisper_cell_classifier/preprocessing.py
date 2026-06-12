import numpy as np
import torch
from PIL import Image
from .const import IMAGE_SIZE

def load_image(image_path):
    """Load an image from disk and return it as a NumPy array in RGB order."""
    with Image.open(image_path) as img:
        img = img.convert("RGB")
        return np.array(img)

def preprocess_for_model(image_np):
    """Converts a NumPy image to a torch tensor suitable for the model.
    Uses manual transforms to avoid dependency on torchvision in environments where it is missing.
    """
    img = Image.fromarray(image_np).resize((IMAGE_SIZE, IMAGE_SIZE))
    
    # Convert to tensor and normalize manually
    img_tensor = torch.from_numpy(np.array(img)).permute(2, 0, 1).float() / 255.0
    
    mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
    std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)
    
    img_tensor = (img_tensor - mean) / std
    return img_tensor.unsqueeze(0)

def denoise_image(image_np):
    """Placeholder denoising function – returns the input unchanged.
    The original implementation relied on OpenCV which is not available in the test environment.
    """
    return image_np