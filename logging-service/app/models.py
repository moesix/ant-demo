from app import db
from app.protos import logging_service_pb2
import datetime

class LogEntry(db.Model):
    __tablename__ = 'log_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    service = db.Column(db.String(255), nullable=False)
    level = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'service': self.service,
            'level': self.level,
            'message': self.message,
            'timestamp': self.timestamp.isoformat()
        }
    
    def to_proto(self):
        return logging_service_pb2.LogEntry(
            id=self.id,
            service=self.service,
            level=self.level,
            message=self.message,
            timestamp=self.timestamp.isoformat()
        )