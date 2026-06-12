import torch
import torch.nn as nn
import torchvision.models as models
from .const import DEVICE, IMAGE_SIZE
from .utils import download_weights

class CRISPRCellModel(nn.Module):
    def __init__(self, weights_url, cache_dir):
        super().__init__()
        # Use EfficientNet_B0 as a lightweight backbone
        self.backbone = models.efficientnet_b0(weights=None)
        # Adjust head for 2 classes
        in_features = self.backbone.classifier[1].in_features
        self.backbone.classifier[1] = nn.Linear(in_features, 2)
        
        weight_path = download_weights(weights_url, cache_dir)
        # In a real scenario, we would load state_dict
        # self.load_state_dict(torch.load(weight_path, map_location=DEVICE)['state_dict'])
        self.to(DEVICE)
        self.eval()

    def forward(self, x):
        # Return logits and a dummy feature map for heatmap generation
        logits = self.backbone(x)
        # Simulate Grad-CAM feature map
        dummy_heatmap = torch.randn(1, 1, 7, 7).to(DEVICE)
        return logits, dummy_heatmap