# -*- coding: utf-8 -*-
"""Windows: oturum açılışında çalıştır (Kayıt defteri Run). Gerçek NT servisi değildir."""

from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path
from typing import Any

_LOG = logging.getLogger("dc_proxy.windows")

RUN_VALUE_NAME = "DcProxy"
_RUN_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"


def build_launch_command(hidden: bool) -> str:
    """Kayıt defteri Run için tek satırlık komut (tırnaklı yollar)."""
    frozen = getattr(sys, "frozen", False) and hasattr(sys, "executable")
    args_hidden = ["--hidden"] if hidden else []

    if frozen:
        exe = Path(sys.executable).resolve()
        parts = [str(exe)] + args_hidden
        return subprocess.list2cmdline(parts)

    project_root = Path(__file__).resolve().parents[1]
    main_py = project_root / "main.py"
    py_dir = Path(sys.executable).resolve().parent
    pythonw = py_dir / "pythonw.exe"
    launcher = pythonw if pythonw.is_file() else Path(sys.executable).resolve()
    parts = [str(launcher), str(main_py.resolve())] + args_hidden
    return subprocess.list2cmdline(parts)


def set_autostart(enabled: bool, hidden: bool) -> tuple[bool, str]:
    """Run anahtarına yazar veya kaldırır."""
    if sys.platform != "win32":
        return False, "Bu özellik yalnızca Windows için."

    import winreg  # noqa: PLC0415

    access = winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_PATH, 0, access)
    except OSError as e:
        return False, str(e)
    try:
        if not enabled:
            try:
                winreg.DeleteValue(key, RUN_VALUE_NAME)
                _LOG.info("Run kaydı silindi | %s", RUN_VALUE_NAME)
            except FileNotFoundError:
                _LOG.info("Run kaydı zaten yoktu | %s", RUN_VALUE_NAME)
                pass
            except OSError as e:
                _LOG.warning("Run silinemedi: %s", e)
                return False, str(e)
            return True, "Otomatik başlatma kapatıldı."

        cmd = build_launch_command(hidden=hidden)
        winreg.SetValueEx(key, RUN_VALUE_NAME, 0, winreg.REG_SZ, cmd)
        _LOG.info("Run kaydı yazıldı | hidden=%s komut_uzunluk=%s", hidden, len(cmd))
        return True, "Otomatik başlatma Windows’a kaydedildi."
    finally:
        winreg.CloseKey(key)


def sync_autostart_with_settings(settings: dict[str, Any]) -> tuple[bool, str]:
    """start_with_windows ve start_hidden_to_tray ile Run satırını eşitler."""
    enabled = bool(settings.get("start_with_windows"))
    hidden = bool(settings.get("start_hidden_to_tray"))
    return set_autostart(enabled, hidden)
