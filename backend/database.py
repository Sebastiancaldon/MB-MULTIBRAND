"""Acceso a MySQL compartido; conserva el punto de entrada de la entrega SOAP."""
from comun.db import connect, fetch_all, fetch_one

def get_connection():
    return connect()
