import os
from dotenv import load_dotenv

load_dotenv()

# Base de datos
DB_HOST = os.getenv('MB_DB_HOST', '127.0.0.1')
DB_PORT = int(os.getenv('MB_DB_PORT', '5432'))
DB_NAME = os.getenv('MB_DB_NAME', 'mb_multibrand')
DB_USER = os.getenv('MB_DB_USER', '')
DB_PASSWORD = os.getenv('MB_DB_PASSWORD', '')

# Seguridad JWT
JWT_SECRET = os.getenv('JWT_SECRET_KEY') or os.getenv('JWT_SECRET', '')

if len(JWT_SECRET) < 32:
    raise RuntimeError(
        'Configure JWT_SECRET_KEY con al menos 32 caracteres'
    )

API_KEY = os.getenv('API_KEY', '')
JWT_MINUTES = int(os.getenv('JWT_MINUTES', '10'))

# Configuración del negocio
COMISION_MB = float(os.getenv('COMISION_MB', '0.05'))

# Frontend autorizado
CORS_ORIGINS = [
    origen.strip()
    for origen in os.getenv(
        'CORS_ORIGINS',
        'http://localhost:5173,http://127.0.0.1:5173'
    ).split(',')
    if origen.strip()
]