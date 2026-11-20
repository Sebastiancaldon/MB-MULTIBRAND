
"""
Autenticación compartida de MB MULTIBRAND.

POST /register -> Registrar usuario
POST /login    -> Iniciar sesión y obtener JWT

Compatible con PostgreSQL y Supabase.
"""

import datetime
import jwt

from flask import Blueprint, request, jsonify
from psycopg.errors import UniqueViolation
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from comun.config import JWT_SECRET, JWT_MINUTES
from comun.db import connect, fetch_one
from comun.security import ALGORITHM

login_bp = Blueprint('login_bp', __name__)


# REGISTRO DE USUARIOS
@login_bp.route('/register', methods=['POST'])
def registrar_usuario():

    datos = request.get_json(silent=True) or {}

    username = str(
        datos.get('username') or ''
    ).strip()

    password = datos.get('password')

    nombre = str(
        datos.get('nombre') or ''
    ).strip()

    correo = str(
        datos.get('correo') or ''
    ).strip().lower()

    if (
        not username
        or not isinstance(password, str)
        or not password
        or not nombre
        or not correo
    ):
        return jsonify({
            "error": (
                "username, password, nombre "
                "y correo son obligatorios"
            )
        }), 400

    if len(password) < 8:
        return jsonify({
            "error": (
                "La contraseña debe tener "
                "al menos 8 caracteres"
            )
        }), 400

    password_hash = generate_password_hash(password)

    conn = connect()

    try:
        with conn.cursor() as c:

            # Crear cliente y recuperar ID
            c.execute("""
                INSERT INTO clientes(nombre, correo)
                VALUES (%s, %s)
                RETURNING id_cliente
            """, (nombre, correo))

            cliente_id = c.fetchone()['id_cliente']

            # Crear cuenta vinculada al cliente
            c.execute("""
                INSERT INTO cuentas(
                    id_cliente,
                    usuario,
                    password_hash
                )
                VALUES (%s, %s, %s)
            """, (
                cliente_id,
                username,
                password_hash
            ))

        conn.commit()

        return jsonify({
            "mensaje": "Usuario registrado exitosamente"
        }), 201

    except UniqueViolation:
        conn.rollback()

        return jsonify({
            "error": (
                "El usuario o correo "
                "ya se encuentra registrado"
            )
        }), 409

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


# INICIO DE SESIÓN
@login_bp.route('/login', methods=['POST'])
def login():

    datos = request.get_json(silent=True) or {}

    username = datos.get('username')
    password = datos.get('password')

    if (
        not isinstance(username, str)
        or not username.strip()
        or not isinstance(password, str)
        or not password
    ):
        return jsonify({
            "error": (
                "username y password "
                "son obligatorios"
            )
        }), 400

    username = username.strip()

    fila = fetch_one("""
        SELECT
            c.id_cliente,
            cu.password_hash,
            cu.estado AS cuenta_estado,
            c.estado AS cliente_estado

        FROM cuentas cu

        JOIN clientes c
            ON c.id_cliente = cu.id_cliente

        WHERE cu.usuario = %s
    """, (username,))

    if (
        fila is None
        or fila['cuenta_estado'] != 'ACTIVA'
        or fila['cliente_estado'] != 'ACTIVO'
        or not fila['password_hash']
        or not check_password_hash(
            fila['password_hash'],
            password
        )
    ):
        return jsonify({
            "error": "Credenciales inválidas"
        }), 401

    ahora = datetime.datetime.now(
        datetime.timezone.utc
    )

    payload = {
        "sub": str(fila['id_cliente']),
        "username": username,
        "iat": ahora,
        "exp": ahora + datetime.timedelta(
            minutes=JWT_MINUTES
        )
    }

    token = jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=ALGORITHM
    )

    return jsonify({
        "token": token,
        "tipo": "Bearer",
        "expira_en_minutos": JWT_MINUTES
    }), 200
