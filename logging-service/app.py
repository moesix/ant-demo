from concurrent import futures
import grpc
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import datetime

from protobuf import logging_service_pb2
from protobuf import logging_service_pb2_grpc

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"postgresql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}@"
    f"{os.environ.get('DB_HOST')}/{os.environ.get('DB_NAME')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class LogEntry(db.Model):
    __tablename__ = 'log_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'message': self.message,
            'created_at': self.created_at.isoformat()
        }

@app.route('/api/logs/')
def api_logs():
    return "Logging Service API"

@app.route('/')
def index():
    return "Logging Service"

@app.route('/health')
def health():
    return {'status': 'healthy'}

class LoggingServiceServicer(logging_service_pb2_grpc.LoggingServiceServicer):
    def CreateLog(self, request, context):
        with app.app_context():
            log = LogEntry(message=request.message)
            db.session.add(log)
            db.session.commit()
            
            return logging_service_pb2.LogResponse(
                id=log.id,
                message=log.message,
                created_at=log.created_at.isoformat()
            )
    
    def GetLogs(self, request, context):
        with app.app_context():
            limit = request.limit if request.limit > 0 else 10
            logs = LogEntry.query.order_by(LogEntry.created_at.desc()).limit(limit).all()
            
            return logging_service_pb2.GetLogsResponse(
                logs=[
                    logging_service_pb2.LogResponse(
                        id=log.id,
                        message=log.message,
                        created_at=log.created_at.isoformat()
                    )
                    for log in logs
                ]
            )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    logging_service_pb2_grpc.add_LoggingServiceServicer_to_server(
        LoggingServiceServicer(), server
    )
    server.add_insecure_port('[::]:50052')
    server.start()
    print("Logging Service gRPC server started on port 50052")
    
    server.wait_for_termination()

if __name__ == '__main__':
    import threading
    import time
    
    # Retry DB connection up to 30 times
    for attempt in range(30):
        try:
            with app.app_context():
                db.create_all()
            print("Database tables created/verified")
            break
        except Exception as e:
            if attempt < 29:
                print(f"DB not ready (attempt {attempt+1}/30): {e}")
                time.sleep(2)
            else:
                print(f"Failed to connect to DB after 30 attempts: {e}")
                raise
    
    def run_flask():
        app.run(host='0.0.0.0', port=5000)
    
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    serve()