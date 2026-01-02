import csv
from typing import IO
from ..db import execute_query

class CSVImporterError(Exception):
    pass

def import_customers_csv(conn, file_obj: IO[str]) -> int:
    """
    Expected CSV header: name,email,credit,is_active
    Returns number of imported rows.
    """
    reader = csv.DictReader(file_obj)
    count = 0
    for row in reader:
        name = row.get("name", "").strip()
        email = row.get("email", "").strip()
        credit = float(row.get("credit", "0") or 0)
        is_active = row.get("is_active", "true").lower() in ("true", "1", "yes")
        if not name or not email:
            raise CSVImporterError("Missing name or email in CSV row.")
        execute_query(conn,
            "INSERT INTO customers (name, email, credit, is_active) VALUES (%s, %s, %s, %s)",
            (name, email, credit, is_active))
        count += 1
    conn.commit()
    return count