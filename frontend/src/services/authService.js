import api from './api'

export default {
  login(username, password) {
    return api.post('/login', { username, password })
  },
  // El backend exige username, password, nombre y correo
  registrar({ username, password, nombre, correo }) {
    return api.post('/register', { username, password, nombre, correo })
  },
}
