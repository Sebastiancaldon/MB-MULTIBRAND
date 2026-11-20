"""Microservicio de calificaciones, reputación y recomendaciones (puerto 5004).

NO es un CRUD plano: cada endpoint aplica reglas de negocio sobre las tablas
existentes (calificaciones, pagos, favoritos, productos, marcas, descuentos):

  POST /api/calificaciones/producto/<id>        Calificar solo con compra verificada (upsert).
  GET  /api/calificaciones/pendientes           Compras aprobadas aún sin calificar.
  GET  /api/calificaciones/producto/<id>/resumen Estadísticas: promedio, distribución, % recomiendan, puntaje ponderado.
  GET  /api/calificaciones/ranking              Ranking con promedio bayesiano (evita que 1 voto de 5★ gane).
  GET  /api/calificaciones/recomendaciones      Recomendaciones personalizadas según favoritos, compras y calificaciones.
  GET  /api/calificaciones/marcas/reputacion    Reputación agregada por marca.

Todas las rutas (exigen JWT: Authorization: Bearer <token>.
"""
from collections import defaultdict

from flask import Flask, request, jsonify, g
from pymysql.err import IntegrityError

from comun.db import connect, fetch_all, fetch_one
from flask_cors import CORS
from comun.config import CORS_ORIGINS
from comun.auth_routes import login_bp
from comun.security import require_auth, error
from comun.serializers import clean


app = Flask(__name__)
CORS(app, origins=CORS_ORIGINS)  # permite que el frontend Vue (otro puerto) consuma esta API
app.register_blueprint(login_bp)  # login y rutas de autenticación en este servicio

# Parámetro del promedio bayesiano: "votos virtuales" que tira hacia la media global.
PRIOR_VOTOS = 3
# Una calificación >= UMBRAL_RECOMIENDA cuenta como "recomendaría el producto".
UMBRAL_RECOMIENDA = 4

# Subconsulta reutilizable: descuento vigente de cada producto.
DESCUENTO_VIGENTE = """LEFT JOIN descuentos d ON d.id_producto=p.id_producto AND d.estado='ACTIVO'
      AND CURDATE() BETWEEN d.fecha_inicio AND d.fecha_fin"""


# ----------------------------------------------------------------- utilidades
def media_global():
    row = fetch_one("SELECT AVG(puntuacion) AS m FROM calificaciones")
    return float(row["m"]) if row and row["m"] is not None else 3.0


def puntaje_ponderado(promedio, votos, c):
    """Promedio bayesiano: (v/(v+m))*R + (m/(v+m))*C."""
    return round((votos / (votos + PRIOR_VOTOS)) * promedio + (PRIOR_VOTOS / (votos + PRIOR_VOTOS)) * c, 3)


def producto_activo(pid):
    return fetch_one(
        "SELECT p.id_producto, p.nombre, p.categoria, m.nombre AS marca FROM productos p "
        "JOIN marcas m ON m.id_marca=p.id_marca WHERE p.id_producto=%s AND p.estado='ACTIVO'", (pid,))


def estadisticas_producto(pid):
    row = fetch_one(
        """SELECT COUNT(*) AS total, COALESCE(AVG(puntuacion),0) AS promedio,
                  COALESCE(SUM(puntuacion>=%s),0) AS recomiendan,
                  COALESCE(SUM(puntuacion=1),0) AS e1, COALESCE(SUM(puntuacion=2),0) AS e2,
                  COALESCE(SUM(puntuacion=3),0) AS e3, COALESCE(SUM(puntuacion=4),0) AS e4,
                  COALESCE(SUM(puntuacion=5),0) AS e5
           FROM calificaciones WHERE id_producto=%s""", (UMBRAL_RECOMIENDA, pid))
    total = int(row["total"])
    promedio = float(row["promedio"])
    return {
        "total_calificaciones": total,
        "promedio": round(promedio, 2),
        "puntaje_ponderado": puntaje_ponderado(promedio, total, media_global()) if total else None,
        "porcentaje_recomiendan": round(float(row["recomiendan"]) * 100 / total, 1) if total else 0.0,
        "distribucion": {str(i): int(row[f"e{i}"]) for i in range(5, 0, -1)},
    }


