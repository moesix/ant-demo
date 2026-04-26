import os
import psutil
from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO, emit
import eventlet
from prometheus_client import make_wsgi_app, Counter, Histogram, Gauge
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import time
import threading

# Initialize async
eventlet.monkey_patch()

app = Flask(__name__)
app.debug = True

# WebSocket setup
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"postgresql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}@"
    f"{os.environ.get('DB_HOST')}/{os.environ.get('DB_NAME')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_POOL_SIZE'] = 10
app.config['SQLALCHEMY_MAX_OVERFLOW'] = 20
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 30
app.config['SQLALCHEMY_POOL_RECYCLE'] = 1800

# Initialize SQLAlchemy and Migrate
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Prometheus Metrics
REQUEST_COUNT = Counter('antdemo_requests_total', 'Total HTTP requests received')
REQUEST_DURATION = Histogram('antdemo_request_duration_seconds', 'Request duration in seconds')
ACTIVE_CONNECTIONS = Gauge('antdemo_active_connections', 'Active WebSocket connections')
SYSTEM_CPU = Gauge('antdemo_system_cpu', 'System CPU usage percentage')
SYSTEM_MEMORY = Gauge('antdemo_system_memory', 'System memory usage percentage')
SYSTEM_DISK = Gauge('antdemo_system_disk', 'System disk usage percentage')
SYSTEM_NET_SENT = Gauge('antdemo_system_net_sent', 'Network bytes sent')
SYSTEM_NET_RECV = Gauge('antdemo_system_net_recv', 'Network bytes received')
DATABASE_QUERIES = Counter('antdemo_database_queries', 'Database queries executed')
ERROR_COUNT = Counter('antdemo_errors_total', 'Application errors')

# Database Models (for Flask-SQLAlchemy)
class AccessLog(db.Model):
    __tablename__ = 'access_logs'
    id = db.Column(db.Integer, primary_key=True)
    log_message = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f'<AccessLog {self.log_message}>'

# Metrics collection thread
def collect_metrics():
    """Background thread to collect system metrics"""
    while True:
        # System metrics
        SYSTEM_CPU.set(psutil.cpu_percent())
        SYSTEM_MEMORY.set(psutil.virtual_memory().percent)
        SYSTEM_DISK.set(psutil.disk_usage('/').percent)
        net = psutil.net_io_counters()
        SYSTEM_NET_SENT.set(net.bytes_sent)
        SYSTEM_NET_RECV.set(net.bytes_recv)
        
        # Push to all connected clients
        metrics = {
            'cpu': psutil.cpu_percent(),
            'memory': psutil.virtual_memory().percent,
            'disk': psutil.disk_usage('/').percent,
            'net_sent': net.bytes_sent,
            'net_recv': net.bytes_recv,
            'timestamp': time.time()
        }
        socketio.emit('metric_update', metrics)
        
        time.sleep(2)

# Start metrics collection
metrics_thread = threading.Thread(target=collect_metrics, daemon=True)
metrics_thread.start()

# App Version - get from environment variable dynamically
def get_app_version():
    """Get application version from environment variable dynamically"""
    return os.environ.get('APP_VERSION', '1')

@app.route('/api/webapp/')
def api_webapp():
    return "Webapp Service"

@app.route('/health')
def health():
    """Health check endpoint for Kubernetes probes"""
    app_version = get_app_version()
    health_status = {
        'status': 'healthy',
        'version': app_version,
        'timestamp': psutil.boot_time()
    }
    
    # Check database connection for v3 and v4
    if app_version == '3' or app_version == '4':
        try:
            from sqlalchemy import text
            DATABASE_QUERIES.inc()
            db.session.execute(text('SELECT 1'))
            db.session.commit()
            health_status['database'] = 'connected'
        except Exception as e:
            health_status['status'] = 'unhealthy'
            health_status['database'] = 'connection failed'
            ERROR_COUNT.inc()
            return jsonify(health_status), 500
    
    return jsonify(health_status), 200

