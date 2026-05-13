"""Optional TLS for MySQL (Aiven, RDS, etc.). Controlled by MYSQL_USE_SSL and MYSQL_SSL_CA / MYSQL_SSL_CA_PEM."""
from __future__ import annotations

import os
import ssl
import tempfile
from pathlib import Path

_pem_temp_path: str | None = None


def _pem_tempfile_from_env() -> str | None:
    """If MYSQL_SSL_CA_PEM is set, write it once to a temp file and return the path."""
    global _pem_temp_path
    raw = os.environ.get("MYSQL_SSL_CA_PEM", "").strip()
    if not raw:
        return None
    if _pem_temp_path and Path(_pem_temp_path).is_file():
        return _pem_temp_path
    pem = raw.replace("\\n", "\n")
    fd, path = tempfile.mkstemp(prefix="mysql_ca_", suffix=".pem", text=True)
    with os.fdopen(fd, "w") as f:
        f.write(pem)
    _pem_temp_path = path
    return path


def _ssl_context() -> ssl.SSLContext | None:
    if os.environ.get("MYSQL_USE_SSL", "").lower() not in ("1", "true", "yes"):
        return None
    ctx = ssl.create_default_context()
    ca_path = os.environ.get("MYSQL_SSL_CA", "").strip()
    pem_path = _pem_tempfile_from_env()
    if pem_path:
        ctx.load_verify_locations(pem_path)
    elif ca_path:
        p = Path(ca_path)
        if p.is_file():
            ctx.load_verify_locations(str(p))
    return ctx


def django_mysql_ssl_options() -> dict:
    ctx = _ssl_context()
    if ctx is None:
        return {}
    return {"ssl": ctx}


def pymysql_ssl_kwargs() -> dict:
    ctx = _ssl_context()
    if ctx is None:
        return {}
    return {"ssl": ctx}
