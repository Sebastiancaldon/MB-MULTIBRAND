
from collections import defaultdict
from decimal import Decimal

from flask import Flask, request, jsonify, g
from flask_cors import CORS
from psycopg.errors import UniqueViolation, IntegrityError

from comun.db import connect, fetch_all, fetch_one
from comun.auth_routes import login_bp
from comun.security import require_auth, error
from comun.serializers import clean


# ============================================================
# CONFIGURACION
# ============================================================

app = Flask(__name__)

CORS(
    app,
    resources={
        r"/api/*": {
            "origins": [
                "https://mb-multibrand.vercel.app"
            ],
            "methods": [
                "GET", "POST", "PUT",
                "PATCH", "DELETE", "OPTIONS"
            ],
            "allow_headers": [
                "Content-Type", "Authorization"
            ]
        }
    }
)

app.register_blueprint(login_bp)

PRIOR_VOTOS = 3
UMBRAL_RECOMIENDA = 4


# ============================================================
# CONSULTA DE DESCUENTOS VIGENTES
# ============================================================

DESCUENTO_VIGENTE = """
LEFT JOIN LATERAL (
    SELECT MAX(d.porcentaje) AS porcentaje
    FROM descuentos d
    WHERE d.id_producto = p.id_producto
      AND d.estado = 'ACTIVO'
      AND CURRENT_DATE BETWEEN
          d.fecha_inicio AND d.fecha_fin
) d ON TRUE
"""


# ============================================================
# UTILIDADES
# ============================================================

def media_global():
    row = fetch_one("""
        SELECT AVG(puntuacion) AS m
        FROM calificaciones
    """)
    return (
        float(row["m"])
        if row and row["m"] is not None
        else 3.0
    )


def puntaje_ponderado(promedio, votos, media):
    return round(
        (votos / (votos + PRIOR_VOTOS)) * promedio
        + (PRIOR_VOTOS / (votos + PRIOR_VOTOS)) * media,
        3
    )


def producto_activo(pid):
    return fetch_one("""
        SELECT p.id_producto,
               p.nombre,
               p.categoria,
               m.nombre AS marca
        FROM productos p
        JOIN marcas m ON m.id_marca = p.id_marca
        WHERE p.id_producto = %s
          AND p.estado = 'ACTIVO'
    """, (pid,))


def estadisticas_producto(pid):
    row = fetch_one("""
        SELECT
            COUNT(*) AS total,
            COALESCE(AVG(puntuacion), 0) AS promedio,
            COUNT(*) FILTER (
                WHERE puntuacion >= %s
            ) AS recomiendan,
            COUNT(*) FILTER (WHERE puntuacion = 1) AS e1,
            COUNT(*) FILTER (WHERE puntuacion = 2) AS e2,
            COUNT(*) FILTER (WHERE puntuacion = 3) AS e3,
            COUNT(*) FILTER (WHERE puntuacion = 4) AS e4,
            COUNT(*) FILTER (WHERE puntuacion = 5) AS e5
        FROM calificaciones
        WHERE id_producto = %s
    """, (UMBRAL_RECOMIENDA, pid))

    total = int(row["total"])
    promedio = float(row["promedio"])

    return {
        "total_calificaciones": total,
        "promedio": round(promedio, 2),
        "puntaje_ponderado": (
            puntaje_ponderado(
                promedio, total, media_global()
            ) if total else None
        ),
        "porcentaje_recomiendan": (
            round(
                float(row["recomiendan"]) * 100 / total,
                1
            ) if total else 0.0
        ),
        "distribucion": {
            str(i): int(row[f"e{i}"])
            for i in range(5, 0, -1)
        }
    }


# ============================================================
# CALIFICAR PRODUCTO
# ============================================================

