# -*- coding: utf-8 -*-
"""Harici süreçleri başlatma (OpenVPN, SSH, xray vb.)."""

from __future__ import annotations

import logging
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any

from .logutil import log_cmd_list

_LOG = logging.getLogger("dc_proxy.launcher")


DEFAULT_OPENVPN_WINDOWS = Path(r"C:\Program Files\OpenVPN\bin\openvpn.exe")


def openvpn_last_log_path() -> Path:
    """OpenVPN --log-append çıktısı (GUI’de gösterilir)."""
    from .profiles import profiles_dir  # noqa: PLC0415

    return profiles_dir() / "openvpn_last.log"


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
    cmd: list[str] = [exe, "--config", cfg]
    auth_file = (fields.get("auth_pass_file") or "").strip()
    if auth_file and Path(auth_file).is_file():
        cmd.extend(["--auth-user-pass", str(Path(auth_file).resolve())])
        _LOG.info("OpenVPN auth-user-pass dosyası kullanılacak | %s", Path(auth_file).name)
    log_p = openvpn_last_log_path()
    extra = _split_extra_args(fields.get("extra_args"))
    if "--log-append" not in extra and "--log" not in extra:
        cmd.extend(["--log-append", str(log_p)])
        _LOG.info("OpenVPN günlük dosyası | %s", log_p)
    cmd.extend(extra)
    _LOG.info("OpenVPN komut hazır | config=%s arg_sayısı=%s", Path(cfg).name, len(cmd))
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
    _LOG.info("SSH SOCKS komut hazır | hedef=%s@%s port=%s socks=%s:%s", user, host, bind, socks_port)
    return cmd, None


def launch_wireguard(fields: dict[str, Any]) -> tuple[list[str], str | None]:
    cfg = fields.get("config_path") or ""
    if not cfg or not Path(cfg).is_file():
        return [], "WireGuard .conf dosyası seçin."
    wg = fields.get("wg_quick_exe") or ""
    if wg and Path(wg).is_file():
        _LOG.info("WireGuard komut hazır | conf=%s wg=%s", Path(cfg).name, Path(wg).name)
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
    _LOG.info("%s komut hazır | json=%s", protocol, Path(cfg).name)
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
        _LOG.info("Shadowsocks geçici JSON yazıldı | dosya=%s", Path(td.name).name)
        return cmd, None
    extra = _split_extra_args(raw)
    cmd = [binary] + extra
    _LOG.info("Shadowsocks komut hazır (satır argümanları) | arg_sayısı=%s", len(cmd))
    return cmd, None


def build_preview_command(protocol: str, fields: dict[str, Any]) -> tuple[list[str], str | None]:
    fields = dict(fields)
    _LOG.debug("build_preview_command | protokol=%s", protocol)
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
    _LOG.info("Komut üretilmedi | protokol=%s (URI modu)", protocol)
    return [], "Bu protokol için bağlantı komutu üretilmez; proxy dizesini panoya kopyalayın."


def start_detached(cmd: list[str], *, hide_console: bool = True) -> subprocess.Popen[Any]:
    """Windows: varsayılan olarak konsol penceresi açılmaz (OpenVPN çıktısı --log-append ile dosyada)."""
    log_cmd_list(_LOG, cmd, prefix="start_detached")
    creationflags = 0
    if sys.platform == "win32":
        if hide_console and hasattr(subprocess, "CREATE_NO_WINDOW"):
            creationflags = subprocess.CREATE_NO_WINDOW  # type: ignore[attr-defined]
        elif hide_console:
            creationflags = 0x08000000
        else:
            creationflags = subprocess.CREATE_NEW_CONSOLE  # type: ignore[attr-defined]
    proc = subprocess.Popen(
        cmd,
        creationflags=creationflags,
        cwd=os.getcwd(),
    )
    _LOG.info("Alt süreç oluşturuldu | pid=%s hide_console=%s", proc.pid, hide_console)
    return proc


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