@app.route('/')
@REQUEST_DURATION.time()
def index():
    REQUEST_COUNT.inc()
    
    try:
        app_version = get_app_version()
        context = {
            'command': 'app.py --version ' + app_version,
            'content': '',
            'os_info': None,
            'logs': None
        }

        if app_version == '1':
            context['content'] = "Hello World!"

        elif app_version == '2':
            context['content'] = "Displaying Operating System Information:"
            disk = psutil.disk_usage('/')
            net = psutil.net_io_counters()
            context['os_info'] = {
            'cpu': psutil.cpu_percent(),
            'mem': psutil.virtual_memory().percent,
            'disk_total': f"{disk.total / (1024**3):.2f} GB", # bytes to GB
            'disk_used': f"{disk.used / (1024**3):.2f} GB",
            'disk_percent': disk.percent,
            'net_sent': f"{net.bytes_sent / (1024**2):.2f} MB", # bytes to GB
            'net_recv': f"{net.bytes_recv / (1024**2):.2f} MB"
        }

        elif app_version == '3':
            try:
                from sqlalchemy import text
                with db.engine.connect() as conn:
                    DATABASE_QUERIES.inc()
                    result = conn.execute(text("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_schema = 'public' 
                            AND table_name = 'access_logs'
                        );
                    """))
                    table_exists = result.scalar()
                    
                    if not table_exists:
                        DATABASE_QUERIES.inc()
                        conn.execute(text("""
                            CREATE TABLE access_logs (
                                id SERIAL PRIMARY KEY,
                                log_message VARCHAR(255) NOT NULL,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                            );
                        """))
                        conn.commit()
                
                new_log = AccessLog(log_message="Site accessed from v3")
                DATABASE_QUERIES.inc()
                db.session.add(new_log)
                db.session.commit()
                
                fetched_logs = AccessLog.query.order_by(AccessLog.created_at.desc()).limit(5).all()
                
                context['logs'] = []
                for log in fetched_logs:
                    context['logs'].append({
                        'message': log.log_message,
                        'timestamp': log.created_at
                    })
                context['content'] = "Your access has been logged to PGSQL."
            except Exception as e:
                context['content'] = f"Database query failed: {e}"
                ERROR_COUNT.inc()
                context['APP_VERSION'] = app_version
                return render_template('index.html', **context), 500

        elif app_version == '4':
            context['content'] = "Microservices Architecture (v4) with API Gateway, User Service, and Logging Service."

        elif app_version == '5':
            context['content'] = "Real-time Metrics Dashboard (v5) with WebSocket streaming and Prometheus integration."
            context['is_metrics'] = True

        else:
            context['content'] = f"Error: Unknown version '{app_version}' specified."
            context['APP_VERSION'] = app_version
            return render_template('index.html', **context), 404

        context['APP_VERSION'] = app_version
        return render_template('index.html', **context)
    except Exception as e:
        import traceback
        ERROR_COUNT.inc()
        return f"Error in index route: {str(e)}\n\nStack trace:\n{traceback.format_exc()}", 500

# WebSocket events
@socketio.on('connect')
def handle_connect():
    """Handle new WebSocket connection"""
    ACTIVE_CONNECTIONS.inc()
    print(f"New WebSocket connection")
    emit('connection_established', {'data': 'Connected'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    ACTIVE_CONNECTIONS.dec()
    print(f"WebSocket disconnected")

@socketio.on('metric_request')
def handle_metric_request(data):
    """Handle metric request from client"""
    print(f"Metric request: {data}")
    metrics = {
        'cpu': psutil.cpu_percent(),
        'memory': psutil.virtual_memory().percent,
        'disk': psutil.disk_usage('/').percent,
        'net_sent': psutil.net_io_counters().bytes_sent,
        'net_recv': psutil.net_io_counters().bytes_recv,
        'timestamp': time.time()
    }
    emit('metric_update', metrics)

# Prometheus metrics endpoint
@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    return make_wsgi_app()

if __name__ == "__main__":
    with app.app_context():
        if get_app_version() == '3':
            db.create_all()
            print("Database tables checked/created.")

    socketio.run(app, host='0.0.0.0', port=5000)