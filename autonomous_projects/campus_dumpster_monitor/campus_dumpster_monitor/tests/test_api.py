import io
from pathlib import Path
from PIL import Image
import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_status_endpoint(client):
    resp = client.get('/status')
    assert resp.status_code == 200
    json_data = resp.get_json()
    assert json_data.get('status') == 'ok'

def test_upload_endpoint(client):
    # Generate a tiny PNG in memory
    img = Image.new('RGB', (64, 64), color='blue')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    data = {'file': (buf, 'test.png')}
    resp = client.post('/upload', content_type='multipart/form-data', data=data)
    assert resp.status_code == 200
    json_data = resp.get_json()
    assert 'detections' in json_data
    detections = json_data['detections']
    assert isinstance(detections, list)
    # Each detection should have label and confidence
    for det in detections:
        assert 'label' in det and 'confidence' in det
