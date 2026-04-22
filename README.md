# dc_proxy

Discord ve ilgili bağlantılar için **VPN / proxy profillerini** tek pencerede toplayan küçük bir masaüstü uygulamasıdır. OpenVPN, SSH SOCKS, HTTP/S ve diğer modlar için alanları doldurur; mümkün olanlarda harici programları (OpenVPN, SSH, xray vb.) başlatır.

## Gereksinimler

- Windows 10/11 (geliştirme ve otomatik başlatma için tasarlandı; tkinter olan diğer sistemlerde de çalışabilir)
- Python **3.10+**
- Tepsi (simge durumu) özelliği için: **pystray** ve **Pillow**

```powershell
cd dc_proxy
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

## Öne çıkanlar

- Üstte **sekme menüsü** ve **Önceki adım / Sonraki adım** ile sıralı kullanım (küçük ekranda da her bölüm tek sekmede; sol sütunda kaybolma yok)
- Sekmeler: **Rehber** → **Bağlantı** → **Profiller** → **Discord** → **Program**
- Koyu tema arayüz, protokole göre Türkçe ipuçları  
- Discord `.exe` yolu (Proxifier vb. için)  
- **Çalışma şekli**  
  - **Windows ile oturum açılışında başlat**: Kayıt defteri `Run` anahtarına yazılır (tam bir Windows **Hizmeti** / `services.msc` değildir).  
  - **Oturum açılışında tepsiye küçült**: Otomatik başlatma satırına `--hidden` eklenir; pencere açılmadan sistem tepsisinde kalır.  
  - **Pencereyi kapatınca simge durumunda çalış**: Üst çarpı (`X`) uygulamayı kapatmaz; çıkmak için tepsi menüsündeki **Çıkış** veya **Uygulamayı tamamen kapat** kullanılır.

## Tek exe oluşturma (PyInstaller)

Tek dosya, konsolsuz exe için:

```powershell
pip install pyinstaller
python -m PyInstaller --noconfirm dc_proxy.spec
```

Çıktı: `dist\dc_proxy.exe`

İlk kurulumdan sonra exe’yi taşıdıysanız, **Windows ile başlat** seçeneğini bir kez kapatıp tekrar açarak kayıt defteri yolunun güncellenmesini sağlayın.

### Gizli başlatma (`--hidden`)

Kayıtlı otomatik başlatma ile birlikte kullanılır; doğrudan test için:

```powershell
.\dist\dc_proxy.exe --hidden
```

## Ayar dosyaları

- `%LOCALAPPDATA%\dc_proxy\settings.json` — `discord_update_exe`, `discord_exe`, `discord_local_socks_port`, `connection_goal` (`socks` = proxy/SOCKS önerisi, `vpn` = tam VPN), çalışma seçenekleri  
- `%LOCALAPPDATA%\dc_proxy\profiles.json` — bağlantı profilleri  
- `%LOCALAPPDATA%\dc_proxy\dc_proxy.log` — tüm çalışma akışı (başlangıç, sekmeler, bağlan, tepsi, kayıt; max. ~512 KiB, dönen yedekler)  
  - **Not:** Parolalar ve proxy URI’deki kimlik bilgisi dosyada **maskelenir**; yine de bu dosyayı paylaşmayın.  

## Notlar

- **OpenVPN (Windows):** TAP / WFP için çoğu zaman **dc_proxy.exe / OpenVPN’i yönetici olarak çalıştırın**. Kimlik için **Kimlik dosyası** (iki satır `.txt`). Bağlanınca siyah konsol yerine çıktı **`%LOCALAPPDATA%\dc_proxy\openvpn_last.log`** dosyasına yazılır; işlem kaydında otomatik özetlenir. Proton’da kullanıcı adına `…+b:0` gibi ek gerekebilir (`.ovpn` yorumları).  
- **OpenVPN = tam PC VPN’i** (varsayılan olarak internetin tamamı tünelden). *Sadece Discord* istiyorsanız OpenVPN ile “seçici” olmaz; **yerel SOCKS** (SSH tüneli, Shadowsocks/xray yerel port, sağlayıcı SOCKS5) + **Proxifier** (veya benzeri) ile **Update.exe** ve **Discord.exe** için kural verin. Proton’da “split tunneling” yalnızca tam istemci uygulamasında anlamlıdır; `.ovpn` ile OpenVPN dc_proxy’den açıldığında yine sistem geneli tünel davranışına yakınsır.  
- Sistem tepsisi için `pip install pystray Pillow` zorunludur; yoksa “simge durumunda çalış” seçeneği tam çıkış önerir.

## Lisans

Projeyi kendi kullanımınıza göre düzenleyebilirsiniz; harici VPN/proxy araçlarının lisansları size aittir.
