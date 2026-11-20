import { catalogoApi } from './api'
export default {
 obtenerOfertas: filtros => catalogoApi.get('/api/catalogo/ofertas', {params:filtros}),
 obtenerMejores: () => catalogoApi.get('/api/catalogo/ofertas/mejores'),
 obtenerProducto: id => catalogoApi.get(`/api/catalogo/productos/${id}`),
 obtenerMarcas: () => catalogoApi.get('/api/catalogo/marcas'),
 obtenerCategorias: () => catalogoApi.get('/api/catalogo/categorias')
}
