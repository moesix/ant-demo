from concurrent import futures
import grpc
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import datetime

from protobuf import user_service_pb2
from protobuf import user_service_pb2_grpc

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"postgresql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}@"
    f"{os.environ.get('DB_HOST')}/{os.environ.get('DB_NAME')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

@app.route('/')
def index():
    return "User Service"

@app.route('/health')
def health():
    return {'status': 'healthy'}

class UserServiceServicer(user_service_pb2_grpc.UserServiceServicer):
    def GetUser(self, request, context):
        with app.app_context():
            user = User.query.get(request.id)
            if not user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details('User not found')
                return user_service_pb2.UserResponse()
            
            return user_service_pb2.UserResponse(
                id=user.id,
                name=user.name,
                email=user.email,
                password=user.password,
                created_at=user.created_at.isoformat(),
                updated_at=user.updated_at.isoformat()
            )
    
    def CreateUser(self, request, context):
        with app.app_context():
            user = User(
                name=request.name,
                email=request.email,
                password=request.password
            )
            db.session.add(user)
            db.session.commit()
            
            return user_service_pb2.UserResponse(
                id=user.id,
                name=user.name,
                email=user.email,
                password=user.password,
                created_at=user.created_at.isoformat(),
                updated_at=user.updated_at.isoformat()
            )
    
    def UpdateUser(self, request, context):
        with app.app_context():
            user = User.query.get(request.id)
            if not user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details('User not found')
                return user_service_pb2.UserResponse()
            
            user.name = request.name
            user.email = request.email
            user.password = request.password
            db.session.commit()
            
            return user_service_pb2.UserResponse(
                id=user.id,
                name=user.name,
                email=user.email,
                password=user.password,
                created_at=user.created_at.isoformat(),
                updated_at=user.updated_at.isoformat()
            )
    
    def DeleteUser(self, request, context):
        with app.app_context():
            user = User.query.get(request.id)
            if not user:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details('User not found')
                return user_service_pb2.UserResponse()
            
            db.session.delete(user)
            db.session.commit()
            
            return user_service_pb2.UserResponse(
                id=user.id,
                name=user.name,
                email=user.email,
                password=user.password,
                created_at=user.created_at.isoformat(),
                updated_at=user.updated_at.isoformat()
            )
    
    def ListUsers(self, request, context):
        with app.app_context():
            users = User.query.all()
            
            return user_service_pb2.ListUsersResponse(
                users=[
                    user_service_pb2.UserResponse(
                        id=user.id,
                        name=user.name,
                        email=user.email,
                        password=user.password,
                        created_at=user.created_at.isoformat(),
                        updated_at=user.updated_at.isoformat()
                    )
                    for user in users
                ]
            )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_service_pb2_grpc.add_UserServiceServicer_to_server(
        UserServiceServicer(), server
    )
    server.add_insecure_port('[::]:50051')
    server.start()
    print("User Service gRPC server started on port 50051")
    
    server.wait_for_termination()

if __name__ == '__main__':
    import threading
    
    with app.app_context():
        db.create_all()
    
    from werkzeug.serving import make_server
    
    def run_flask():
        app.run(host='0.0.0.0', port=5000)
    
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    serve()