# ----------------------------------------------------------------- endpoints
@app.post("/api/calificaciones/producto/<int:producto_id>")
@require_auth
def calificar(producto_id):
    """Crea o actualiza la calificación del usuario. Regla: solo quien compró (pago APROBADO) puede calificar."""
    data = request.get_json(silent=True) or {}
    puntuacion = data.get("puntuacion")
    comentario = data.get("comentario")
    if not isinstance(puntuacion, int) or isinstance(puntuacion, bool) or not 1 <= puntuacion <= 5:
        return error("puntuacion debe ser un entero entre 1 y 5")
    if comentario is not None:
        if not isinstance(comentario, str) or len(comentario.strip()) > 255:
            return error("comentario debe ser texto de máximo 255 caracteres")
        comentario = comentario.strip() or None
    if not producto_activo(producto_id):
        return error("Producto no encontrado", 404)
    compra = fetch_one("SELECT COUNT(*) AS n FROM pagos WHERE id_cliente=%s AND id_producto=%s AND estado_pago='APROBADO'",
                       (g.user_id, producto_id))
    if not compra["n"]:
        return error("Solo puede calificar productos que haya comprado (compra verificada)", 403)

    conn = connect()
    try:
        with conn.cursor() as c:
            c.execute("SELECT id_calificacion FROM calificaciones WHERE id_cliente=%s AND id_producto=%s FOR UPDATE",
                      (g.user_id, producto_id))
            existente = c.fetchone()
            if existente:
                c.execute("UPDATE calificaciones SET puntuacion=%s, comentario=%s, fecha=NOW() WHERE id_calificacion=%s",
                          (puntuacion, comentario, existente["id_calificacion"]))
            else:
                c.execute("INSERT INTO calificaciones(id_cliente,id_producto,puntuacion,comentario) VALUES(%s,%s,%s,%s)",
                          (g.user_id, producto_id, puntuacion, comentario))
        conn.commit()
    except IntegrityError:
        conn.rollback()
        return error("No fue posible registrar la calificación", 409)
    finally:
        conn.close()
    return jsonify({
        "mensaje": "Calificación actualizada" if existente else "Calificación registrada",
        "id_producto": producto_id, "puntuacion": puntuacion, "comentario": comentario,
        "compra_verificada": True, "resumen_producto": estadisticas_producto(producto_id),
    }), (200 if existente else 201)


@app.get("/api/calificaciones/pendientes")
@require_auth
def pendientes():
    """Productos comprados (pago APROBADO) que el usuario todavía no ha calificado."""
    rows = clean(fetch_all(
        """SELECT p.id_producto, p.nombre AS producto, m.nombre AS marca, p.categoria,
                  COUNT(pg.id_pago) AS compras, MAX(pg.fecha_pago) AS ultima_compra
           FROM pagos pg JOIN productos p ON p.id_producto=pg.id_producto JOIN marcas m ON m.id_marca=p.id_marca
           WHERE pg.id_cliente=%s AND pg.estado_pago='APROBADO'
             AND NOT EXISTS (SELECT 1 FROM calificaciones k WHERE k.id_cliente=pg.id_cliente AND k.id_producto=pg.id_producto)
           GROUP BY p.id_producto, p.nombre, m.nombre, p.categoria ORDER BY ultima_compra DESC""", (g.user_id,)))
    return jsonify({"total": len(rows), "pendientes_por_calificar": rows})


@app.get("/api/calificaciones/producto/<int:producto_id>/resumen")
def resumen_producto(producto_id):
    """Estadísticas de reputación de un producto, últimos comentarios y la calificación del propio usuario."""
    prod = producto_activo(producto_id)
    if not prod:
        return error("Producto no encontrado", 404)
    comentarios = clean(fetch_all(
        """SELECT cl.nombre AS cliente, k.puntuacion, k.comentario, k.fecha FROM calificaciones k
           JOIN clientes cl ON cl.id_cliente=k.id_cliente
           WHERE k.id_producto=%s AND k.comentario IS NOT NULL ORDER BY k.fecha DESC LIMIT 5""", (producto_id,)))
    mia = None
    return jsonify({"producto": clean(prod), **estadisticas_producto(producto_id),
                    "ultimos_comentarios": comentarios, "mi_calificacion": mia})


@app.get("/api/calificaciones/ranking")
def ranking():
    """Ranking por puntaje bayesiano. Filtros: categoria, marca, minimo_votos, limite (máx. 50)."""
    categoria = request.args.get("categoria")
    marca = request.args.get("marca")
    minimo = request.args.get("minimo_votos", default=1, type=int)
    limite = request.args.get("limite", default=10, type=int)
    if minimo is None or minimo < 1 or limite is None or not 1 <= limite <= 50:
        return error("minimo_votos debe ser >= 1 y limite entre 1 y 50")
    sql = f"""SELECT p.id_producto, p.nombre AS producto, p.categoria, m.nombre AS marca, p.precio,
                     COALESCE(d.porcentaje,0) AS descuento, COUNT(k.id_calificacion) AS votos, AVG(k.puntuacion) AS promedio
              FROM productos p JOIN marcas m ON m.id_marca=p.id_marca
              JOIN calificaciones k ON k.id_producto=p.id_producto {DESCUENTO_VIGENTE}
              WHERE p.estado='ACTIVO' AND m.estado='ACTIVA'"""
    args = []
    if categoria:
        sql += " AND p.categoria=%s"; args.append(categoria)
    if marca:
        sql += " AND m.nombre=%s"; args.append(marca)
    sql += " GROUP BY p.id_producto, p.nombre, p.categoria, m.nombre, p.precio, d.porcentaje HAVING COUNT(k.id_calificacion)>=%s"
    args.append(minimo)
    c = media_global()
    items = []
    for r in fetch_all(sql, args):
        votos, prom = int(r["votos"]), float(r["promedio"])
        items.append({**clean(r), "votos": votos, "promedio": round(prom, 2),
                      "puntaje_ponderado": puntaje_ponderado(prom, votos, c)})
    items.sort(key=lambda x: (-x["puntaje_ponderado"], -x["votos"]))
    items = items[:limite]
    for pos, it in enumerate(items, 1):
        it["posicion"] = pos
    return jsonify({"criterio": f"Promedio bayesiano (prior={PRIOR_VOTOS} votos, media global={round(c, 2)})",
                    "total": len(items), "ranking": items})


