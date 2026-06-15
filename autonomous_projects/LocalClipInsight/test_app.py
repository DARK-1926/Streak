import pytest
import numpy as np
from main import LocalClipInsight

def test_initialization():
    lci = LocalClipInsight()
    assert lci.device in ["cuda", "cpu"]

def test_search_logic():
    lci = LocalClipInsight()
    # Mocking FAISS index and metadata for unit test
    lci.index = None
    # We simulate a small index to ensure the search logic doesn't crash
    import faiss
    d = 512
    lci.index = faiss.IndexFlatIP(d)
    lci.index.add(np.random.random((10, d)).astype('float32'))
    lci.metadata = [{"video": "test.mp4", "timestamp": i} for i in range(10)]
    
    # Mocking CLIP model output to avoid downloading weights during unit test
    class MockModel:
        def encode_text(self, x): return torch.randn(1, 512)
    
    import torch
    lci.model = MockModel()
    results = lci.search("test query", top_k=2)
    assert len(results) == 2
