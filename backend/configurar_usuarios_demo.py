"""Asigna las contraseñas de demostración a las cuentas creadas por bd.sql."""
from werkzeug.security import generate_password_hash
from comun.db import connect

DEMO_USERS=[('sebastian','SebasDemo2026!'),('demo','DemoMultibrand2026!')]
conn=connect()
try:
    with conn.cursor() as c:
        for username,password in DEMO_USERS:
            c.execute('UPDATE cuentas SET password_hash=%s WHERE usuario=%s',(generate_password_hash(password),username))
            if c.rowcount != 1:
                raise RuntimeError(f'No se encontró la cuenta {username}. Importe bd.sql primero.')
    conn.commit()
    print('Contraseñas demo configuradas.')
finally:conn.close()
