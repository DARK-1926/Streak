from main import index_video

def test_index_video():
    result = index_video("dummy_path")
    assert result["status"] == "indexed"