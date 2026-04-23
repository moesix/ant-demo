import os
import psutil
import psycopg2
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# DB
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.environ.get('DB_HOST'),
            database=os.environ.get('DB_NAME'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASSWORD'))
        return conn
    except psycopg2.OperationalError as e:
        # Return the error to be displayed on the page
        return e

# App Version
APP_VERSION = os.environ.get('APP_VERSION', '1')

@app.route('/health')
def health():
    """Health check endpoint for Kubernetes probes"""
    health_status = {
        'status': 'healthy',
        'version': APP_VERSION,
        'timestamp': psutil.boot_time()
    }
    
    # Check database connection for v3
    if APP_VERSION == '3':
        conn = get_db_connection()
        if isinstance(conn, Exception):
            health_status['status'] = 'unhealthy'
            health_status['database'] = 'connection failed'
            return jsonify(health_status), 500
        else:
            health_status['database'] = 'connected'
            conn.close()
    
    return jsonify(health_status), 200

@app.route('/')
def index():
    context = {
        'command': 'app.py --version ' + APP_VERSION,
        'content': '',
        'os_info': None,
        'logs': None
    }

    if APP_VERSION == '1':
        context['content'] = "Hello World!"

    elif APP_VERSION == '2':
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

    elif APP_VERSION == '3':
        conn = get_db_connection()
        if isinstance(conn, Exception):
            context['content'] = f"Database Connection Error: {conn}"
            context['APP_VERSION'] = APP_VERSION
            return render_template('index.html', **context), 500
        
        try:
            cur = conn.cursor()
            # Log the current access
            cur.execute("INSERT INTO access_logs (log_message) VALUES (%s)", (f"Site accessed from v3",))
            conn.commit()
            
            # get last 5 access logs
            cur.execute("SELECT log_message, created_at FROM access_logs ORDER BY created_at DESC LIMIT 5")
            fetched_logs = cur.fetchall()
            
            # Format logs
            context['logs'] = [{'message': row[0], 'timestamp': row[1]} for row in fetched_logs]
            context['content'] = "Your access has been logged to PGSQL."

            cur.close()
            conn.close()
        except Exception as e:
            context['content'] = f"Database query failed: {e}"
            context['APP_VERSION'] = APP_VERSION
            return render_template('index.html', **context), 500

    else:
        context['content'] = f"Error: Unknown version '{APP_VERSION}' specified."
        context['APP_VERSION'] = APP_VERSION
        return render_template('index.html', **context), 404

    context['APP_VERSION'] = APP_VERSION
    return render_template('index.html', **context)

if __name__ == "__main__":
    # Table check for v3
    if APP_VERSION == '3':
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
            conn.close()
            print("Database table 'access_logs' checked/created.")

    app.run(host='0.0.0.0', port=5000)