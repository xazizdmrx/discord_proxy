# -*- coding: utf-8 -*-
"""Profil kaydet/yükle."""

from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

_LOG = logging.getLogger("dc_proxy.profiles")


def profiles_dir() -> Path:
    base = os.environ.get("LOCALAPPDATA") or str(Path.home() / ".local" / "share")
    d = Path(base) / "dc_proxy"
    d.mkdir(parents=True, exist_ok=True)
    return d


def profiles_path() -> Path:
    return profiles_dir() / "profiles.json"


def load_profiles() -> list[dict[str, Any]]:
    p = profiles_path()
    if not p.is_file():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
    except (json.JSONDecodeError, OSError):
        pass
    return []


def save_profiles(profiles: list[dict[str, Any]]) -> None:
    p = profiles_path()
    p.write_text(json.dumps(profiles, ensure_ascii=False, indent=2), encoding="utf-8")
    _LOG.info("profiles.json kaydedildi | kayıt_sayısı=%s yol=%s", len(profiles), p)


def settings_path() -> Path:
    return profiles_dir() / "settings.json"


def default_settings() -> dict[str, Any]:
    return {
        "discord_exe": "",
        "discord_update_exe": "",
        "discord_local_socks_port": "1080",
        "connection_goal": "socks",
        "start_with_windows": False,
        "minimize_to_tray_on_close": False,
        "start_hidden_to_tray": False,
    }


def load_settings() -> dict[str, Any]:
    out = default_settings()
    p = settings_path()
    if not p.is_file():
        return out
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            out["discord_exe"] = str(data.get("discord_exe") or "")
            out["discord_update_exe"] = str(data.get("discord_update_exe") or "")
            out["discord_local_socks_port"] = str(data.get("discord_local_socks_port") or "1080")
            _cg = str(data.get("connection_goal") or "socks").strip().lower()
            out["connection_goal"] = _cg if _cg in ("socks", "vpn") else "socks"
            out["start_with_windows"] = bool(data.get("start_with_windows"))
            out["minimize_to_tray_on_close"] = bool(data.get("minimize_to_tray_on_close"))
            out["start_hidden_to_tray"] = bool(data.get("start_hidden_to_tray"))
    except (json.JSONDecodeError, OSError):
        pass
    return out


def save_settings(settings: dict[str, Any]) -> None:
    p = settings_path()
    _cg = str(settings.get("connection_goal") or "socks").strip().lower()
    payload = {
        "discord_exe": str(settings.get("discord_exe") or ""),
        "discord_update_exe": str(settings.get("discord_update_exe") or ""),
        "discord_local_socks_port": str(settings.get("discord_local_socks_port") or "1080"),
        "connection_goal": _cg if _cg in ("socks", "vpn") else "socks",
        "start_with_windows": bool(settings.get("start_with_windows")),
        "minimize_to_tray_on_close": bool(settings.get("minimize_to_tray_on_close")),
        "start_hidden_to_tray": bool(settings.get("start_hidden_to_tray")),
    }
    p.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    _LOG.info(
        "settings.json kaydedildi | discord_exe_var=%s update_exe_var=%s win_start=%s tray_kapat=%s hidden_start=%s",
        bool(payload["discord_exe"]),
        bool(payload["discord_update_exe"]),
        payload["start_with_windows"],
        payload["minimize_to_tray_on_close"],
        payload["start_hidden_to_tray"],
    )


def _discord_base_dir() -> Path | None:
    if sys.platform != "win32":
        return None
    base_dir = os.environ.get("LOCALAPPDATA")
    if not base_dir:
        return None
    base = Path(base_dir) / "Discord"
    return base if base.is_dir() else None


def guess_discord_update_exe() -> str:
    """Güncelleme / oturum açmadan önce çalışan Update.exe."""
    base = _discord_base_dir()
    if not base:
        return ""
    upd = base / "Update.exe"
    return str(upd) if upd.is_file() else ""


def guess_discord_main_exe() -> str:
    """Asıl istemci: app-*\\Discord.exe."""
    base = _discord_base_dir()
    if not base:
        return ""
    for app_dir in sorted(base.glob("app-*"), reverse=True):
        exe = app_dir / "Discord.exe"
        if exe.is_file():
            return str(exe)
    return ""


def guess_discord_exe() -> str:
    """Geriye uyumluluk: önce ana istemci, yoksa güncelleyici."""
    m = guess_discord_main_exe()
    return m if m else guess_discord_update_exe()
