import sys
import os
import numpy as np
import torch
from PIL import Image

# Ensure package is in path
sys.path.append(os.getcwd())

from crisper_cell_classifier import predict
from crisper_cell_classifier.utils import create_synthetic_image

def test_pipeline():
    print("Running CRISPR Cell Classifier Integration Test...")
    
    # 1. Setup: Create synthetic data
    test_img_np = create_synthetic_image(size=(512, 512, 3))
    temp_path = "temp_test_image.png"
    Image.fromarray(test_img_np).save(temp_path)
    
    try:
        # 2. Execution: Run prediction
        result = predict(temp_path)
        
        # 3. Assertions
        print(f"Result: {result}")
        
        assert "label" in result, "Missing 'label' key"
        assert "probability" in result, "Missing 'probability' key"
        assert "heatmap" in result, "Missing 'heatmap' key"
        
        assert result["label"] in ["edited", "unedited"], "Invalid label"
        assert 0.0 <= result["probability"] <= 1.0, "Probability out of bounds"
        
        heatmap = result["heatmap"]
        assert isinstance(heatmap, np.ndarray), "Heatmap must be numpy array"
        assert heatmap.shape == (512, 512), f"Heatmap shape mismatch: {heatmap.shape} != (512, 512)"
        
        print("✅ All tests passed successfully!")
        return True
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    success = test_pipeline()
    sys.exit(0 if success else 1)