"""Test main application functionality."""

import pytest
from fastapi.testclient import TestClient

from src.main import app


def test_health_check():
    """Test health check endpoint."""
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data


def test_root_endpoint():
    """Test root endpoint."""
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data