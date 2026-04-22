# -*- coding: utf-8 -*-
"""Dosyaya yapılandırılmış günlük (hassas içerik yazılmaz)."""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

_initialized = False


def setup_logging() -> Path:
    """%LOCALAPPDATA%\\dc_proxy\\dc_proxy.log (dönen dosya, ~512 KiB sonra dönüşümlü)."""
    global _initialized
    from .profiles import profiles_dir  # noqa: PLC0415 — döngü yok

    log_path = profiles_dir() / "dc_proxy.log"
    root = logging.getLogger("dc_proxy")
    if _initialized:
        return log_path
    root.setLevel(logging.DEBUG)
    root.handlers.clear()

    fh = RotatingFileHandler(
        log_path,
        maxBytes=512_000,
        backupCount=4,
        encoding="utf-8",
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    root.addHandler(fh)
    root.propagate = False
    _initialized = True
    return log_path


def log_cmd_list(logger: logging.Logger, cmd: list[str], *, prefix: str = "Komut") -> None:
    """Uzun argümanları kısaltır; şifre içeriği beklenmez (yalnızca argv)."""
    if not cmd:
        logger.info("%s: (boş)", prefix)
        return
    safe: list[str] = []
    for i, a in enumerate(cmd):
        p = Path(a) if len(a) < 2048 else None
        if p and len(str(p)) > 80 and p.suffix.lower() in (".ovpn", ".conf", ".json", ".pem", ".key"):
            safe.append(f".../{p.name}")
        elif len(a) > 120:
            safe.append(a[:117] + "...")
        else:
            safe.append(a)
    logger.info("%s: %s", prefix, safe)


def startup_banner() -> None:
    log = logging.getLogger("dc_proxy")
    frozen = getattr(sys, "frozen", False)
    exe = getattr(sys, "executable", "")
    log.info(
        "dc_proxy süreç başlangıcı | frozen=%s python=%s cwd=%s",
        frozen,
        exe,
        Path.cwd(),
    )


def sanitize_log_line(text: str) -> str:
    """proxy URI içindeki kullanıcı:şifre kısmını maskele."""
    if "://" not in text or "@" not in text:
        return text
    try:
        scheme, rest = text.split("://", 1)
        if "@" not in rest:
            return text
        _creds, host = rest.rsplit("@", 1)
        return f"{scheme}://***@{host}"
    except ValueError:
        return text
