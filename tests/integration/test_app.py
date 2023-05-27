import requests

def test_app_running():
    response = requests.get('http://localhost:8501')
    assert response.status_code == 200
