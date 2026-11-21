
from comun.db import connect

try:
    print("Conectando con Supabase...")

    conn = connect()

    with conn.cursor() as cur:
        cur.execute("SELECT current_database()")
        resultado = cur.fetchone()

        print("Base de datos:", resultado)

        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)

        tablas = cur.fetchall()

        print("\nTablas encontradas:")

        for tabla in tablas:
            print("-", tabla["table_name"])

    conn.close()

    print("\nCONEXIÓN EXITOSA CON SUPABASE")

except Exception as error:
    print("\nERROR DE CONEXIÓN:")
    print(type(error).__name__)
    print(str(error))
