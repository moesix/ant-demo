#!/usr/bin/env python3
import grpc
from protobuf import user_service_pb2
from protobuf import user_service_pb2_grpc
from protobuf import logging_service_pb2
from protobuf import logging_service_pb2_grpc

def test_user_service():
    print("Testing User Service gRPC...")
    try:
        # Test direct connection (port 50051)
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = user_service_pb2_grpc.UserServiceStub(channel)
            response = stub.ListUsers(user_service_pb2.ListUsersRequest())
            print(f"Direct connection - Number of users: {len(response.users)}")
            
            # Print users
            for user in response.users:
                print(f"User: {user.name} ({user.email})")
        
        # Test through Kong (port 8000)
        with grpc.insecure_channel('localhost:8000') as channel:
            stub = user_service_pb2_grpc.UserServiceStub(channel)
            # Note: For Kong gRPC routing with path prefix, we might need to use
            # a custom channel or modify the service name. However, in our current
            # configuration, Kong is configured to route /api/users to the user service.
            try:
                response = stub.ListUsers(user_service_pb2.ListUsersRequest())
                print(f"Through Kong - Number of users: {len(response.users)}")
            except Exception as e:
                print(f"Through Kong - Error: {str(e)}")
                
    except Exception as e:
        print(f"Connection error: {str(e)}")

def test_logging_service():
    print("\nTesting Logging Service gRPC...")
    try:
        # Test direct connection (port 50052)
        with grpc.insecure_channel('localhost:50052') as channel:
            stub = logging_service_pb2_grpc.LoggingServiceStub(channel)
            response = stub.GetLogs(logging_service_pb2.GetLogsRequest(limit=3))
            print(f"Direct connection - Number of logs: {len(response.logs)}")
            
            # Print logs
            for log in response.logs:
                print(f"Log: {log.message}")
        
        # Test through Kong (port 8000)
        with grpc.insecure_channel('localhost:8000') as channel:
            stub = logging_service_pb2_grpc.LoggingServiceStub(channel)
            try:
                response = stub.GetLogs(logging_service_pb2.GetLogsRequest(limit=3))
                print(f"Through Kong - Number of logs: {len(response.logs)}")
            except Exception as e:
                print(f"Through Kong - Error: {str(e)}")
                
    except Exception as e:
        print(f"Connection error: {str(e)}")

if __name__ == "__main__":
    test_user_service()
    test_logging_service()