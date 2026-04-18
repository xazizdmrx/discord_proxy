# -*- coding: utf-8 -*-
"""Profil kaydet/yükle."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any


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


def settings_path() -> Path:
    return profiles_dir() / "settings.json"


def default_settings() -> dict[str, Any]:
    return {
        "discord_exe": "",
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
            out["start_with_windows"] = bool(data.get("start_with_windows"))
            out["minimize_to_tray_on_close"] = bool(data.get("minimize_to_tray_on_close"))
            out["start_hidden_to_tray"] = bool(data.get("start_hidden_to_tray"))
    except (json.JSONDecodeError, OSError):
        pass
    return out


def save_settings(settings: dict[str, Any]) -> None:
    p = settings_path()
    payload = {
        "discord_exe": str(settings.get("discord_exe") or ""),
        "start_with_windows": bool(settings.get("start_with_windows")),
        "minimize_to_tray_on_close": bool(settings.get("minimize_to_tray_on_close")),
        "start_hidden_to_tray": bool(settings.get("start_hidden_to_tray")),
    }
    p.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def guess_discord_exe() -> str:
    """Windows: %LOCALAPPDATA%\\Discord altında yaygın yolları dener."""
    if sys.platform != "win32":
        return ""
    base_dir = os.environ.get("LOCALAPPDATA")
    if not base_dir:
        return ""
    base = Path(base_dir) / "Discord"
    if not base.is_dir():
        return ""
    candidates: list[str] = []
    for app_dir in sorted(base.glob("app-*"), reverse=True):
        discord_exe = app_dir / "Discord.exe"
        if discord_exe.is_file():
            candidates.append(str(discord_exe))
            break
    update_exe = base / "Update.exe"
    if update_exe.is_file():
        candidates.append(str(update_exe))
    return candidates[0] if candidates else ""
