"""
Test fixtures and configuration for the Mergington High School API tests.
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the src directory to the path so we can import the app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities data to initial state before each test."""
    # Store original activities
    original_activities = {}
    for name, details in activities.items():
        original_activities[name] = {
            "description": details["description"],
            "schedule": details["schedule"],
            "max_participants": details["max_participants"],
            "participants": details["participants"].copy()  # Make a copy of the list
        }
    
    yield
    
    # Reset activities after test
    activities.clear()
    activities.update(original_activities)


@pytest.fixture
def sample_activity_data():
    """Sample activity data for testing."""
    return {
        "Test Activity": {
            "description": "A test activity for unit testing",
            "schedule": "Mondays, 3:00 PM - 4:00 PM",
            "max_participants": 5,
            "participants": ["test1@mergington.edu", "test2@mergington.edu"]
        }
    }
