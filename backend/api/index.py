
import os

service = os.environ.get(
    "MB_SERVICE", "catalogo"
)

if service == "catalogo":
    from microservicio_catalogo.app import app
elif service == "compras":
    from microservicio_cliente_compras.app import app
elif service == "calificaciones":
    from microservicio_calificaciones.app import app
else:
    raise RuntimeError(
        f"Microservicio desconocido: {service}"
    )
