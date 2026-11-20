from flask import Flask,request,jsonify
from comun.db import fetch_all,fetch_one
from flask_cors import CORS
from comun.config import CORS_ORIGINS
from comun.auth_routes import login_bp
from comun.security import require_auth,error
from comun.serializers import clean
app=Flask(__name__)
CORS(app, origins=CORS_ORIGINS)  # permite que el frontend Vue (otro puerto) consuma esta API
app.register_blueprint(login_bp)  # login y rutas de autenticación en este servicio

@app.get('/api/catalogo/ofertas')
def ofertas():
    categoria=request.args.get('categoria'); marca=request.args.get('marca'); max_precio=request.args.get('max_precio',type=float)
    sql="""SELECT p.id_producto,p.nombre AS producto,p.categoria,m.nombre AS marca,p.precio,p.stock,
      COALESCE(d.porcentaje,0) AS descuento, ROUND(p.precio*(1-COALESCE(d.porcentaje,0)/100),2) AS precio_final
      FROM productos p JOIN marcas m ON m.id_marca=p.id_marca
      LEFT JOIN descuentos d ON d.id_producto=p.id_producto AND d.estado='ACTIVO' AND CURDATE() BETWEEN d.fecha_inicio AND d.fecha_fin
      WHERE p.estado='ACTIVO' AND m.estado='ACTIVA'"""
    args=[]
    if categoria: sql+=' AND p.categoria=%s'; args.append(categoria)
    if marca: sql+=' AND m.nombre=%s'; args.append(marca)
    if max_precio is not None: sql+=' AND p.precio*(1-COALESCE(d.porcentaje,0)/100)<=%s'; args.append(max_precio)
    sql+=' ORDER BY precio_final ASC'
    return jsonify({'total':(rows:=clean(fetch_all(sql,args))).__len__(),'ofertas':rows})

@app.get('/api/catalogo/ofertas/mejores')
def mejores():
    rows=clean(fetch_all("""SELECT p.id_producto,p.nombre AS producto,m.nombre AS marca,p.precio,d.porcentaje AS descuento,
      ROUND(p.precio*(1-d.porcentaje/100),2) AS precio_final FROM productos p JOIN marcas m ON m.id_marca=p.id_marca
      JOIN descuentos d ON d.id_producto=p.id_producto WHERE p.estado='ACTIVO' AND d.estado='ACTIVO'
      AND CURDATE() BETWEEN d.fecha_inicio AND d.fecha_fin ORDER BY d.porcentaje DESC LIMIT 5"""))
    return jsonify({'criterio':'Mayor porcentaje de descuento vigente','ofertas':rows})

@app.get('/api/catalogo/productos/<int:producto_id>')
def detalle(producto_id):
    row=fetch_one("""SELECT p.id_producto,p.nombre AS producto,p.categoria,p.descripcion,m.nombre AS marca,p.precio,p.stock,
      COALESCE(d.porcentaje,0) AS descuento,ROUND(p.precio*(1-COALESCE(d.porcentaje,0)/100),2) AS precio_final
      FROM productos p JOIN marcas m ON m.id_marca=p.id_marca LEFT JOIN descuentos d ON d.id_producto=p.id_producto
      AND d.estado='ACTIVO' AND CURDATE() BETWEEN d.fecha_inicio AND d.fecha_fin WHERE p.id_producto=%s AND p.estado='ACTIVO'""",(producto_id,))
    if not row:return error('Producto no encontrado',404)
    return jsonify(clean(row))

@app.get('/api/catalogo/marcas')
def marcas():
    return jsonify({'marcas':clean(fetch_all("SELECT id_marca,nombre,descripcion,canal_oficial FROM marcas WHERE estado='ACTIVA' ORDER BY nombre"))})

@app.get('/api/catalogo/categorias')
def categorias():
    return jsonify({'categorias':clean(fetch_all("SELECT DISTINCT categoria FROM productos WHERE estado='ACTIVO' ORDER BY categoria"))})

@app.get('/health')
def health(): return jsonify({'servicio':'catalogo','estado':'activo'})

@app.errorhandler(404)
def not_found(_): return jsonify({'error':'Ruta no encontrada'}),404
@app.errorhandler(500)
def internal(_): return jsonify({'error':'Error interno. Revise la consola del servicio.'}),500
if __name__=='__main__': app.run(host='127.0.0.1',port=5001,debug=False)
