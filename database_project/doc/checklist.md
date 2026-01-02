# Příloha 1 – Checklist (CZ/EN)

Tento dokument sumarizuje splnění požadavků zadání a obsahuje odkazy/sekce pro kontrolu:

## Hlavní úkol D1/D2/D3
- [x] D1 – Repository pattern (vlastní DAO/TableGateway + Repository)
- [ ] D2 – Row Gateway / Active Record (neimplementováno)
- [ ] D3 – Object-Relation Mapping (Mapper pattern) (neimplementováno)

## Databáze a datové typy
- [x] RDBMS: MySQL
- [x] Min. 5 tabulek včetně vazebních (M:N):
  - customers, products, categories, product_categories (M:N), orders, order_items
- [x] 2x pohled (view):
  - view_customer_order_totals, view_product_sales
- [x] 1x vazba M:N:
  - products ↔ categories (product_categories)
- [x] Datové typy:
  - float: price, total_amount, unit_price, line_total
  - bool: is_active, is_paid
  - enum: orders.status
  - string/varchar: name, email
  - date/time: orders.order_date (DATE), orders.delivery_time (TIME), created_at (DATETIME)

## Funkcionality
- [x] Vložení/smazání/zobrazení/úprava informací do více tabulek:
  - Vytvoření objednávky (orders + order_items + vazba na customers), upravy v repozitářích
- [x] Transakce nad více tabulkami:
  - create_order_transaction (orders, order_items, products.stock)
- [x] Souhrnný report:
  - Report stránka /report využívá view + agregace (COUNT, SUM, MIN, MAX)
- [x] Import dat (CSV/JSON):
  - Import zákazníků (CSV)
  - Import produktů (JSON)
- [x] Konfigurační soubor:
  - config/config.yaml
- [x] Ošetření vstupů a chyb:
  - Validace formulářů (základní), chyby konfigurace, chyby DB, limit velikosti souboru, flash hlášky

## Dokumentace a testy
- [x] README (instalace, konfigurace, spuštění)
- [x] Min. 3 testovací scénáře (vyexportovat do PDF):
  - 1_install_and_setup.md
  - 2_functional_tests.md
  - 3_error_and_config_tests.md

## Poznámky
- Aplikace je spustitelná bez IDE dle README.
- Prezentace a testování proběhne na školním PC.
- Nepoužití hotového ORM – splněno.
- V případě využití cizího kódu – uvést zdroj (není zde použito).