import io
from pathlib import Path
from PIL import Image
import pytest
from detector import Detector

@pytest.fixture(scope='module')
def detector():
    # Initialise once for the whole module
    return Detector()

def test_model_loads(detector):
    # The constructor should not raise; model attribute must exist
    assert detector._model is not None

def test_predict_returns_structure(detector):
    # Create a simple solid‑color image (red) – 224x224 is enough
    img = Image.new('RGB', (224, 224), color='red')
    results = detector.predict(img)
    assert isinstance(results, list)
    assert len(results) > 0
    for entry in results:
        assert isinstance(entry, dict)
        assert 'label' in entry and 'confidence' in entry
        assert isinstance(entry['label'], str)
        assert isinstance(entry['confidence'], float)
    # Probabilities should sum to <= 1 (top‑k subset)
    total_conf = sum(item['confidence'] for item in results)
    assert 0.0 <= total_conf <= 1.0
