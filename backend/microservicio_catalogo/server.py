"""Servidor REST de microservicio_catalogo; puerto 5001."""
from .app import app

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False, use_reloader=False)
