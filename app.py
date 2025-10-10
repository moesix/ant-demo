import os
import psutil
import psycopg2
from flask import Flask

app = Flask(__name__)

# --- Database Connection ---
def get_db_connection():
    conn = psycopg2.connect(
        host=os.environ.get('DB_HOST'),
        database=os.environ.get('DB_NAME'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'))
    return conn

# --- App Version Logic ---
APP_VERSION = os.environ.get('APP_VERSION', '1') # Default to v1

@app.route('/')
def index():
    if APP_VERSION == '1':
        # Version 1: Display simple text [cite: 8]
        return "<h1>Hello World! v1</h1>"

    elif APP_VERSION == '2':
        # Version 2: Display OS information [cite: 9]
        cpu_usage = psutil.cpu_percent()
        mem_usage = psutil.virtual_memory().percent
        return f"<h1>OS Info v2</h1><p>CPU Usage: {cpu_usage}%</p><p>Memory Usage: {mem_usage}%</p>"

    elif APP_VERSION == '3':
        # Version 3: Log access to database [cite: 10]
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO access_logs (log_message) VALUES (%s)", (f"Accessed v3 at {psutil.time.time()}",))
            conn.commit()
            cur.close()
            conn.close()
            return "<h1>Hello from v3!</h1><p>Your access has been logged to PostgreSQL.</p>"
        except Exception as e:
            return f"<h1>Database Connection Error</h1><p>{e}</p>", 500
    else:
        return "<h1>Unknown Version</h1>", 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)