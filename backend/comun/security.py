import hmac
from functools import wraps
import jwt
from flask import request, jsonify, g
from comun.config import JWT_SECRET, JWT_MINUTES, API_KEY

ALGORITHM='HS256'
def require_auth(fn):
    @wraps(fn)
    def wrapper(*args,**kwargs):
        header=request.headers.get('Authorization','')
        if not header.startswith('Bearer '):
            return jsonify({'error':'Token requerido (Authorization: Bearer <token>)'}),401
        token=header[7:].strip()
        try:
            payload=jwt.decode(token,JWT_SECRET,algorithms=[ALGORITHM])
            g.user_id=int(payload['sub']); g.username=payload['username']; g.usuario=payload
        except jwt.ExpiredSignatureError:
            return jsonify({'error':'El token expiró. Inicie sesión nuevamente.'}),401
        except (jwt.InvalidTokenError,KeyError,ValueError,TypeError):
            return jsonify({'error':'Token inválido.'}),401
        return fn(*args,**kwargs)
    return wrapper

def require_api_key(fn):
    @wraps(fn)
    def wrapper(*args,**kwargs):
        clave=request.headers.get('X-API-KEY','')
        # compare_digest compara en tiempo constante (evita ataques de temporización)
        if API_KEY and hmac.compare_digest(clave.encode(),API_KEY.encode()):
            return fn(*args,**kwargs)
        return jsonify({'error':'Acceso denegado. API Key inválida.'}),401
    return wrapper

def error(message,status=400,**extra):
    return jsonify({'error':message,**extra}),status
