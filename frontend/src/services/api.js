import axios from 'axios'
const base = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5001'
const purchases = import.meta.env.VITE_COMPRAS_URL || 'http://127.0.0.1:5002'
const ratings = import.meta.env.VITE_CALIFICACIONES_URL || 'http://127.0.0.1:5004'
function client(baseURL) {
  const instance = axios.create({ baseURL, timeout: 12000 })
  instance.interceptors.request.use(config => {
    const token = localStorage.getItem('token')
    if (token) config.headers.Authorization = `Bearer ${token}`
    if (config.url === '/register' && import.meta.env.VITE_API_KEY) config.headers['X-API-KEY'] = import.meta.env.VITE_API_KEY
    return config
  })
  instance.interceptors.response.use(r => r, error => {
    if (error.response?.status === 401 && localStorage.getItem('token') && !['/login','/register'].includes(error.config?.url)) {
      localStorage.removeItem('token'); localStorage.removeItem('username')
      window.dispatchEvent(new Event('mb-session-expired'))
    }
    return Promise.reject(error)
  })
  return instance
}
export const catalogoApi = client(base)
export const comprasApi = client(purchases)
export const calificacionesApi = client(ratings)
export default catalogoApi
