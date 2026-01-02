from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import date
import os
import io

# --- import bootstrap (supports both `python -m src.app` and `python src/app.py`) ---
try:
    # running as a module: python -m src.app
    from .config import load_config, ConfigError
    from .db import get_connection, DBError
    from .repositories.customer import CustomerRepository
    from .repositories.product import ProductRepository
    from .repositories.category import CategoryRepository
    from .repositories.order import OrderRepository
    from .services.order_service import OrderService, OrderServiceError
    from .importers.csv_importer import import_customers_csv, CSVImporterError
    from .importers.json_importer import import_products_json, JSONImporterError
except ImportError:
    # running as a script: python src/app.py (not recommended)
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # add project root to sys.path
    from .config import load_config, ConfigError
    from .db import get_connection, DBError
    from .repositories.customer import CustomerRepository
    from .repositories.product import ProductRepository
    from .repositories.category import CategoryRepository
    from .repositories.order import OrderRepository
    from .services.order_service import OrderService, OrderServiceError
    from .importers.csv_importer import import_customers_csv, CSVImporterError
    from .importers.json_importer import import_products_json, JSONImporterError
# --- end import bootstrap ---

cfg = None
try:
    cfg = load_config()
except ConfigError as e:
    # Minimal fallback app to show config error
    app = Flask(__name__)
    @app.route("/")
    def config_error():
        return render_template("error.html", message=f"Config error: {str(e)}")
    if __name__ == "__main__":
        app.run(debug=True)
    raise SystemExit(0)

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = cfg["app"]["secret_key"]
app.config["MAX_CONTENT_LENGTH"] = cfg["app"]["max_upload_size_mb"] * 1024 * 1024

def with_conn(fn):
    def wrapper(*args, **kwargs):
        conn = get_connection()
        try:
            result = fn(conn, *args, **kwargs)
            return result
        except DBError as e:
            conn.rollback()
            return render_template("error.html", message=f"Database error: {str(e)}")
        finally:
            conn.close()
    wrapper.__name__ = fn.__name__
    return wrapper

@app.route("/")
@with_conn
def index(conn):
    cust_repo = CustomerRepository(conn)
    prod_repo = ProductRepository(conn)
    order_repo = OrderRepository(conn)
    customers = cust_repo.list_all()
    products = prod_repo.list_all()
    orders = order_repo.list_all()
    return render_template("index.html", customers=customers, products=products, orders=orders)

@app.route("/customers")
@with_conn
def customers(conn):
    cust_repo = CustomerRepository(conn)
    return render_template("customers.html", customers=cust_repo.list_all())

@app.route("/products")
@with_conn
def products(conn):
    prod_repo = ProductRepository(conn)
    cat_repo = CategoryRepository(conn)
    products = prod_repo.list_all()
    categories = cat_repo.list_all()
    return render_template("products.html", products=products, categories=categories)

@app.route("/orders")
@with_conn
def orders(conn):
    order_repo = OrderRepository(conn)
    orders = order_repo.list_all()
    return render_template("orders.html", orders=orders)

@app.route("/orders/<int:order_id>")
@with_conn
def order_detail(conn, order_id: int):
    order_repo = OrderRepository(conn)
    cust_repo = CustomerRepository(conn)
    order = order_repo.get_by_id(order_id)
    if not order:
        flash(f"Objednávka #{order_id} nebyla nalezena.", "error")
        return redirect(url_for("orders"))
    customer = cust_repo.get_by_id(order["customer_id"])
    items = order_repo.list_items(order_id)
    return render_template("order_detail.html", order=order, customer=customer, items=items)

@app.route("/orders/new", methods=["GET", "POST"])
@with_conn
def order_new(conn):
    cust_repo = CustomerRepository(conn)
    prod_repo = ProductRepository(conn)
    service = OrderService(conn)
    customers = cust_repo.list_all()
    products = prod_repo.list_all()
    if request.method == "POST":
        customer_id = int(request.form.get("customer_id", "0"))
        delivery_time = request.form.get("delivery_time") or None
        # Collect items from form
        items = []
        product_ids = request.form.getlist("product_id")
        quantities = request.form.getlist("quantity")
        for pid, q in zip(product_ids, quantities):
            if pid and q:
                items.append({"product_id": int(pid), "quantity": int(q)})

        try:
            if customer_id <= 0 or not items:
                flash("Please select a customer and at least one product with quantity.", "error")
                return redirect(url_for("order_new"))

            order_id = service.create_order_transaction(customer_id, items, date.today(), delivery_time)
            flash(f"Order {order_id} created successfully.", "success")
            return redirect(url_for("orders"))
        except OrderServiceError as e:
            flash(str(e), "error")
        except Exception as e:
            flash(f"Unexpected error: {str(e)}", "error")

    return render_template("order_create.html", customers=customers, products=products)

@app.route("/report")
@with_conn
def report(conn):
    # Aggregated report using views and joins across multiple tables
    cur1 = conn.cursor()
    cur1.execute("SELECT * FROM view_customer_order_totals ORDER BY total_spent DESC")
    customer_totals = cur1.fetchall()

    cur2 = conn.cursor()
    cur2.execute("SELECT * FROM view_product_sales ORDER BY total_revenue DESC")
    product_sales = cur2.fetchall()

    # Additional cross-table aggregates: min/max/avg
    cur3 = conn.cursor()
    cur3.execute("""
        SELECT
          COUNT(DISTINCT o.id) AS orders_count,
          COALESCE(SUM(o.total_amount), 0) AS total_revenue,
          COALESCE(MIN(o.total_amount), 0) AS min_order_total,
          COALESCE(MAX(o.total_amount), 0) AS max_order_total
        FROM orders o
    """)
    overall = cur3.fetchone()

    return render_template("report.html",
                           customer_totals=customer_totals,
                           product_sales=product_sales,
                           overall=overall)

@app.route("/import/customers", methods=["POST"])
@with_conn
def import_customers(conn):
    fmt = "csv"
    if fmt not in cfg["app"]["allowed_import_formats"]:
        return render_template("error.html", message="CSV import not allowed by config.")
    file = request.files.get("customers_csv")
    if not file:
        flash("Please upload a CSV file.", "error")
        return redirect(url_for("customers"))
    try:
        # Proper text stream for csv.DictReader
        text_stream = io.TextIOWrapper(file.stream, encoding="utf-8")
        count = import_customers_csv(conn, text_stream)
        flash(f"Imported {count} customers.", "success")
    except CSVImporterError as e:
        flash(str(e), "error")
    return redirect(url_for("customers"))

@app.route("/import/products", methods=["POST"])
@with_conn
def import_products(conn):
    fmt = "json"
    if fmt not in cfg["app"]["allowed_import_formats"]:
        return render_template("error.html", message="JSON import not allowed by config.")
    file = request.files.get("products_json")
    if not file:
        flash("Please upload a JSON file.", "error")
        return redirect(url_for("products"))
    try:
        count = import_products_json(conn, file.stream)
        flash(f"Imported {count} products.", "success")
    except JSONImporterError as e:
        flash(str(e), "error")
    return redirect(url_for("products"))

@app.errorhandler(413)
def file_too_large(_):
    return render_template("error.html", message="Uploaded file too large."), 413

if __name__ == "__main__":
    # Run via `python -m src.app` from project root, or `python run.py`
    app.run(debug=cfg["app"]["debug"])