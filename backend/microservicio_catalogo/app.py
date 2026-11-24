
from flask import Flask, request, jsonify
from flask_cors import CORS

from comun.db import fetch_all, fetch_one
from comun.config import CORS_ORIGINS
from comun.auth_routes import login_bp
from comun.security import error
from comun.serializers import clean

app = Flask(__name__)

CORS(app, origins=CORS_ORIGINS)

# Autenticación
app.register_blueprint(login_bp)


@app.get('/api/catalogo/ofertas')
def ofertas():
    categoria = request.args.get('categoria')
    marca = request.args.get('marca')
    max_precio = request.args.get(
        'max_precio', type=float
    )

    sql = """
        SELECT
            p.id_producto,
            p.nombre AS producto,
            p.categoria,
            m.nombre AS marca,
            p.precio,
            p.stock,
            COALESCE(d.porcentaje, 0) AS descuento,
            ROUND(
                p.precio *
                (1 - COALESCE(d.porcentaje, 0) / 100),
                2
            ) AS precio_final

        FROM productos p

        JOIN marcas m
            ON m.id_marca = p.id_marca

        LEFT JOIN descuentos d
            ON d.id_producto = p.id_producto
            AND d.estado = 'ACTIVO'
            AND CURRENT_DATE
                BETWEEN d.fecha_inicio AND d.fecha_fin

        WHERE p.estado = 'ACTIVO'
          AND m.estado = 'ACTIVA'
    """

    args = []

    if categoria:
        sql += " AND p.categoria = %s"
        args.append(categoria)

    if marca:
        sql += " AND m.nombre = %s"
        args.append(marca)

    if max_precio is not None:
        sql += """
            AND p.precio *
            (1 - COALESCE(d.porcentaje, 0) / 100)
            <= %s
        """
        args.append(max_precio)

    sql += " ORDER BY precio_final ASC"

    rows = clean(fetch_all(sql, args))

    return jsonify({
        'total': len(rows),
        'ofertas': rows
    })


@app.get('/api/catalogo/ofertas/mejores')
def mejores():
    sql = """
        SELECT
            p.id_producto,
            p.nombre AS producto,
            m.nombre AS marca,
            p.precio,
            d.porcentaje AS descuento,
            ROUND(
                p.precio * (1 - d.porcentaje / 100),
                2
            ) AS precio_final

        FROM productos p

        JOIN marcas m
            ON m.id_marca = p.id_marca

        JOIN descuentos d
            ON d.id_producto = p.id_producto

        WHERE p.estado = 'ACTIVO'
          AND d.estado = 'ACTIVO'
          AND CURRENT_DATE
              BETWEEN d.fecha_inicio AND d.fecha_fin

        ORDER BY d.porcentaje DESC
        LIMIT 5
    """

    rows = clean(fetch_all(sql))

    return jsonify({
        'criterio': 'Mayor porcentaje de descuento vigente',
        'ofertas': rows
    })


@app.get('/api/catalogo/productos/<int:producto_id>')
def detalle(producto_id):
    sql = """
        SELECT
            p.id_producto,
            p.nombre AS producto,
            p.categoria,
            p.descripcion,
            m.nombre AS marca,
            p.precio,
            p.stock,
            COALESCE(d.porcentaje, 0) AS descuento,
            ROUND(
                p.precio *
                (1 - COALESCE(d.porcentaje, 0) / 100),
                2
            ) AS precio_final

        FROM productos p

        JOIN marcas m
            ON m.id_marca = p.id_marca

        LEFT JOIN descuentos d
            ON d.id_producto = p.id_producto
            AND d.estado = 'ACTIVO'
            AND CURRENT_DATE
                BETWEEN d.fecha_inicio AND d.fecha_fin

        WHERE p.id_producto = %s
          AND p.estado = 'ACTIVO'
    """

    row = fetch_one(sql, (producto_id,))

    if not row:
        return error(
            'Producto no encontrado', 404
        )

    row["tallas"] = fetch_all("SELECT talla, stock FROM producto_tallas WHERE id_producto=%s ORDER BY id_producto_talla", (producto_id,))
    return jsonify(clean(row))


@app.get('/api/catalogo/marcas')
def marcas():
    sql = """
        SELECT
            id_marca,
            nombre,
            descripcion,
            canal_oficial

        FROM marcas

        WHERE estado = 'ACTIVA'
        ORDER BY nombre
    """

    return jsonify({
        'marcas': clean(fetch_all(sql))
    })


@app.get('/api/catalogo/categorias')
def categorias():
    sql = """
        SELECT DISTINCT categoria
        FROM productos
        WHERE estado = 'ACTIVO'
        ORDER BY categoria
    """

    return jsonify({
        'categorias': clean(fetch_all(sql))
    })


@app.get('/api/catalogo/diagnostico')
def diagnostico():
    return jsonify({
        'ruta_recibida': request.path,
        'servicio': 'catalogo',
        'estado': 'activo'
    })

@app.before_request
def diagnosticar_ruta():
    print(
        "RUTA RECIBIDA:",
        request.path,
        "RUTA ORIGINAL:",
        request.environ.get("RAW_URI"),
        flush=True
    )

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
        port=5001,
        debug=False
    )
