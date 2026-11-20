
import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()

def connect():
    database_url = os.environ["DATABASE_URL"]

    return psycopg.connect(
        database_url,
        row_factory=dict_row,
        connect_timeout=10
    )

def fetch_all(sql, params=()):
    conn = connect()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()
    finally:
        conn.close()

def fetch_one(sql, params=()):
    conn = connect()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchone()
    finally:
        conn.close()
