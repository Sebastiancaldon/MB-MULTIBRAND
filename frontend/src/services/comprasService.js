import { comprasApi } from './api'
export default {
 procesar: (id_producto,cantidad) => comprasApi.post('/api/compras/procesar',{id_producto,cantidad}),
 estado: id => comprasApi.get(`/api/compras/${id}/estado`),
 favoritos: () => comprasApi.get('/api/compras/favoritos'),
 agregarFavorito: id_producto => comprasApi.post('/api/compras/favoritos',{id_producto}),
 quitarFavorito: id => comprasApi.delete(`/api/compras/favoritos/${id}`)
}
