import pytest
from optimizer import HardwareProfiler, ModelSelector

@pytest.fixture
def profiler():
    return HardwareProfiler()

def test_cpu_info(profiler):
    cpu = profiler.cpu_info()
    assert "cores" in cpu
    assert cpu["cores"] > 0

def test_memory_info(profiler):
    mem = profiler.memory_info()
    assert mem["total_gb"] > 0

def test_disk_info(profiler):
    disk = profiler.disk_info()
    assert disk["total_gb"] > 0

def test_model_selector(profiler):
    selector = ModelSelector(profiler)
    rec = selector.recommend()
    assert rec in {"llama-70b", "llama-7b"}
