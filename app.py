import os
import psutil
from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

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

# Database Models (for Flask-SQLAlchemy)
class AccessLog(db.Model):
    __tablename__ = 'access_logs'
    id = db.Column(db.Integer, primary_key=True)
    log_message = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f'<AccessLog {self.log_message}>'

# App Version - get from environment variable dynamically
def get_app_version():
    """Get application version from environment variable dynamically"""
    return os.environ.get('APP_VERSION', '1')

@app.route('/health')
def health():
    """Health check endpoint for Kubernetes probes"""
    app_version = get_app_version()
    health_status = {
        'status': 'healthy',
        'version': app_version,
        'timestamp': psutil.boot_time()
    }
    
    # Check database connection for v3
    if app_version == '3':
        try:
            # Attempt to connect to the database
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            db.session.commit()
            health_status['database'] = 'connected'
        except Exception as e:
            health_status['status'] = 'unhealthy'
            health_status['database'] = 'connection failed'
            return jsonify(health_status), 500
    
    return jsonify(health_status), 200

@app.route('/')
def index():
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
            # Check if access_logs table exists and create it if necessary
            from sqlalchemy import text
            with db.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'access_logs'
                    );
                """))
                table_exists = result.scalar()
                
                if not table_exists:
                    conn.execute(text("""
                        CREATE TABLE access_logs (
                            id SERIAL PRIMARY KEY,
                            log_message VARCHAR(255) NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                        );
                    """))
                    conn.commit()
            
            # Log the current access
            new_log = AccessLog(log_message="Site accessed from v3")
            db.session.add(new_log)
            db.session.commit()
            
            # Get last 5 access logs
            fetched_logs = AccessLog.query.order_by(AccessLog.created_at.desc()).limit(5).all()
            
            # Format logs
            context['logs'] = []
            for log in fetched_logs:
                context['logs'].append({
                    'message': log.log_message,
                    'timestamp': log.created_at
                })
            context['content'] = "Your access has been logged to PGSQL."
        except Exception as e:
            context['content'] = f"Database query failed: {e}"
            context['APP_VERSION'] = app_version
            return render_template('index.html', **context), 500

    else:
        context['content'] = f"Error: Unknown version '{app_version}' specified."
        context['APP_VERSION'] = app_version
        return render_template('index.html', **context), 404

    context['APP_VERSION'] = app_version
    return render_template('index.html', **context)

if __name__ == "__main__":
    # Create tables if they don't exist (for v3)
    with app.app_context():
        if get_app_version() == '3':
            # Create all tables
            db.create_all()
            print("Database tables checked/created.")

    app.run(host='0.0.0.0', port=5000)