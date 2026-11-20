"""Alias de ejecución compatible con la estructura del proyecto SOAP."""
from .server import app

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(__import__("os").environ.get("PORT", "5004")), debug=False, use_reloader=False)
