# -*- coding: utf-8 -*-
"""Desteklenen protokoller, UI sırası ve alan şemaları."""

from typing import Any

# Kullanıcı isteği: OpenVPN birinci, SSH ikinci, HTTP/HTTPS üçüncü grupta öne çıksın.
PROTOCOL_ORDER = [
    "openvpn",
    "ssh_tunnel",
    "http",
    "https",
    "socks4",
    "socks5",
    "ftp",
    "shadowsocks",
    "vmess",
    "vless",
    "trojan",
    "wireguard",
]

PROTOCOL_LABELS_TR = {
    "openvpn": "OpenVPN (asıl kullanım)",
    "ssh_tunnel": "SSH tüneli (SOCKS üzerinden SSH)",
    "http": "HTTP proxy",
    "https": "HTTPS proxy",
    "ftp": "FTP proxy",
    "socks4": "SOCKS4",
    "socks5": "SOCKS5",
    "shadowsocks": "Shadowsocks",
    "vmess": "VMess",
    "vless": "VLESS",
    "trojan": "Trojan",
    "wireguard": "WireGuard (VPN benzeri)",
}

# Kısa kullanım rehberi (yeni kullanıcılar için)
PROTOCOL_HINTS_TR: dict[str, str] = {
    "openvpn": (
        "⚠️ Bu mod tam sistem VPN’idir (tüm PC trafiği tünelden gider). Yalnızca Discord için proxy istiyorsanız "
        "OpenVPN yerine SSH tüneli / SOCKS5 + Proxifier kullanın.\n\n"
        "① .ovpn profilini ve (önerilen) kimlik dosyasını seçin.\n"
        "② Kimlik dosyası: iki satır — 1. kullanıcı adı, 2. parola (UTF-8 metin).\n"
        "③ Proton VPN: kullanıcı adına sunucu eki gerekebilir (ör. …+b:0) — .ovpn içindeki yorumlara bakın.\n"
        "④ Windows’ta dc_proxy.exe veya OpenVPN’i «Yönetici olarak çalıştır» ile açın; aksi halde TAP/MTU veya «WFP: initialization failed» / «Erişim engellendi» oluşur.\n"
        "⑤ Bağlan sizi siyah konsol açmaz; ayrıntı %LOCALAPPDATA%\\dc_proxy\\openvpn_last.log ve aşağıdaki işlem kaydında son satırlar olarak gelir.\n"
        "💡 Tam VPN istiyorsanız: açıkken Discord da genelde ek ayarsız o yolu kullanır."
    ),
    "ssh_tunnel": (
        "① Sunucu adresi, kullanıcı adı ve (varsa) anahtar dosyası girin.\n"
        "② Yerel SOCKS portu (ör. 1080) sizin bilgisayarınızda açılır.\n"
        "③ Bağlan — sonra SOCKS adresini Proxifier vb. ile kullanın.\n"
        "④ Yalnızca Discord istiyorsanız: Discord sekmesinde «Proxifier talimatını panoya kopyala».\n"
        "💡 Örnek adres: socks5://127.0.0.1:1080"
    ),
    "http": (
        "① Proxy sağlayıcınızın verdiği sunucu ve portu yazın.\n"
        "② Kullanıcı/parola varsa doldurun; yoksa boş bırakın.\n"
        "③ Bağlan veya 📋 ile panoya kopyalanan adresi kullanın.\n"
        "💡 Windows’ta yalnızca HTTP’ye uyan programlara etki eder."
    ),
    "https": (
        "① HTTPS CONNECT proxy bilgilerini girin.\n"
        "② Bağlan veya 📋 ile URI’yi kopyalayın.\n"
        "💡 Discord masaüstü bazen doğrudan sisteme uymaz; Proxifier gerekebilir."
    ),
    "socks4": (
        "① SOCKS4 adres ve portunu girin.\n"
        "② Bağlan ile URI panoya yazılır.\n"
        "💡 SOCKS5 genelde daha yaygındır; mümkünse SOCKS5 deneyin."
    ),
    "socks5": (
        "① SOCKS5 sunucu ve portunu girin.\n"
        "② Gerekirse kullanıcı/parola ekleyin.\n"
        "③ Bağlan — panodaki socks5://… bağlantısını ilgili uygulamada kullanın.\n"
        "④ Uzak SOCKS doğrudan Proxifier’da da tanımlanabilir; yerel SSH SOCKS için Discord sekmesindeki talimatı kullanın."
    ),
    "ftp": (
        "① FTP proxy sunucusu ve portu (çoğu kez 21 veya sağlayıcıya özel).\n"
        "② Bu tür FTP ile ilgilidır; Discord için sık kullanılmaz.\n"
        "💡 Proxy URI’yi kopyalayıp uygun istemcide kullanın."
    ),
    "shadowsocks": (
        "① Bilgisayarınızdaki ss-local veya uyumlu programı (.exe) seçin.\n"
        "② JSON veya komut satırı metnini kutuya yapıştırın.\n"
        "③ Bağlan — süreç açılır; yerel SOCKS portunu not alın.\n"
        "💡 Doğru binary yolu olmazsa çalışmaz; sağlayıcı talimatına uyun."
    ),
    "vmess": (
        "① xray/sing-box gibi çekirdeği ve .json yapılandırmayı seçin.\n"
        "② Bağlan ile çalıştırılır.\n"
        "💡 Yapılandırma dosyası sağlayıcınızdan gelmelidir."
    ),
    "vless": (
        "① Desteklenen çekirdeği (binary) ve JSON profilini seçin.\n"
        "② Bağlan.\n"
        "💡 VLESS için genelde xray veya sing-box kullanılır."
    ),
    "trojan": (
        "① Trojan istemcisini ve JSON yapılandırmayı seçin.\n"
        "② Bağlan.\n"
        "💡 Dosyalar güvenilir kaynaktan olmalıdır."
    ),
    "wireguard": (
        "⚠️ Tam sistem VPN benzeri; trafik genelde tamamı tünelden gider — yalnızca Discord için SOCKS/SSH + Proxifier daha uygundur.\n\n"
        "① .conf dosyanızı seçin.\n"
        "② Windows’ta çoğu kez resmi WireGuard uygulamasına bu dosyayı ekleyin.\n"
        "③ İsteğe bağlı: wg-quick.exe tam yolu varsa burada kullanılır.\n"
        "💡 Tam VPN kullanıyorsanız Discord da çoğu kez otomatik o yolu kullanır."
    ),
}


