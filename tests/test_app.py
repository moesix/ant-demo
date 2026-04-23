"""
Unit Tests for Flask Application
"""

import pytest
from app import app

@pytest.fixture
def client():
    """Create a test client for the Flask application"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    """Test the health endpoint returns healthy status"""
    response = client.get('/health')
    assert response.status_code == 200
    assert b'"status":"healthy"' in response.data

def test_index_endpoint_v1(client, monkeypatch):
    """Test the index endpoint returns Hello World for v1"""
    monkeypatch.setenv('APP_VERSION', '1')
    response = client.get('/')
    assert response.status_code == 200
    assert b'Hello World!' in response.data

def test_index_endpoint_v2(client, monkeypatch):
    """Test the index endpoint returns OS info for v2"""
    monkeypatch.setenv('APP_VERSION', '2')
    response = client.get('/')
    assert response.status_code == 200
    assert b'System Information' in response.data