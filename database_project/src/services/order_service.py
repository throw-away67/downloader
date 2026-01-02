from typing import List, Dict
from datetime import date
from ..db import DBError, execute_query
from ..repositories.order import OrderRepository
from ..repositories.product import ProductRepository

class OrderServiceError(Exception):
    pass

class OrderService:
    def __init__(self, conn):
        self.conn = conn
        self.order_repo = OrderRepository(conn)
        self.product_repo = ProductRepository(conn)

    def create_order_transaction(self, customer_id: int, items: List[Dict], order_date: date, delivery_time: str | None) -> int:
        """
        items: list of dicts {product_id: int, quantity: int}
        Transaction across orders, order_items, products (stock).
        """
        try:
            total_amount = 0.0
            prepared = []
            for it in items:
                product = self.product_repo.get_by_id(it["product_id"])
                if not product or not product["is_active"]:
                    raise OrderServiceError(f"Product {it['product_id']} not found or inactive.")
                qty = int(it["quantity"])
                if qty <= 0:
                    raise OrderServiceError("Quantity must be > 0.")
                if product["stock"] < qty:
                    raise OrderServiceError(f"Not enough stock for product {product['name']}.")
                unit_price = float(product["price"])
                line_total = unit_price * qty
                total_amount += line_total
                prepared.append({
                    "product_id": it["product_id"],
                    "quantity": qty,
                    "unit_price": unit_price,
                    "line_total": line_total
                })

            # Start transaction
            order_id = self.order_repo.create_order(
                customer_id=customer_id,
                status="new",
                order_date=str(order_date),
                delivery_time=delivery_time,
                total_amount=total_amount,
                is_paid=False
            )

            # Insert items and update stock
            for pi in prepared:
                self.order_repo.add_item(order_id, pi["product_id"], pi["quantity"], pi["unit_price"], pi["line_total"])
                # update product stock
                execute_query(self.conn,
                    "UPDATE products SET stock = stock - %s WHERE id=%s",
                    (pi["quantity"], pi["product_id"]))

            # Commit
            self.conn.commit()
            return order_id

        except (DBError, OrderServiceError) as e:
            self.conn.rollback()
            raise OrderServiceError(f"Order transaction failed: {str(e)}")
        except Exception as e:
            self.conn.rollback()
            raise