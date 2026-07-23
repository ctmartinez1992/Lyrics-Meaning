import importlib
import os
from pathlib import Path


def _load_dotenv_file(dotenv_path: Path | None = None) -> None:
    target = dotenv_path or (Path(__file__).resolve().parents[2] / ".env")
    if not target.exists():
        return

    for raw_line in target.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue

        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]

        os.environ.setdefault(key, value)


_load_dotenv_file()

_ENV = os.getenv("DJANGO_ENV", "local").lower()
_SETTINGS_MODULE = {
    "local": "config.settings.local",
    "dev": "config.settings.dev",
    "prod": "config.settings.prod",
}.get(_ENV, "config.settings.local")

_module = importlib.import_module(_SETTINGS_MODULE)

for _name in dir(_module):
    if _name.isupper():
        globals()[_name] = getattr(_module, _name)
