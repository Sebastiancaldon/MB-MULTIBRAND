
import os
from urllib.parse import unquote

from werkzeug.wrappers import Request

service = os.environ.get("MB_SERVICE", "catalogo")

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

flask_app = app


def app(environ, start_response):
    request = Request(environ)

    original_path = request.args.get("original_path")

    if original_path is not None:
        environ["PATH_INFO"] = "/" + unquote(
            original_path.lstrip("/")
        )

    return flask_app(environ, start_response)
