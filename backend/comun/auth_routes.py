"""Rutas de login compartidas (Blueprint), al estilo del ejemplo cafeteria_api_GPPD_jwt.

Cada microservicio registra este Blueprint, de modo que el login vive como una
ruta más de CADA servicio y no existe un servicio único de autenticación:

    POST /login      (público)            -> emite el JWT
    POST /register   (header X-API-KEY)   -> crea cliente + cuenta

Todos los servicios comparten JWT_SECRET_KEY (.env), así que un token emitido
por cualquiera de ellos es válido en los demás.
"""
import datetime
import jwt
from flask import Blueprint, request, jsonify
from pymysql.err import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from comun.config import JWT_SECRET, JWT_MINUTES
from comun.db import connect, fetch_one
from comun.security import require_api_key, ALGORITHM

login_bp = Blueprint('login_bp', __name__)


@login_bp.route('/register', methods=['POST'])
@require_api_key  # Para que no cualquiera cree usuarios
def registrar_usuario():
    datos = request.get_json(silent=True) or {}
    username = str(datos.get('username') or '').strip()
    password = datos.get('password')
    nombre = str(datos.get('nombre') or '').strip()
    correo = str(datos.get('correo') or '').strip().lower()

    if not username or not password or not nombre or not correo:
        return jsonify({"error": "username, password, nombre y correo son obligatorios"}), 400
    if len(password) < 8:
        return jsonify({"error": "La contraseña debe tener al menos 8 caracteres"}), 400

    # Se guarda el hash (con sal), nunca la contraseña en texto plano
    password_hash = generate_password_hash(password)

    conn = connect()
    try:
        with conn.cursor() as c:
            c.execute("INSERT INTO clientes(nombre,correo) VALUES(%s,%s)", (nombre, correo))
            c.execute("INSERT INTO cuentas(id_cliente,usuario,password_hash) VALUES(%s,%s,%s)",
                      (c.lastrowid, username, password_hash))
        conn.commit()
        return jsonify({"mensaje": "Usuario registrado exitosamente"}), 201
    except IntegrityError:
        conn.rollback()
        return jsonify({"error": "No se pudo registrar (¿usuario o correo duplicado?)"}), 400
    finally:
        conn.close()


@login_bp.route('/login', methods=['POST'])
def login():
    datos = request.get_json(silent=True) or {}
    username = datos.get('username')
    password = datos.get('password')

    if not username or not password:
        return jsonify({"error": "username y password son obligatorios"}), 400

    fila = fetch_one("""SELECT c.id_cliente, cu.password_hash, cu.estado cuenta_estado, c.estado cliente_estado
        FROM cuentas cu JOIN clientes c ON c.id_cliente=cu.id_cliente WHERE cu.usuario=%s""", (str(username).strip(),))

    # Mismo mensaje si el usuario no existe, está inactivo o la clave es incorrecta,
    # así no se revela cuáles usuarios existen
    if (fila is None or fila['cuenta_estado'] != 'ACTIVA' or fila['cliente_estado'] != 'ACTIVO'
            or not fila['password_hash'] or not check_password_hash(fila['password_hash'], password)):
        return jsonify({"error": "Credenciales inválidas"}), 401

    ahora = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        "sub": str(fila['id_cliente']),   # identificador del usuario (debe ser texto)
        "username": str(username).strip(),
        "iat": ahora,                     # fecha de emisión
        "exp": ahora + datetime.timedelta(minutes=JWT_MINUTES)  # expira en JWT_MINUTES
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)

    return jsonify({
        "token": token,
        "tipo": "Bearer",
        "expira_en_minutos": JWT_MINUTES
    }), 200
