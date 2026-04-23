import os
import psutil
import psycopg2
from flask import Flask, render_template, jsonify
from psycopg2 import pool
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

# Database Connection Pool
DB_POOL = None

def init_db_pool():
    """Initialize database connection pool"""
    global DB_POOL
    try:
        DB_POOL = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            host=os.environ.get('DB_HOST'),
            database=os.environ.get('DB_NAME'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASSWORD')
        )
        app.logger.info("Database connection pool initialized")
    except Exception as e:
        app.logger.error(f"Failed to initialize database connection pool: {e}")

def get_db_connection():
    """Get connection from pool or fall back to direct connection"""
    try:
        if DB_POOL:
            return DB_POOL.getconn()
        else:
            conn = psycopg2.connect(
                host=os.environ.get('DB_HOST'),
                database=os.environ.get('DB_NAME'),
                user=os.environ.get('DB_USER'),
                password=os.environ.get('DB_PASSWORD'))
            return conn
    except psycopg2.OperationalError as e:
        # Return the error to be displayed on the page
        return e

def release_db_connection(conn):
    """Release connection back to pool"""
    if DB_POOL and conn:
        try:
            DB_POOL.putconn(conn)
        except Exception as e:
            app.logger.error(f"Failed to release connection: {e}")

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
        conn = get_db_connection()
        if isinstance(conn, Exception):
            health_status['status'] = 'unhealthy'
            health_status['database'] = 'connection failed'
            return jsonify(health_status), 500
        else:
            health_status['database'] = 'connected'
            release_db_connection(conn)
    
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
        conn = get_db_connection()
        if isinstance(conn, Exception):
            context['content'] = f"Database Connection Error: {conn}"
            context['APP_VERSION'] = APP_VERSION
            return render_template('index.html', **context), 500
        
        try:
            cur = conn.cursor()
            # Log the current access
            cur.execute("INSERT INTO access_logs (log_message, created_at) VALUES (%s, NOW())", (f"Site accessed from v3",))
            conn.commit()
            
            # get last 5 access logs
            cur.execute("SELECT log_message, created_at FROM access_logs ORDER BY created_at DESC LIMIT 5")
            fetched_logs = cur.fetchall()
            
            # Format logs
            context['logs'] = []
            for row in fetched_logs:
                log = {'message': row[0]}
                if row[1]:
                    log['timestamp'] = row[1]
                else:
                    log['timestamp'] = None
                context['logs'].append(log)
            context['content'] = "Your access has been logged to PGSQL."

            cur.close()
            release_db_connection(conn)
        except Exception as e:
            context['content'] = f"Database query failed: {e}"
            context['APP_VERSION'] = APP_VERSION
            return render_template('index.html', **context), 500

    else:
        context['content'] = f"Error: Unknown version '{app_version}' specified."
        context['APP_VERSION'] = app_version
        return render_template('index.html', **context), 404

    context['APP_VERSION'] = app_version
    return render_template('index.html', **context)

if __name__ == "__main__":
    # Initialize database connection pool
    init_db_pool()
    
    # Table check for v3
    if get_app_version() == '3':
        conn = get_db_connection()
        if not isinstance(conn, Exception):
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS access_logs (
                    id SERIAL PRIMARY KEY,
                    log_message VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
            cur.close()
            release_db_connection(conn)
            print("Database table 'access_logs' checked/created.")

    app.run(host='0.0.0.0', port=5000)