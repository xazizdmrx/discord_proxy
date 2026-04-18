# -*- coding: utf-8 -*-
"""Harici süreçleri başlatma (OpenVPN, SSH, xray vb.)."""

from __future__ import annotations

import os
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any


DEFAULT_OPENVPN_WINDOWS = Path(r"C:\Program Files\OpenVPN\bin\openvpn.exe")


def _split_extra_args(s: str | None) -> list[str]:
    if not s or not str(s).strip():
        return []
    try:
        return shlex.split(s.strip(), posix=os.name != "nt")
    except ValueError:
        return re.split(r"\s+", s.strip())


def launch_openvpn(fields: dict[str, Any]) -> tuple[list[str], str | None]:
    exe = fields.get("openvpn_exe") or ""
    if not exe or not Path(exe).is_file():
        if DEFAULT_OPENVPN_WINDOWS.is_file():
            exe = str(DEFAULT_OPENVPN_WINDOWS)
        else:
            exe = "openvpn"
    cfg = fields.get("config_path") or ""
    if not cfg or not Path(cfg).is_file():
        return [], "OpenVPN profil dosyası (.ovpn) seçin."
    cmd = [exe, "--config", cfg] + _split_extra_args(fields.get("extra_args"))
    return cmd, None


def launch_ssh(fields: dict[str, Any]) -> tuple[list[str], str | None]:
    host = (fields.get("host") or "").strip()
    if not host:
        return [], "SSH sunucu adresi girin."
    user = (fields.get("username") or "").strip()
    if not user:
        return [], "SSH kullanıcı adı girin."
    port = (fields.get("port") or "22").strip() or "22"
    bind = (fields.get("socks_bind") or "127.0.0.1").strip() or "127.0.0.1"
    socks_port = (fields.get("socks_port") or "1080").strip() or "1080"
    ssh_exe = fields.get("ssh_exe") or ""
    if ssh_exe and Path(ssh_exe).is_file():
        exe = ssh_exe
    else:
        exe = "ssh"
    cmd = [
        exe,
        "-N",
        "-D",
        f"{bind}:{socks_port}",
        "-p",
        port,
        "-o",
        "ExitOnForwardFailure=yes",
        "-o",
        "ServerAliveInterval=60",
        f"{user}@{host}",
    ]
    ident = fields.get("identity_file")
    if ident and Path(str(ident)).is_file():
        cmd[1:1] = ["-i", str(ident)]
    return cmd, None


def launch_wireguard(fields: dict[str, Any]) -> tuple[list[str], str | None]:
    cfg = fields.get("config_path") or ""
    if not cfg or not Path(cfg).is_file():
        return [], "WireGuard .conf dosyası seçin."
    wg = fields.get("wg_quick_exe") or ""
    if wg and Path(wg).is_file():
        return [wg, "up", str(cfg)], None
    return [], (
        "Windows'ta önce WireGuard istemcisine bu .conf'u ekleyin veya "
        "wg-quick.exe tam yolunu girin."
    )


def launch_xray_like(protocol: str, fields: dict[str, Any]) -> tuple[list[str], str | None]:
    binary = fields.get("binary") or ""
    if not binary or not Path(binary).is_file():
        return [], f"{protocol}: çekirdek binary dosyası seçin."
    cfg = fields.get("config_path") or ""
    if not cfg or not Path(cfg).is_file():
        return [], "Yapılandırma JSON dosyası seçin."
    cmd = [binary, "run", "-c", str(cfg)] + _split_extra_args(fields.get("extra_args"))
    return cmd, None


def launch_shadowsocks(fields: dict[str, Any]) -> tuple[list[str], str | None]:
    binary = fields.get("binary") or ""
    if not binary or not Path(binary).is_file():
        return [], "Shadowsocks/xray vb. binary seçin."
    raw = (fields.get("raw_config") or "").strip()
    if not raw:
        return [], "JSON veya komut satırı argümanlarını girin."
    # JSON ise geçici dosyaya yazılabilir — basit tut: kullanıcı argüman olarak vermiş olabilir
    if raw.startswith("{") or raw.startswith("["):
        import tempfile

        td = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8")
        td.write(raw)
        td.close()
        cmd = [binary, "-c", td.name]
        return cmd, None
    extra = _split_extra_args(raw)
    cmd = [binary] + extra
    return cmd, None


def build_preview_command(protocol: str, fields: dict[str, Any]) -> tuple[list[str], str | None]:
    fields = dict(fields)
    if protocol == "openvpn":
        return launch_openvpn(fields)
    if protocol == "ssh_tunnel":
        return launch_ssh(fields)
    if protocol == "wireguard":
        return launch_wireguard(fields)
    if protocol == "shadowsocks":
        return launch_shadowsocks(fields)
    if protocol in ("vmess", "vless", "trojan"):
        return launch_xray_like(protocol, fields)
    return [], "Bu protokol için bağlantı komutu üretilmez; proxy dizesini panoya kopyalayın."


def start_detached(cmd: list[str]) -> subprocess.Popen[Any]:
    """Windows'ta yeni konsol veya arka planda süreç."""
    creationflags = 0
    if sys.platform == "win32":
        creationflags = subprocess.CREATE_NEW_CONSOLE  # type: ignore[attr-defined]
    return subprocess.Popen(
        cmd,
        creationflags=creationflags,
        cwd=os.getcwd(),
    )


def proxy_url_for(protocol: str, fields: dict[str, Any]) -> str | None:
    """Discord / sistem proxy için URI (Bağlantı moduna bağlı)."""
    host = (fields.get("host") or "").strip()
    port = (fields.get("port") or "").strip()
    user = (fields.get("user") or "").strip()
    password = (fields.get("password") or "").strip()
    if not host or not port:
        return None
    auth = ""
    if user:
        from urllib.parse import quote

        auth = quote(user, safe="")
        if password:
            auth += ":" + quote(password, safe="")
        auth += "@"
    if protocol == "http":
        return f"http://{auth}{host}:{port}"
    if protocol == "https":
        return f"https://{auth}{host}:{port}"
    if protocol == "socks4":
        return f"socks4://{auth}{host}:{port}"
    if protocol == "socks5":
        return f"socks5://{auth}{host}:{port}"
    if protocol == "ftp":
        return f"ftp://{auth}{host}:{port}"
    return None
