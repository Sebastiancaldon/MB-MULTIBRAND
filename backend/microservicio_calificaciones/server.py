"""Servidor REST de microservicio_calificaciones; puerto 5004."""
from .app import app

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5004, debug=False, use_reloader=False)
