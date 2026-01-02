import json
from typing import IO
from ..db import execute_query

class JSONImporterError(Exception):
    pass

def import_products_json(conn, file_obj: IO[str]) -> int:
    """
    Expected JSON: [{ "name": "...", "price": 12.3, "stock": 10, "is_active": true }, ...]
    Returns number of imported products.
    """
    try:
        data = json.load(file_obj)
        if not isinstance(data, list):
            raise JSONImporterError("JSON must be an array of products.")
        count = 0
        for item in data:
            name = str(item.get("name", "")).strip()
            price = float(item.get("price", 0))
            stock = int(item.get("stock", 0))
            is_active = bool(item.get("is_active", True))
            if not name or price <= 0 or stock < 0:
                raise JSONImporterError("Invalid product entry.")
            execute_query(conn,
                "INSERT INTO products (name, price, stock, is_active) VALUES (%s, %s, %s, %s)",
                (name, price, stock, is_active))
            count += 1
        conn.commit()
        return count
    except json.JSONDecodeError as e:
        raise JSONImporterError(f"Invalid JSON: {str(e)}")