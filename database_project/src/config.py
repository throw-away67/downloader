import os
import yaml

class ConfigError(Exception):
    pass

def load_config():
    cfg_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "config.yaml")
    if not os.path.exists(cfg_path):
        raise ConfigError(f"Missing config file at {cfg_path}")
    with open(cfg_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    # Validate minimal structure
    if "database" not in data or "app" not in data:
        raise ConfigError("Config must contain 'database' and 'app' sections.")
    db = data["database"]
    app = data["app"]
    required_db = ["host", "port", "user", "password", "name"]
    for key in required_db:
        if key not in db:
            raise ConfigError(f"Missing database.{key} in config.")
    if "secret_key" not in app:
        raise ConfigError("Missing app.secret_key in config.")
    app.setdefault("debug", False)
    app.setdefault("allowed_import_formats", ["csv", "json"])
    app.setdefault("max_upload_size_mb", 5)
    return data