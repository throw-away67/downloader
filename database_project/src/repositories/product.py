from typing import Optional, List, Dict
from ..db import execute_query

class ProductRepository:
    def __init__(self, conn):
        self.conn = conn

    def list_all(self) -> List[Dict]:
        cur = execute_query(self.conn, "SELECT * FROM products ORDER BY created_at DESC")
        return cur.fetchall()

    def get_by_id(self, product_id: int) -> Optional[Dict]:
        cur = execute_query(self.conn, "SELECT * FROM products WHERE id=%s", (product_id,))
        return cur.fetchone()

    def create(self, name: str, price: float, stock: int, is_active: bool = True) -> int:
        execute_query(self.conn,
            "INSERT INTO products (name, price, stock, is_active) VALUES (%s, %s, %s, %s)",
            (name, price, stock, is_active))
        self.conn.commit()
        cur = execute_query(self.conn, "SELECT LAST_INSERT_ID() AS id")
        return cur.fetchone()["id"]

    def update(self, product_id: int, name: str, price: float, stock: int, is_active: bool) -> None:
        execute_query(self.conn,
            "UPDATE products SET name=%s, price=%s, stock=%s, is_active=%s WHERE id=%s",
            (name, price, stock, is_active, product_id))
        self.conn.commit()

    def delete(self, product_id: int) -> None:
        execute_query(self.conn, "DELETE FROM products WHERE id=%s", (product_id,))
        self.conn.commit()