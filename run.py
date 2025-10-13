# run.py
import logging
from app import app, socketio

# Configure logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger('werkzeug')
log.setLevel(logging.WARNING)

if __name__ == '__main__':
    try:
        # Use SocketIO server with compatible parameters
        socketio.run(
            app, 
            debug=True, 
            host="0.0.0.0", 
            port=5000,
            use_reloader=True
        )
    except Exception as e:
        print(f"Error starting SocketIO server: {e}")
        # Fallback to regular Flask if SocketIO fails
        print("Falling back to regular Flask server...")
        app.run(debug=True, host="0.0.0.0", port=5000, use_reloader=True)