@app.post("/api/calificaciones/producto/<int:producto_id>")
@require_auth
def calificar(producto_id):
    data = request.get_json(silent=True) or {}

    puntuacion = data.get("puntuacion")
    comentario = data.get("comentario")

    if (
        type(puntuacion) is not int
        or not 1 <= puntuacion <= 5
    ):
        return error(
            "puntuacion debe ser un entero entre 1 y 5"
        )

    if comentario is not None:
        if (
            not isinstance(comentario, str)
            or len(comentario.strip()) > 255
        ):
            return error(
                "comentario debe tener maximo 255 caracteres"
            )
        comentario = comentario.strip() or None

    if not producto_activo(producto_id):
        return error("Producto no encontrado", 404)

    compra = fetch_one("""
        SELECT COUNT(*) AS n
        FROM pagos
        WHERE id_cliente = %s
          AND id_producto = %s
          AND estado_pago = 'APROBADO'
    """, (g.user_id, producto_id))

    if not compra or not compra["n"]:
        return error(
            "Solo puede calificar productos comprados",
            403
        )

    conn = connect()
    existente = False

    try:
        with conn.cursor() as c:
            c.execute("""
                SELECT id_calificacion
                FROM calificaciones
                WHERE id_cliente = %s
                  AND id_producto = %s
                FOR UPDATE
            """, (g.user_id, producto_id))

            anterior = c.fetchone()
            existente = bool(anterior)

            if existente:
                c.execute("""
                    UPDATE calificaciones
                    SET puntuacion = %s,
                        comentario = %s,
                        fecha = CURRENT_TIMESTAMP
                    WHERE id_calificacion = %s
                """, (
                    puntuacion,
                    comentario,
                    anterior["id_calificacion"]
                ))
            else:
                c.execute("""
                    INSERT INTO calificaciones (
                        id_cliente,
                        id_producto,
                        puntuacion,
                        comentario
                    )
                    VALUES (%s, %s, %s, %s)
                """, (
                    g.user_id,
                    producto_id,
                    puntuacion,
                    comentario
                ))

        conn.commit()

    except IntegrityError:
        conn.rollback()
        return error(
            "No fue posible registrar la calificacion",
            409
        )

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

    return jsonify({
        "mensaje": (
            "Calificacion actualizada"
            if existente else "Calificacion registrada"
        ),
        "id_producto": producto_id,
        "puntuacion": puntuacion,
        "comentario": comentario,
        "compra_verificada": True,
        "resumen_producto": estadisticas_producto(
            producto_id
        )
    }), (200 if existente else 201)


# ============================================================
# CALIFICACIONES PENDIENTES
# ============================================================

@app.get("/api/calificaciones/pendientes")
@require_auth
def pendientes():
    rows = clean(fetch_all("""
        SELECT
            p.id_producto,
            p.nombre AS producto,
            m.nombre AS marca,
            p.categoria,
            COUNT(pg.id_pago) AS compras,
            MAX(pg.fecha_pago) AS ultima_compra
        FROM pagos pg
        JOIN productos p
          ON p.id_producto = pg.id_producto
        JOIN marcas m
          ON m.id_marca = p.id_marca
        WHERE pg.id_cliente = %s
          AND pg.estado_pago = 'APROBADO'
          AND NOT EXISTS (
              SELECT 1
              FROM calificaciones k
              WHERE k.id_cliente = pg.id_cliente
                AND k.id_producto = pg.id_producto
          )
        GROUP BY
            p.id_producto,
            p.nombre,
            m.nombre,
            p.categoria
        ORDER BY ultima_compra DESC
    """, (g.user_id,)))

    return jsonify({
        "total": len(rows),
        "pendientes_por_calificar": rows
    })


# ============================================================
# RESUMEN DE PRODUCTO
# ============================================================

@app.get(
    "/api/calificaciones/producto/<int:producto_id>/resumen"
)
def resumen_producto(producto_id):
    prod = producto_activo(producto_id)

    if not prod:
        return error("Producto no encontrado", 404)

    comentarios = clean(fetch_all("""
        SELECT
            cl.nombre AS cliente,
            k.puntuacion,
            k.comentario,
            k.fecha
        FROM calificaciones k
        JOIN clientes cl
          ON cl.id_cliente = k.id_cliente
        WHERE k.id_producto = %s
          AND k.comentario IS NOT NULL
        ORDER BY k.fecha DESC
        LIMIT 5
    """, (producto_id,)))

    return jsonify({
        "producto": clean(prod),
        **estadisticas_producto(producto_id),
        "ultimos_comentarios": comentarios,
        "mi_calificacion": None
    })


