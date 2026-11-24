
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from psycopg.errors import UniqueViolation

from comun.db import connect, fetch_all, fetch_one
from comun.config import CORS_ORIGINS, COMISION_MB
from comun.auth_routes import login_bp
from comun.security import require_auth, error
from comun.serializers import clean

app = Flask(__name__)
CORS(app, origins=CORS_ORIGINS)
app.register_blueprint(login_bp)


@app.post('/api/compras/favoritos')
@require_auth
def agregar_favorito():
    data = request.get_json(silent=True) or {}
    pid = data.get('id_producto')

    if type(pid) is not int:
        return error('id_producto entero es obligatorio')

    if not fetch_one(
        """SELECT id_producto FROM productos
           WHERE id_producto=%s AND estado='ACTIVO'""",
        (pid,)
    ):
        return error('Producto no encontrado', 404)

    conn = connect()
    try:
        with conn.cursor() as c:
            c.execute(
                """INSERT INTO favoritos
                   (id_cliente, id_producto)
                   VALUES (%s, %s)""",
                (g.user_id, pid)
            )

        conn.commit()
        return jsonify({
            'mensaje': 'Producto agregado a favoritos',
            'id_producto': pid
        }), 201

    except UniqueViolation:
        conn.rollback()
        return error('El producto ya está en favoritos', 409)

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


@app.get('/api/compras/favoritos')
@require_auth
def listar_favoritos():
    rows = clean(fetch_all("""
        SELECT p.id_producto,
               p.nombre AS producto,
               m.nombre AS marca,
               p.precio,
               f.fecha_agregado
        FROM favoritos f
        JOIN productos p
          ON p.id_producto=f.id_producto
        JOIN marcas m
          ON m.id_marca=p.id_marca
        WHERE f.id_cliente=%s
        ORDER BY f.fecha_agregado DESC
    """, (g.user_id,)))

    return jsonify({
        'total': len(rows),
        'favoritos': rows
    })


@app.delete('/api/compras/favoritos/<int:producto_id>')
@require_auth
def quitar_favorito(producto_id):
    conn = connect()

    try:
        with conn.cursor() as c:
            c.execute(
                """DELETE FROM favoritos
                   WHERE id_cliente=%s
                     AND id_producto=%s""",
                (g.user_id, producto_id)
            )
            eliminados = c.rowcount

        conn.commit()

        if eliminados == 0:
            return error(
                'El producto no estaba en favoritos', 404
            )

        return jsonify({
            'mensaje': 'Favorito eliminado',
            'id_producto': producto_id
        })

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


@app.post('/api/compras/procesar')
@require_auth
def procesar_compra():
    data = request.get_json(silent=True) or {}
    pid = data.get('id_producto')
    cantidad = data.get('cantidad', 1)
    talla = data.get('talla')

    if (
        type(pid) is not int
        or type(cantidad) is not int
        or cantidad < 1
        or not isinstance(talla, str)
        or not talla.strip()
    ):
        return error(
            'Envíe id_producto, cantidad positiva y talla'
        )

    conn = connect()

    try:
        with conn.cursor() as c:
            c.execute("""
                SELECT p.id_producto,
                       p.nombre,
                       p.precio,
                       p.stock,
                       COALESCE((
                           SELECT MAX(d.porcentaje)
                           FROM descuentos d
                           WHERE d.id_producto=p.id_producto
                             AND d.estado='ACTIVO'
                             AND CURRENT_DATE BETWEEN
                                 d.fecha_inicio AND d.fecha_fin
                       ), 0) AS descuento
                FROM productos p
                WHERE p.id_producto=%s
                  AND p.estado='ACTIVO'
                FOR UPDATE
            """, (pid,))

            p = c.fetchone()

            if not p:
                conn.rollback()
                return error('Producto no encontrado', 404)

            if p['stock'] < cantidad:
                conn.rollback()
                return error(
                    'Stock insuficiente',
                    409,
                    stock_disponible=p['stock']
                )

            c.execute("SELECT stock FROM producto_tallas WHERE id_producto=%s AND talla=%s FOR UPDATE", (pid, talla))
            variante = c.fetchone()
            if not variante or variante['stock'] < cantidad:
                conn.rollback()
                return error('Stock insuficiente para la talla seleccionada', 409)
            c.execute("UPDATE producto_tallas SET stock=stock-%s WHERE id_producto=%s AND talla=%s", (cantidad, pid, talla))
            original = float(p['precio']) * cantidad
            descuento = float(p['descuento'])

            total = round(
                original * (1 - descuento / 100), 2
            )

            comision = round(total * COMISION_MB, 2)
            valor_marca = round(total - comision, 2)

            c.execute("""
                INSERT INTO pagos(
                    id_cliente,
                    id_producto,
                    precio_original,
                    porcentaje_descuento,
                    total_pagado,
                    comision_mb,
                    valor_marca,
                    talla, cantidad, estado_pago
                )
                VALUES(
                    %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, 'APROBADO'
                )
                RETURNING id_pago
            """, (
                g.user_id,
                pid,
                original,
                descuento,
                total,
                comision,
                valor_marca, talla, cantidad
            ))

            pago_id = c.fetchone()['id_pago']

            c.execute("""
                UPDATE productos
                SET stock=stock-%s
                WHERE id_producto=%s
            """, (cantidad, pid))

        conn.commit()

        return jsonify({
            'mensaje': 'Compra simulada procesada',
            'id_pago': pago_id,
            'producto': p['nombre'],
            'cantidad': cantidad,
            'talla': talla,
            'precio_original': round(original, 2),
            'descuento_porcentaje': descuento,
            'total_pagado': total,
            'comision_mb': comision,
            'valor_marca': valor_marca,
            'estado_pago': 'APROBADO',
            'nota': 'No se realiza un cobro bancario real'
        }), 201

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


@app.get('/api/compras/<int:pago_id>/estado')
@require_auth
def estado_compra(pago_id):
    row = fetch_one("""
        SELECT pg.id_pago, pg.talla, pg.cantidad,
               pg.estado_pago,
               pg.fecha_pago,
               pg.precio_original,
               pg.porcentaje_descuento,
               pg.total_pagado,
               pg.comision_mb,
               pg.valor_marca,
               p.nombre AS producto
        FROM pagos pg
        JOIN productos p
          ON p.id_producto=pg.id_producto
        WHERE pg.id_pago=%s
          AND pg.id_cliente=%s
    """, (pago_id, g.user_id))

    if not row:
        return error(
            'Compra no encontrada para este usuario', 404
        )

    return jsonify(clean(row))



@app.errorhandler(404)
def not_found(_):
    return jsonify({
        'error': 'Ruta no encontrada'
    }), 404


@app.errorhandler(500)
def internal(_):
    return jsonify({
        'error': 'Error interno. Revise la consola del servicio.'
    }), 500


if __name__ == '__main__':
    app.run(
        host='127.0.0.1',
        port=5002,
        debug=False
    )
