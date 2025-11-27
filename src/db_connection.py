import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
from mysql.connector import pooling

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "database": os.getenv("DB_NAME","cursos_online"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "Chetos5566"),
    "autocommit": False,
    "charset": "utf8mb4",
}

POOL_NAME = os.getenv("POOL_NAME", "bib_pool")
POOL_SIZE = int(os.getenv("POOL_SIZE", 5))

# Pool de conexiones 
pool = pooling.MySQLConnectionPool(
    pool_name=POOL_NAME,
    pool_size=POOL_SIZE,
    **DB_CONFIG
)

def get_conn():
    return pool.get_connection()

def create_connection():
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            database=DB_CONFIG["database"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            charset=DB_CONFIG["charset"]
        )
        return conn
    except Error as e:
        print(f"Error al conectar: {e}")
        return None


def close_connection(conn):
    if conn and conn.is_connected():
        conn.close()