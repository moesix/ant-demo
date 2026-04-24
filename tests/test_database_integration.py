"""
Integration Tests with Real Database Connections
"""

import os
import pytest
from app import app, db, AccessLog
from dotenv import load_dotenv
from contextlib import contextmanager

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

@pytest.fixture(scope='function')
def app_context():
    """Create an application context for integration testing with clean state per test"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"postgresql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}@"
        f"{os.environ.get('DB_HOST')}/{os.environ.get('DB_NAME')}"
    )
    
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        yield
        # Clean up all data from all tables
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()
        db.session.remove()
        db.drop_all()

@contextmanager
def get_db_session():
    """Context manager to get a database session"""
    try:
        db.session.begin()
        yield db.session
    except Exception:
        db.session.rollback()
        raise
    finally:
        db.session.close()

def test_access_log_persistence(app_context):
    """Test that AccessLog entries are properly persisted to the database"""
    with get_db_session() as session:
        test_log_message = "Integration test log entry"
        log = AccessLog(log_message=test_log_message)
        session.add(log)
        session.commit()
        
        # Verify the log was created with expected properties
        assert log.id is not None
        assert log.log_message == test_log_message
        assert log.created_at is not None
        
        # Retrieve the log from the database
        retrieved_log = session.query(AccessLog).filter_by(log_message=test_log_message).first()
        assert retrieved_log is not None
        assert retrieved_log.id == log.id

def test_multiple_log_entries(app_context):
    """Test that multiple AccessLog entries can be created and retrieved"""
    with get_db_session() as session:
        log_messages = ["First log entry", "Second log entry", "Third log entry"]
        for message in log_messages:
            session.add(AccessLog(log_message=message))
        session.commit()
        
        # Verify all logs were created
        logs = session.query(AccessLog).all()
        assert len(logs) == 3
        
        # Verify all log messages are present
        log_messages_from_db = [log.log_message for log in logs]
        for message in log_messages:
            assert message in log_messages_from_db

def test_query_latest_access_logs(app_context):
    """Test querying the latest 5 access logs"""
    with get_db_session() as session:
        # Create more than 5 log entries
        for i in range(6):
            session.add(AccessLog(log_message=f"Test log entry {i}"))
        session.commit()
        
        # Get the latest 5 logs
        latest_logs = session.query(AccessLog).order_by(AccessLog.created_at.desc()).limit(5).all()
        
        # Verify we got exactly 5 logs
        assert len(latest_logs) == 5
        
        # Verify the logs are in descending order
        previous_timestamp = None
        for log in latest_logs:
            if previous_timestamp:
                assert log.created_at <= previous_timestamp
            previous_timestamp = log.created_at