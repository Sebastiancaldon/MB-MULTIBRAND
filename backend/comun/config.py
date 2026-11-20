import os
from dotenv import load_dotenv
load_dotenv()
DB_HOST=os.getenv('MB_DB_HOST','127.0.0.1')
DB_PORT=int(os.getenv('MB_DB_PORT','3306'))
DB_NAME=os.getenv('MB_DB_NAME','mb_multibrand')
DB_USER=os.getenv('MB_DB_USER','root')
DB_PASSWORD=os.getenv('MB_DB_PASSWORD','root')
JWT_SECRET=os.getenv('JWT_SECRET_KEY') or os.getenv('JWT_SECRET','')
if len(JWT_SECRET)<32:
    raise RuntimeError('Configure JWT_SECRET_KEY (>=32 caracteres) en .env. Genere una con: python -c "import secrets; print(secrets.token_hex(32))"')
API_KEY=os.getenv('API_KEY','')
JWT_MINUTES=int(os.getenv('JWT_MINUTES','10'))
COMISION_MB=float(os.getenv('COMISION_MB','0.05'))

# Orígenes del frontend Vue que pueden consumir la API (separados por coma)
CORS_ORIGINS=[o.strip() for o in os.getenv('CORS_ORIGINS','http://localhost:5173,http://127.0.0.1:5173').split(',') if o.strip()]
