# -*- coding: utf-8 -*-
"""Yalnızca Discord için SOCKS + Proxifier kılavuz metni (VPN değil)."""

from __future__ import annotations


def proxifier_guide_tr(
    *,
    local_port: int,
    update_exe: str,
    discord_exe: str,
) -> str:
    """Proxifier için adım adım Türkçe metin; exe yolları kullanıcıdan."""
    upd = (update_exe or "").strip() or "(yukarıda tanımlı Update.exe yolunu yazın)"
    dis = (discord_exe or "").strip() or "(yukarıda tanımlı Discord.exe yolunu yazın)"
    return (
        "dc_proxy — Yalnızca Discord (proxy, tam sistem VPN değil)\n"
        "=======================================================\n\n"
        "OpenVPN tüm bilgisayarı tünel eder; «sadece Discord» için kullanmayın.\n"
        "Aşağıdaki akış: önce yerel SOCKS, sonra yalnızca Discord süreçlerini oraya yönlendirir.\n\n"
        "ADIM 1 — Yerel SOCKS dinleyicisi\n"
        "--------------------------------\n"
        "Bağlantı sekmesinde birini seçin ve ▶ Bağlan ile yerel portu açın:\n"
        "  • «SSH tüneli» → çoğu kurulumda 127.0.0.1 üzerinde SOCKS (ör. -D ile),\n"
        "  • veya «SOCKS5» → sağlayıcınızın verdiği uzak SOCKS (dc_proxy URI kopyalar).\n"
        "Bu kılavuz, Discord’u şu adrese yönlendirmeyi varsayar:\n"
        f"  → 127.0.0.1:{local_port}  (SOCKS5)\n\n"
        "ADIM 2 — Proxifier’da proxy sunucusu\n"
        "-------------------------------------\n"
        "Proxifier → Profile → Proxy Servers → Add…\n"
        "  Address: 127.0.0.1\n"
        f"  Port: {local_port}\n"
        "  Protocol: SOCKS Version 5\n"
        "(Kimlik gerekiyorsa Proxifier’da girin; SSH yerel SOCKS çoğu kez şifresizdir.)\n\n"
        "ADIM 3 — Kurallar (Discord’un iki exe’si)\n"
        "-----------------------------------------\n"
        "Proxifier → Rules → Add… — Önce dar kapsam, doğru sıra önemli.\n\n"
        "Kural A — Güncelleme süreci\n"
        "  Name: Discord Update\n"
        f'  Applications: tam yol → "{upd}"\n'
        "  Target Hosts: Any\n"
        "  Action: SOCKS5 127.0.0.1 (yukarıda eklediğiniz sunucu)\n\n"
        "Kural B — Ana istemci\n"
        "  Name: Discord App\n"
        f'  Applications: tam yol → "{dis}"\n'
        "  Target Hosts: Any\n"
        "  Action: Aynı SOCKS5\n\n"
        "Varsayılan «Default» kuralınız «Direct» kalsın; böylece tarayıcı vb. doğrudan çıkar.\n\n"
        "Not: Ses (UDP/WebRTC) her ortamda proxyle tam taşınmayabilir; sorun olursa Proxifier dokümantasyonuna bakın.\n"
    )
