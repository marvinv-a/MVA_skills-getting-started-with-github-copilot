import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory activities after each test."""
    snapshot = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(snapshot)


@pytest.fixture
def client():
    return TestClient(app)
