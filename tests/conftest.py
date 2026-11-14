"""
Pytest configuration and fixtures for activities API tests
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provide a TestClient for making HTTP requests to the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """
    Fixture to reset activities to a known state before each test.
    This ensures test isolation and prevents state leakage between tests.
    """
    # Store original state
    original_state = {
        name: {
            "description": activity["description"],
            "schedule": activity["schedule"],
            "max_participants": activity["max_participants"],
            "participants": activity["participants"].copy()
        }
        for name, activity in activities.items()
    }
    
    yield  # Test runs here
    
    # Restore original state after test
    for name in activities:
        activities[name]["participants"] = original_state[name]["participants"].copy()
