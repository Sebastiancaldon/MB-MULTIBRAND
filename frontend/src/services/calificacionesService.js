import { calificacionesApi } from './api'
export default {
 resumenes: () => calificacionesApi.get('/api/calificaciones/resumenes'),
 resumen: id => calificacionesApi.get(`/api/calificaciones/producto/${id}/resumen`),
 calificar: (id,puntuacion,comentario) => calificacionesApi.post(`/api/calificaciones/producto/${id}`,{puntuacion,comentario}),
 pendientes: () => calificacionesApi.get('/api/calificaciones/pendientes'),
 ranking: params => calificacionesApi.get('/api/calificaciones/ranking',{params}),
 recomendaciones: () => calificacionesApi.get('/api/calificaciones/recomendaciones'),
 reputacionMarcas: () => calificacionesApi.get('/api/calificaciones/marcas/reputacion')
}