def fields_for(protocol: str) -> list[dict[str, Any]]:
    """Her protokol için profil alanları (name, key, widget, opsiyonel)."""
    common_note = {
        "name": "not",
        "key": "notes",
        "widget": "text",
        "label": "Notlar (Discord ayarı vb.)",
        "optional": True,
    }
    if protocol == "openvpn":
        return [
            {"name": "OpenVPN exe", "key": "openvpn_exe", "widget": "file", "optional": True},
            {"name": "Profil (.ovpn)", "key": "config_path", "widget": "file", "filter": [("OpenVPN", "*.ovpn"), ("Tümü", "*.*")]},
            {
                "name": "Kimlik dosyası (isteğe bağlı, --auth-user-pass)",
                "key": "auth_pass_file",
                "widget": "file",
                "optional": True,
                "filter": [("Metin", "*.txt"), ("Tümü", "*.*")],
                "label": "Kimlik dosyası (2 satır: kullanıcı, parola)",
            },
            {"name": "Ek argümanlar", "key": "extra_args", "widget": "entry", "optional": True, "placeholder": "--auth-nocache veya boş"},
            common_note,
        ]
    if protocol == "ssh_tunnel":
        return [
            {"name": "Sunucu (host)", "key": "host", "widget": "entry"},
            {"name": "SSH portu", "key": "port", "widget": "entry", "default": "22"},
            {"name": "Kullanıcı adı", "key": "username", "widget": "entry"},
            {"name": "Özel anahtar (.pem)", "key": "identity_file", "widget": "file", "optional": True},
            {"name": "Yerel SOCKS adresi", "key": "socks_bind", "widget": "entry", "default": "127.0.0.1"},
            {"name": "Yerel SOCKS portu", "key": "socks_port", "widget": "entry", "default": "1080"},
            {"name": "SSH exe", "key": "ssh_exe", "widget": "file", "optional": True},
            common_note,
        ]
    if protocol in ("http", "https"):
        return [
            {"name": "Sunucu", "key": "host", "widget": "entry"},
            {"name": "Port", "key": "port", "widget": "entry", "default": "8080"},
            {"name": "Kullanıcı", "key": "user", "widget": "entry", "optional": True},
            {"name": "Parola", "key": "password", "widget": "password", "optional": True},
            common_note,
        ]
    if protocol in ("socks4", "socks5"):
        return [
            {"name": "Sunucu", "key": "host", "widget": "entry"},
            {"name": "Port", "key": "port", "widget": "entry", "default": "1080"},
            {"name": "Kullanıcı", "key": "user", "widget": "entry", "optional": True},
            {"name": "Parola", "key": "password", "widget": "password", "optional": True},
            common_note,
        ]
    if protocol == "ftp":
        return [
            {"name": "Sunucu", "key": "host", "widget": "entry"},
            {"name": "Port", "key": "port", "widget": "entry", "default": "21"},
            {"name": "Kullanıcı", "key": "user", "widget": "entry", "optional": True},
            {"name": "Parola", "key": "password", "widget": "password", "optional": True},
            common_note,
        ]
    if protocol == "wireguard":
        return [
            {"name": "WireGuard conf", "key": "config_path", "widget": "file", "filter": [("WireGuard", "*.conf"), ("Tümü", "*.*")]},
            {"name": "wg-quick / wireguard exe (ops.)", "key": "wg_quick_exe", "widget": "file", "optional": True},
            common_note,
        ]
    # shadowsocks, vmess, vless, trojan: harici çekirdek + şablon
    if protocol == "shadowsocks":
        return [
            {"name": "Çekirdek (ss-local, xray, vb.)", "key": "binary", "widget": "file"},
            {"name": "Yerel SOCKS port", "key": "local_port", "widget": "entry", "default": "1080"},
            {"name": "Sunucu (JSON / argümanlar)", "key": "raw_config", "widget": "text", "label": "JSON veya CLI argümanları"},
            common_note,
        ]
    if protocol in ("vmess", "vless", "trojan"):
        return [
            {"name": "Çekirdek (xray, sing-box, …)", "key": "binary", "widget": "file"},
            {"name": "Yapılandırma dosyası (.json)", "key": "config_path", "widget": "file", "filter": [("JSON", "*.json"), ("Tümü", "*.*")]},
            {"name": "Ek argümanlar", "key": "extra_args", "widget": "entry", "optional": True},
            common_note,
        ]
    return [common_note]
