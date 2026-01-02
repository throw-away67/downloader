from typing import List, Dict
from ..db import execute_query

class CategoryRepository:
    def __init__(self, conn):
        self.conn = conn

    def list_all(self) -> List[Dict]:
        cur = execute_query(self.conn, "SELECT * FROM categories ORDER BY created_at DESC")
        return cur.fetchall()

    def assign_to_product(self, product_id: int, category_id: int) -> None:
        execute_query(self.conn,
            "INSERT IGNORE INTO product_categories (product_id, category_id) VALUES (%s, %s)",
            (product_id, category_id))
        self.conn.commit()

    def remove_from_product(self, product_id: int, category_id: int) -> None:
        execute_query(self.conn,
            "DELETE FROM product_categories WHERE product_id=%s AND category_id=%s",
            (product_id, category_id))
        self.conn.commit()

    def categories_for_product(self, product_id: int) -> List[Dict]:
        cur = execute_query(self.conn,
            """
            SELECT c.* FROM categories c
            JOIN product_categories pc ON pc.category_id = c.id
            WHERE pc.product_id = %s
            """,
            (product_id,))
        return cur.fetchall()