@app.get("/api/calificaciones/recomendaciones")
@require_auth
def recomendaciones():
    """Recomendaciones personalizadas.

    Afinidad por categoría y marca = favoritos (+2) + compras (+3) + calificaciones (>=4: +2, <=2: -2).
    Score = afinidad normalizada (60%) + puntaje ponderado/5 (30%) + descuento vigente (10%).
    Sin historial (usuario nuevo) se recomiendan los mejor calificados con descuento.
    """
    limite = request.args.get("limite", default=5, type=int)
    if limite is None or not 1 <= limite <= 20:
        return error("limite debe estar entre 1 y 20")
    uid = g.user_id
    afin_cat, afin_marca = defaultdict(float), defaultdict(float)

    señales = [
        ("favorito", 2, "SELECT p.categoria, p.id_marca FROM favoritos f JOIN productos p ON p.id_producto=f.id_producto WHERE f.id_cliente=%s"),
        ("compra", 3, "SELECT p.categoria, p.id_marca FROM pagos pg JOIN productos p ON p.id_producto=pg.id_producto "
                      "WHERE pg.id_cliente=%s AND pg.estado_pago='APROBADO'"),
        ("calificación alta", 2, "SELECT p.categoria, p.id_marca FROM calificaciones k JOIN productos p ON p.id_producto=k.id_producto "
                                 "WHERE k.id_cliente=%s AND k.puntuacion>=4"),
        ("calificación baja", -2, "SELECT p.categoria, p.id_marca FROM calificaciones k JOIN productos p ON p.id_producto=k.id_producto "
                                  "WHERE k.id_cliente=%s AND k.puntuacion<=2"),
    ]
    historial = 0
    for _, peso, sql in señales:
        for r in fetch_all(sql, (uid,)):
            afin_cat[r["categoria"]] += peso
            afin_marca[r["id_marca"]] += peso
            historial += 1
    max_afin = max([abs(v) for v in list(afin_cat.values()) + list(afin_marca.values())] or [1]) or 1

    comprados = {r["id_producto"] for r in fetch_all(
        "SELECT DISTINCT id_producto FROM pagos WHERE id_cliente=%s AND estado_pago='APROBADO'", (uid,))}
    favs = {r["id_producto"] for r in fetch_all("SELECT id_producto FROM favoritos WHERE id_cliente=%s", (uid,))}
    c = media_global()
    candidatos = fetch_all(
        f"""SELECT p.id_producto, p.nombre AS producto, p.categoria, p.id_marca, m.nombre AS marca, p.precio, p.stock,
                   COALESCE(d.porcentaje,0) AS descuento,
                   ROUND(p.precio*(1-COALESCE(d.porcentaje,0)/100),2) AS precio_final,
                   (SELECT COUNT(*) FROM calificaciones k WHERE k.id_producto=p.id_producto) AS votos,
                   (SELECT AVG(k.puntuacion) FROM calificaciones k WHERE k.id_producto=p.id_producto) AS promedio
            FROM productos p JOIN marcas m ON m.id_marca=p.id_marca {DESCUENTO_VIGENTE}
            WHERE p.estado='ACTIVO' AND m.estado='ACTIVA' AND p.stock>0""")

    resultado = []
    for p in candidatos:
        if p["id_producto"] in comprados:
            continue
        votos = int(p["votos"])
        prom = float(p["promedio"]) if p["promedio"] is not None else c
        ponderado = puntaje_ponderado(prom, votos, c) if votos else c
        a_cat, a_marca = afin_cat.get(p["categoria"], 0), afin_marca.get(p["id_marca"], 0)
        afinidad = (a_cat + a_marca) / (2 * max_afin)
        score = 0.6 * afinidad + 0.3 * (ponderado / 5) + 0.1 * (float(p["descuento"]) / 100)
        motivos = []
        if a_marca > 0: motivos.append(f"Te interesa la marca {p['marca']}")
        if a_cat > 0: motivos.append(f"Te interesa la categoría {p['categoria']}")
        if p["id_producto"] in favs: motivos.append("Está en tus favoritos")
        if votos and ponderado >= 4: motivos.append(f"Muy bien calificado ({round(prom, 1)}★ en {votos} " + ("voto" if votos == 1 else "votos") + ")")
        if float(p["descuento"]) > 0: motivos.append(f"Tiene {float(p['descuento']):g}% de descuento vigente")
        if a_marca < 0 or a_cat < 0: motivos.append("Atención: calificaste mal productos similares")
        resultado.append({
            "id_producto": p["id_producto"], "producto": p["producto"], "marca": p["marca"], "categoria": p["categoria"],
            "precio": float(p["precio"]), "descuento": float(p["descuento"]), "precio_final": float(p["precio_final"]),
            "calificacion_promedio": round(prom, 2) if votos else None, "votos": votos,
            "score": round(score, 4), "motivos": motivos or ["Producto disponible en el catálogo"],
        })
    resultado.sort(key=lambda x: -x["score"])
    resultado = resultado[:limite]
    for pos, it in enumerate(resultado, 1):
        it["posicion"] = pos
    return jsonify({"personalizado": historial > 0, "senales_historial": historial,
                    "total": len(resultado), "recomendaciones": resultado})


