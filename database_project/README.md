# Portfolio App (Python + MySQL)

Jednoduchá webová aplikace ve Flasku s MySQL pro správu zákazníků, produktů a objednávek. Obsahuje formulář pro vytvoření objednávky, základní přehledy a import dat.

## Požadavky
- Python 3.10+
- MySQL 8.x (nebo kompatibilní)
- pip

## testovací scénáře ve složce `test/scenarios/`

## Rychlý start
1) Vytvoření a aktivace virtuálního prostředí:
```
python -m venv .venv
# Windows:
.\.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate
```

2) Instalace závislostí:
```
pip install -r requirements.txt
```

3) Nastavení konfigurace:
- Otevřete soubor `config/config.yaml` a vyplňte údaje k databázi (host, port, user, password, name).
- Nastavte `app.secret_key` na libovolný řetězec.

4) Příprava databáze:
```
# vytvoření schématu
mysql -u <user> -p -h <host> -P <port> < db/schema.sql
# volitelně základní data
mysql -u <user> -p -h <host> -P <port> portfolio_app < db/seed.sql
```

5) Spuštění aplikace:
```
# z kořene projektu
python -m src.app
```

Aplikace poběží na adrese:
```
http://127.0.0.1:5000/
```

## Hlavní stránky
- `/` – přehled zákazníků, produktů a posledních objednávek
- `/customers` – seznam zákazníků + import CSV
- `/products` – seznam produktů + import JSON
- `/orders` – seznam všech objednávek
- `/orders/new` – vytvoření nové objednávky
- `/orders/<id>` – detail objednávky
- `/report` – jednoduchý souhrnný report

## Import dat
- Zákazníci (CSV) na stránce `/customers`  
  Očekávané sloupce: `name,email,credit,is_active`
- Produkty (JSON) na stránce `/products`  
  Očekávaný formát: pole objektů, např.:
```
[
  {"name": "Item A", "price": 10.5, "stock": 5, "is_active": true},
  {"name": "Item B", "price": 20.0, "stock": 3, "is_active": false}
]
```