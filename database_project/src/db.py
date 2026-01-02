import pymysql
from .config import load_config

_cfg = load_config()
_db = _cfg["database"]

def get_connection():
    return pymysql.connect(
        host=_db["host"],
        user=_db["user"],
        password=_db["password"],
        database=_db["name"],
        port=int(_db["port"]),
        charset="utf8mb4",
        autocommit=False,  # we control transactions manually
        cursorclass=pymysql.cursors.DictCursor,
    )

class DBError(Exception):
    pass

def execute_query(conn, sql, params=None):
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur
    except Exception as e:
        raise DBError(str(e))