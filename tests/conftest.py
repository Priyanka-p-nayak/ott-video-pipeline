"""Shared pytest fixtures for all test files."""

import pytest
from app import create_app


@pytest.fixture
def client():
    """
    Creates a Flask test client connected to our app.
    Any test function that takes 'client' as a parameter
    automatically receives this fake browser.
    """
    app = create_app()
    app.config['TESTING'] = True
    
    # Create the fake browser and yield it to the test
    with app.test_client() as test_client:
        yield test_client