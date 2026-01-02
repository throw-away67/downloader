from typing import Optional, List, Dict
from ..db import execute_query

class OrderRepository:
    def __init__(self, conn):
        self.conn = conn

    def list_all(self) -> List[Dict]:
        cur = execute_query(self.conn,
            """
            SELECT o.*, c.name AS customer_name
            FROM orders o
            JOIN customers c ON c.id = o.customer_id
            ORDER BY o.created_at DESC
            """)
        return cur.fetchall()

    def get_by_id(self, order_id: int) -> Optional[Dict]:
        cur = execute_query(self.conn, "SELECT * FROM orders WHERE id=%s", (order_id,))
        return cur.fetchone()

    def list_items(self, order_id: int) -> List[Dict]:
        cur = execute_query(self.conn,
            """
            SELECT oi.*, p.name AS product_name
            FROM order_items oi
            JOIN products p ON p.id = oi.product_id
            WHERE oi.order_id = %s
            """,
            (order_id,))
        return cur.fetchall()

    def create_order(self, customer_id: int, status: str, order_date: str, delivery_time: Optional[str], total_amount: float, is_paid: bool) -> int:
        execute_query(self.conn,
            """
            INSERT INTO orders (customer_id, status, order_date, delivery_time, total_amount, is_paid)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (customer_id, status, order_date, delivery_time, total_amount, is_paid))
        cur = execute_query(self.conn, "SELECT LAST_INSERT_ID() AS id")
        return cur.fetchone()["id"]

    def add_item(self, order_id: int, product_id: int, quantity: int, unit_price: float, line_total: float) -> int:
        execute_query(self.conn,
            """
            INSERT INTO order_items (order_id, product_id, quantity, unit_price, line_total)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (order_id, product_id, quantity, unit_price, line_total))
        cur = execute_query(self.conn, "SELECT LAST_INSERT_ID() AS id")
        return cur.fetchone()["id"]