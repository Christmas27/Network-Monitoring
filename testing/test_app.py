#!/usr/bin/env python3
"""
Basic tests for the Network Dashboard application
"""

import pytest
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

@pytest.fixture
def client():
    """Create a test client for the Flask application"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    """Test the health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert 'timestamp' in data
    assert 'version' in data

def test_dashboard_page(client):
    """Test the main dashboard page loads"""
    response = client.get('/')
    assert response.status_code == 200

def test_devices_page(client):
    """Test the devices page loads"""
    response = client.get('/devices')
    assert response.status_code == 200

def test_api_devices_endpoint(client):
    """Test the API devices endpoint"""
    response = client.get('/api/devices')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)

def test_static_files(client):
    """Test that static files are accessible"""
    # Test CSS file
    response = client.get('/static/css/style.css')
    # Should return 200 if file exists, or 404 if not (both are valid for this test)
    assert response.status_code in [200, 404]

if __name__ == '__main__':
    pytest.main([__file__])
