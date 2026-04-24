"""
Database Tests
"""

import os
import pytest
from app import app, db, AccessLog
from dotenv import load_dotenv

@pytest.fixture
def test_client():
    """Create a test client with test database configuration"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        
        with app.app_context():
            db.session.remove()
            db.drop_all()

def test_access_log_creation(test_client):
    """Test creating a new AccessLog entry"""
    with app.app_context():
        log = AccessLog(log_message="Test log entry")
        db.session.add(log)
        db.session.commit()
        
        assert log.id is not None
        assert log.log_message == "Test log entry"
        assert log.created_at is not None

def test_query_access_logs(test_client):
    """Test querying AccessLog entries"""
    with app.app_context():
        log1 = AccessLog(log_message="First log entry")
        log2 = AccessLog(log_message="Second log entry")
        db.session.add_all([log1, log2])
        db.session.commit()
        
        logs = AccessLog.query.all()
        assert len(logs) == 2
        assert logs[0].log_message in ["First log entry", "Second log entry"]