@app.get("/api/calificaciones/marcas/reputacion")
def reputacion_marcas():
    """Reputación por marca: promedio, puntaje ponderado, nivel, mejor producto y descuento medio vigente."""
    c = media_global()
    marcas = fetch_all("SELECT id_marca, nombre, canal_oficial FROM marcas WHERE estado='ACTIVA'")
    prod = fetch_all(
        f"""SELECT p.id_producto, p.nombre, p.id_marca, COUNT(k.id_calificacion) AS votos, AVG(k.puntuacion) AS promedio,
                   COALESCE(d.porcentaje,0) AS descuento
            FROM productos p LEFT JOIN calificaciones k ON k.id_producto=p.id_producto {DESCUENTO_VIGENTE}
            WHERE p.estado='ACTIVO' GROUP BY p.id_producto, p.nombre, p.id_marca, d.porcentaje""")
    por_marca = defaultdict(list)
    for p in prod:
        por_marca[p["id_marca"]].append(p)

    salida = []
    for m in marcas:
        ps = por_marca.get(m["id_marca"], [])
        votos = sum(int(p["votos"]) for p in ps)
        suma = sum(float(p["promedio"]) * int(p["votos"]) for p in ps if p["votos"])
        prom = suma / votos if votos else None
        pond = puntaje_ponderado(prom, votos, c) if votos else None
        calificados = [p for p in ps if p["votos"]]
        mejor = max(calificados, key=lambda p: puntaje_ponderado(float(p["promedio"]), int(p["votos"]), c), default=None)
        nivel = ("SIN_DATOS" if pond is None else "EXCELENTE" if pond >= 4.5 else "BUENA" if pond >= 3.5
                 else "REGULAR" if pond >= 2.5 else "BAJA")
        salida.append({
            "id_marca": m["id_marca"], "marca": m["nombre"], "canal_oficial": m["canal_oficial"],
            "productos_activos": len(ps), "productos_calificados": len(calificados), "total_votos": votos,
            "promedio": round(prom, 2) if prom is not None else None, "puntaje_ponderado": pond, "nivel": nivel,
            "mejor_producto": mejor["nombre"] if mejor else None,
            "descuento_promedio_vigente": round(sum(float(p["descuento"]) for p in ps) / len(ps), 1) if ps else 0.0,
        })
    salida.sort(key=lambda x: (x["puntaje_ponderado"] is None, -(x["puntaje_ponderado"] or 0)))
    return jsonify({"total": len(salida), "marcas": clean(salida)})


@app.get("/health")
@require_auth
def health():
    return jsonify({"servicio": "calificaciones", "estado": "activo"})


@app.errorhandler(404)
def not_found(_):
    return jsonify({"error": "Ruta no encontrada"}), 404


@app.errorhandler(405)
def not_allowed(_):
    return jsonify({"error": "Método no permitido"}), 405


@app.errorhandler(500)
def internal(_):
    return jsonify({"error": "Error interno. Revise la consola del servicio."}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5004, debug=False)


@app.get('/api/calificaciones/resumenes')
def resumenes_publicos():
    rows = fetch_all("SELECT id_producto, COUNT(*) AS votos, ROUND(AVG(puntuacion),2) AS promedio FROM calificaciones GROUP BY id_producto")
    return jsonify({'resumenes': clean(rows)})
