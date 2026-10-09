"""The one place client values come from: config/client.yaml, plus the secrets in .env."""

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).parent
REQUIRED = [
    "client.name", "client.currency", "client.decimals",
    "warehouse.host", "warehouse.port", "warehouse.database", "warehouse.user",
    "inputs.orders", "inputs.payments", "inputs.customers", "inputs.payment_methods", "inputs.regions",
    "rules.late_after_days",
    "calendar.start", "calendar.end",
    "report.title", "report.check_month",
    "report.colours.data", "report.colours.text", "report.colours.muted",
    "report.colours.page", "report.colours.line", "report.colours.danger",
]


def load_config():
    cfg = yaml.safe_load((ROOT / "config" / "client.yaml").read_text(encoding="utf-8"))
    for key in REQUIRED:
        node = cfg
        for part in key.split("."):
            if not isinstance(node, dict) or part not in node:
                raise SystemExit(f"config/client.yaml is missing {key}")
            node = node[part]

    load_dotenv(ROOT / ".env")
    if not os.environ.get("DB_PASSWORD"):
        raise SystemExit(".env is missing DB_PASSWORD (copy .env.example to .env)")

    w = cfg["warehouse"]
    cfg["db_url"] = f"postgresql://{w['user']}:{os.environ['DB_PASSWORD']}@{w['host']}:{w['port']}/{w['database']}"
    cfg["input_dir"] = ROOT / "data" / "input"
    return cfg