# ============================================================
# RESUMENES PUBLICOS
# ============================================================

@app.get("/api/calificaciones/resumenes")
def resumenes_publicos():
    rows = fetch_all("""
        SELECT
            id_producto,
            COUNT(*) AS votos,
            ROUND(AVG(puntuacion), 2) AS promedio
        FROM calificaciones
        GROUP BY id_producto
    """)

    return jsonify({
        "resumenes": clean(rows)
    })


# ============================================================
# RANKING DE PRODUCTOS
# ============================================================

@app.get("/api/calificaciones/ranking")
def ranking():
    categoria = request.args.get("categoria")
    marca = request.args.get("marca")

    minimo = request.args.get(
        "minimo_votos", default=1, type=int
    )
    limite = request.args.get(
        "limite", default=10, type=int
    )

    if (
        minimo is None or minimo < 1
        or limite is None
        or not 1 <= limite <= 50
    ):
        return error("Parametros invalidos")

    sql = f"""
        SELECT
            p.id_producto,
            p.nombre AS producto,
            p.categoria,
            m.nombre AS marca,
            p.precio,
            COALESCE(d.porcentaje, 0) AS descuento,
            COUNT(k.id_calificacion) AS votos,
            AVG(k.puntuacion) AS promedio
        FROM productos p
        JOIN marcas m
          ON m.id_marca = p.id_marca
        JOIN calificaciones k
          ON k.id_producto = p.id_producto
        {DESCUENTO_VIGENTE}
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

    sql += """
        GROUP BY
            p.id_producto,
            p.nombre,
            p.categoria,
            m.nombre,
            p.precio,
            d.porcentaje
        HAVING COUNT(k.id_calificacion) >= %s
    """

    args.append(minimo)

    media = media_global()
    items = []

    for r in fetch_all(sql, tuple(args)):
        votos = int(r["votos"])
        prom = float(r["promedio"])

        items.append({
            **clean(r),
            "votos": votos,
            "promedio": round(prom, 2),
            "puntaje_ponderado": puntaje_ponderado(
                prom, votos, media
            )
        })

    items.sort(
        key=lambda x: (
            -x["puntaje_ponderado"],
            -x["votos"]
        )
    )

    items = items[:limite]

    for pos, item in enumerate(items, 1):
        item["posicion"] = pos

    return jsonify({
        "criterio": (
            f"Promedio bayesiano "
            f"(prior={PRIOR_VOTOS} votos, "
            f"media global={round(media, 2)})"
        ),
        "total": len(items),
        "ranking": items
    })


# ============================================================
# RECOMENDACIONES PERSONALIZADAS
# ============================================================

@app.get("/api/calificaciones/recomendaciones")
@require_auth
def recomendaciones():
    limite = request.args.get(
        "limite", default=5, type=int
    )

    if limite is None or not 1 <= limite <= 20:
        return error("limite debe estar entre 1 y 20")

    uid = g.user_id

    afin_cat = defaultdict(float)
    afin_marca = defaultdict(float)

    senales = [
        (
            2,
            """
            SELECT p.categoria, p.id_marca
            FROM favoritos f
            JOIN productos p
              ON p.id_producto = f.id_producto
            WHERE f.id_cliente = %s
            """
        ),
        (
            3,
            """
            SELECT p.categoria, p.id_marca
            FROM pagos pg
            JOIN productos p
              ON p.id_producto = pg.id_producto
            WHERE pg.id_cliente = %s
              AND pg.estado_pago = 'APROBADO'
            """
        ),
        (
            2,
            """
            SELECT p.categoria, p.id_marca
            FROM calificaciones k
            JOIN productos p
              ON p.id_producto = k.id_producto
            WHERE k.id_cliente = %s
              AND k.puntuacion >= 4
            """
        ),
        (
            -2,
            """
            SELECT p.categoria, p.id_marca
            FROM calificaciones k
            JOIN productos p
              ON p.id_producto = k.id_producto
            WHERE k.id_cliente = %s
              AND k.puntuacion <= 2
            """
        )
    ]

    historial = 0

    for peso, sql in senales:
        for r in fetch_all(sql, (uid,)):
            afin_cat[r["categoria"]] += peso
            afin_marca[r["id_marca"]] += peso
            historial += 1

    valores = (
        list(afin_cat.values())
        + list(afin_marca.values())
    )

    max_afin = max(
        [abs(v) for v in valores] or [1]
    ) or 1

    comprados = {
        r["id_producto"]
        for r in fetch_all("""
            SELECT DISTINCT id_producto
            FROM pagos
            WHERE id_cliente = %s
              AND estado_pago = 'APROBADO'
        """, (uid,))
    }

    favoritos = {
        r["id_producto"]
        for r in fetch_all("""
            SELECT id_producto
            FROM favoritos
            WHERE id_cliente = %s
        """, (uid,))
    }

    media = media_global()

    candidatos = fetch_all(f"""
        SELECT
            p.id_producto,
            p.nombre AS producto,
            p.categoria,
            p.id_marca,
            m.nombre AS marca,
            p.precio,
            p.stock,
            COALESCE(d.porcentaje, 0) AS descuento,
            ROUND(
                p.precio *
                (1 - COALESCE(d.porcentaje, 0) / 100),
                2
            ) AS precio_final,
            (
                SELECT COUNT(*)
                FROM calificaciones k
                WHERE k.id_producto = p.id_producto
            ) AS votos,
            (
                SELECT AVG(k.puntuacion)
                FROM calificaciones k
                WHERE k.id_producto = p.id_producto
            ) AS promedio
        FROM productos p
        JOIN marcas m
          ON m.id_marca = p.id_marca
        {DESCUENTO_VIGENTE}
        WHERE p.estado = 'ACTIVO'
          AND m.estado = 'ACTIVA'
          AND p.stock > 0
    """)

    resultado = []

    for p in candidatos:
        if p["id_producto"] in comprados:
            continue

        votos = int(p["votos"])

        prom = (
            float(p["promedio"])
            if p["promedio"] is not None
            else media
        )

        ponderado = (
            puntaje_ponderado(prom, votos, media)
            if votos else media
        )

        a_cat = afin_cat.get(p["categoria"], 0)
        a_marca = afin_marca.get(p["id_marca"], 0)

        afinidad = (
            (a_cat + a_marca) / (2 * max_afin)
        )

        descuento = float(p["descuento"])

        score = (
            0.6 * afinidad
            + 0.3 * (ponderado / 5)
            + 0.1 * (descuento / 100)
        )

        motivos = []

        if a_marca > 0:
            motivos.append(
                f"Te interesa la marca {p['marca']}"
            )

        if a_cat > 0:
            motivos.append(
                f"Te interesa la categoria {p['categoria']}"
            )

        if p["id_producto"] in favoritos:
            motivos.append("Esta en tus favoritos")

        if votos and ponderado >= 4:
            motivos.append(
                f"Muy bien calificado ({round(prom, 1)} "
                f"estrellas en {votos} votos)"
            )

        if descuento > 0:
            motivos.append(
                f"Tiene {descuento:g}% de descuento vigente"
            )

        if a_marca < 0 or a_cat < 0:
            motivos.append(
                "Calificaste mal productos similares"
            )

        resultado.append({
            "id_producto": p["id_producto"],
            "producto": p["producto"],
            "marca": p["marca"],
            "categoria": p["categoria"],
            "precio": float(p["precio"]),
            "descuento": descuento,
            "precio_final": float(p["precio_final"]),
            "calificacion_promedio": (
                round(prom, 2) if votos else None
            ),
            "votos": votos,
            "score": round(score, 4),
            "motivos": motivos or [
                "Producto disponible en el catalogo"
            ]
        })

    resultado.sort(
        key=lambda x: -x["score"]
    )

    resultado = resultado[:limite]

    for pos, item in enumerate(resultado, 1):
        item["posicion"] = pos

    return jsonify({
        "personalizado": historial > 0,
        "senales_historial": historial,
        "total": len(resultado),
        "recomendaciones": resultado
    })


# ============================================================
# REPUTACION DE MARCAS
# ============================================================

@app.get("/api/calificaciones/marcas/reputacion")
def reputacion_marcas():
    media = media_global()

    marcas = fetch_all("""
        SELECT id_marca, nombre, canal_oficial
        FROM marcas
        WHERE estado = 'ACTIVA'
    """)

    productos = fetch_all(f"""
        SELECT
            p.id_producto,
            p.nombre,
            p.id_marca,
            COUNT(k.id_calificacion) AS votos,
            AVG(k.puntuacion) AS promedio,
            COALESCE(d.porcentaje, 0) AS descuento
        FROM productos p
        LEFT JOIN calificaciones k
          ON k.id_producto = p.id_producto
        {DESCUENTO_VIGENTE}
        WHERE p.estado = 'ACTIVO'
        GROUP BY
            p.id_producto,
            p.nombre,
            p.id_marca,
            d.porcentaje
    """)

    por_marca = defaultdict(list)

    for p in productos:
        por_marca[p["id_marca"]].append(p)

    salida = []

    for marca in marcas:
        ps = por_marca.get(
            marca["id_marca"], []
        )

        votos = sum(
            int(p["votos"]) for p in ps
        )

        suma = sum(
            float(p["promedio"]) * int(p["votos"])
            for p in ps if p["votos"]
        )

        promedio = (
            suma / votos if votos else None
        )

        ponderado = (
            puntaje_ponderado(
                promedio, votos, media
            ) if votos else None
        )

        calificados = [
            p for p in ps if p["votos"]
        ]

        mejor = max(
            calificados,
            key=lambda p: puntaje_ponderado(
                float(p["promedio"]),
                int(p["votos"]),
                media
            ),
            default=None
        )

        if ponderado is None:
            nivel = "SIN_DATOS"
        elif ponderado >= 4.5:
            nivel = "EXCELENTE"
        elif ponderado >= 3.5:
            nivel = "BUENA"
        elif ponderado >= 2.5:
            nivel = "REGULAR"
        else:
            nivel = "BAJA"

        descuento_medio = (
            round(
                sum(
                    float(p["descuento"])
                    for p in ps
                ) / len(ps),
                1
            ) if ps else 0.0
        )

        salida.append({
            "id_marca": marca["id_marca"],
            "marca": marca["nombre"],
            "canal_oficial": marca["canal_oficial"],
            "productos_activos": len(ps),
            "productos_calificados": len(calificados),
            "total_votos": votos,
            "promedio": (
                round(promedio, 2)
                if promedio is not None else None
            ),
            "puntaje_ponderado": ponderado,
            "nivel": nivel,
            "mejor_producto": (
                mejor["nombre"] if mejor else None
            ),
            "descuento_promedio_vigente": descuento_medio
        })

    salida.sort(
        key=lambda x: (
            x["puntaje_ponderado"] is None,
            -(x["puntaje_ponderado"] or 0)
        )
    )

    return jsonify({
        "total": len(salida),
        "marcas": clean(salida)
    })


# ============================================================
# MANEJO DE ERRORES
# ============================================================

@app.errorhandler(404)
def not_found(_):
    return jsonify({
        "error": "Ruta no encontrada"
    }), 404


@app.errorhandler(405)
def not_allowed(_):
    return jsonify({
        "error": "Metodo no permitido"
    }), 405


@app.errorhandler(500)
def internal(_):
    return jsonify({
        "error": "Error interno. Revise los logs de Vercel."
    }), 500


# ============================================================
# EJECUCION LOCAL
# ============================================================

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5004,
        debug=False
    )
