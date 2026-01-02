from typing import Optional, List, Dict
from ..db import execute_query

class CustomerRepository:
    def __init__(self, conn):
        self.conn = conn

    def list_all(self) -> List[Dict]:
        cur = execute_query(self.conn, "SELECT * FROM customers ORDER BY created_at DESC")
        return cur.fetchall()

    def get_by_id(self, customer_id: int) -> Optional[Dict]:
        cur = execute_query(self.conn, "SELECT * FROM customers WHERE id=%s", (customer_id,))
        return cur.fetchone()

    def create(self, name: str, email: str, credit: float = 0.0, is_active: bool = True) -> int:
        execute_query(self.conn,
            "INSERT INTO customers (name, email, credit, is_active) VALUES (%s, %s, %s, %s)",
            (name, email, credit, is_active))
        self.conn.commit()
        cur = execute_query(self.conn, "SELECT LAST_INSERT_ID() AS id")
        return cur.fetchone()["id"]

    def update(self, customer_id: int, name: str, email: str, credit: float, is_active: bool) -> None:
        execute_query(self.conn,
            "UPDATE customers SET name=%s, email=%s, credit=%s, is_active=%s WHERE id=%s",
            (name, email, credit, is_active, customer_id))
        self.conn.commit()

    def delete(self, customer_id: int) -> None:
        execute_query(self.conn, "DELETE FROM customers WHERE id=%s", (customer_id,))
        self.conn.commit()