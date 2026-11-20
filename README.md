# MB Multibrand – Frontend (Vue) + Backend (Flask REST)

Estructura igual a la del proyecto de la cafetería: dos carpetas independientes que solo se comunican por HTTP.

```
MB_MULTIBRAND_VUE/
├── backend/     Flask + MySQL (microservicios, puertos 5001, 5002 y 5004)
├── frontend/    Vue 3 + Vite + Pinia + Vue Router + Axios (puerto 5173)
└── documentacion/
```

## 1. Base de datos
Importa `backend/bd.sql` en MySQL (crea `mb_multibrand`). 

## 2. Backend
```
cd backend
pip install -r requirements.txt
# revisa backend/.env (usuario y clave de MySQL, API_KEY, JWT_SECRET_KEY)

         # los 3 microservicios
# o solo el catálogo (lo único que usa el frontend):
python -m microservicio_catalogo.server
```

## 3. Frontend
```
cd frontend
npm install
npm run dev                     # http://localhost:5173
```
`frontend/.env`: `VITE_API_URL` (catálogo, 5001) y `VITE_API_KEY` (debe ser igual a `API_KEY` del backend).

## Pantallas y endpoints
| Pantalla | Endpoint | Protección |
|---|---|---|
| /login | POST /login | pública |
| /register | POST /register | X-API-KEY |
| /catalogo | GET /api/catalogo/ofertas, /marcas, /categorias | JWT |

El token JWT dura 10 minutos (`JWT_MINUTES`); al expirar, el frontend vuelve al login.
CORS: el backend acepta `http://localhost:5173` y `http://127.0.0.1:5173` (`CORS_ORIGINS` en `.env`).
