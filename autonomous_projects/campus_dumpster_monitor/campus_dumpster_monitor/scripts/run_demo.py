import os
from app import create_app

if __name__ == '__main__':
    # Use Flask's built‑in dev server; in production a WSGI server would be used.
    app = create_app()
    # Optionally set host/port via env vars
    host = os.getenv('FLASK_RUN_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_RUN_PORT', '5000'))
    app.run(host=host, port=port, debug=True)
