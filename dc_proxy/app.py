# -*- coding: utf-8 -*-
"""Tkinter arayüzü — koyu tema, sade adımlar (OpenVPN → SSH → HTTP/S)."""

from __future__ import annotations

import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any
from uuid import uuid4

from . import profiles as profiles_mod
from .launcher import (
    build_preview_command,
    proxy_url_for,
    start_detached,
)
from .protocols import PROTOCOL_HINTS_TR, PROTOCOL_LABELS_TR, PROTOCOL_ORDER, fields_for
from .theme import (
    BG_ELEV,
    apply_dark_root,
    apply_dark_style,
    configure_hint_widget,
    configure_text_widget,
)


def _copy_to_clipboard(root: tk.Tk, text: str) -> None:
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()


class ToolTip:
    """Basit fare üstü ipucu."""

    def __init__(self, widget: tk.Widget, text: str) -> None:
        self.widget = widget
        self.text = text
        self._tip: tk.Toplevel | None = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def _show(self, _ev: Any = None) -> None:
        if self._tip or not self.text.strip():
            return
        try:
            x = self.widget.winfo_rootx() + 12
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        except tk.TclError:
            return
        self._tip = tk.Toplevel(self.widget)
        self._tip.wm_overrideredirect(True)
        self._tip.wm_geometry(f"+{x}+{y}")
        lbl = tk.Label(
            self._tip,
            text=self.text,
            justify=tk.LEFT,
            background="#21262d",
            foreground="#e6edf3",
            relief=tk.SOLID,
            borderwidth=1,
            padx=10,
            pady=8,
            font=("Segoe UI", 9) if sys.platform == "win32" else ("Helvetica", 9),
            wraplength=320,
        )
        lbl.pack()

    def _hide(self, _ev: Any = None) -> None:
        if self._tip:
            self._tip.destroy()
            self._tip = None


class DcProxyApp(tk.Tk):
    def __init__(self, *, start_hidden: bool = False) -> None:
        super().__init__()
        self.title("🌐 dc_proxy — Discord için bağlantılar")
        self.geometry("980x700")
        self.minsize(820, 560)

        apply_dark_root(self)
        self._style = ttk.Style(self)
        apply_dark_style(self._style)

        self._profiles: list[dict[str, Any]] = profiles_mod.load_profiles()
        self._settings: dict[str, Any] = profiles_mod.load_settings()
        self._current_pid: subprocess.Popen[Any] | None = None
        self._field_widgets: dict[str, Any] = {}
        self._form_frame: ttk.Frame | None = None
        self._form_canvas_win: int | None = None
        self._cli_start_hidden = bool(start_hidden)
        self._tray_icon: Any = None

        self._build_ui()
        self._load_profile_list()

        if sys.platform == "win32" and self._settings.get("start_with_windows"):
            from .windows_integration import sync_autostart_with_settings

            ok, msg = sync_autostart_with_settings(self._settings)
            if not ok:
                self._log(f"⚠️ Otomatik başlatma eşitlemesi: {msg}")

        self.protocol("WM_DELETE_WINDOW", self._on_user_close_window)
        self.after(500, self._maybe_start_hidden_from_cli)

    def _build_ui(self) -> None:
        root = ttk.Frame(self, padding=0)
        root.pack(fill=tk.BOTH, expand=True)

        header = ttk.Frame(root, padding=(20, 16, 20, 12))
        header.pack(fill=tk.X)

        title_row = ttk.Frame(header)
        title_row.pack(fill=tk.X)
        ttk.Label(title_row, text="🌐 dc_proxy", style="Title.TLabel").pack(side=tk.LEFT)
        ttk.Label(
            title_row,
            text="   Discord için VPN / proxy ayarlarını tek yerden yönetin",
            style="Subtitle.TLabel",
        ).pack(side=tk.LEFT)

        ttk.Label(
            header,
            text=(
                "Kayıtlı bilgiler yalnızca bu bilgisayarda saklanır. Sağlayıcıdan gelen dosya ve şifrelere güvenin."
            ),
            style="Muted.TLabel",
            wraplength=900,
            justify=tk.LEFT,
        ).pack(anchor=tk.W, pady=(8, 0))

        self.var_discord_exe = tk.StringVar(value=str(self._settings.get("discord_exe") or ""))
        if not (self.var_discord_exe.get() or "").strip() and sys.platform == "win32":
            guessed = profiles_mod.guess_discord_exe()
            if guessed:
                self.var_discord_exe.set(guessed)

        self._STEP_NAMES = ["Rehber", "Bağlantı", "Profiller", "Discord", "Program"]

        main_fill = ttk.Frame(root)
        main_fill.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 8))

        nav = ttk.Frame(main_fill, padding=(0, 4, 0, 8))
        nav.pack(fill=tk.X)
        ttk.Button(nav, text="◀ Önceki adım", style="Ghost.TButton", command=self._prev_step).pack(side=tk.LEFT, padx=(0, 10))
        self._step_banner = ttk.Label(
            nav,
            text=f"Adım 1 / {len(self._STEP_NAMES)} — Rehber",
            style="Subtitle.TLabel",
        )
        self._step_banner.pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(nav, text="Sonraki adım ▶", style="Ghost.TButton", command=self._next_step).pack(side=tk.RIGHT, padx=(10, 0))

        self._notebook = ttk.Notebook(main_fill)
        self._notebook.pack(fill=tk.BOTH, expand=True)

        # --- Sekme 1: Rehber ---
        tab_guide = ttk.Frame(self._notebook, padding=16)
        self._notebook.add(tab_guide, text="1  Rehber")
        ttk.Label(
            tab_guide,
            text="🎯 Nasıl kullanılır?",
            style="Accent.TLabel",
        ).pack(anchor=tk.W)
        ttk.Label(
            tab_guide,
            text=(
                "Üstteki sekmelere veya “Önceki / Sonraki adım” düğmelerine basarak sırayla ilerleyebilirsiniz.\n\n"
                "① Rehber — bu sayfa\n"
                "② Bağlantı — OpenVPN / SSH / proxy bilgilerinizi girin ve ▶️ Bağlan’a basın\n"
                "③ Profiller — sık kullandığınız ayarı kaydedip tek tıkla yükleyin\n"
                "④ Discord — Proxifier vb. için hangi Discord .exe kullanılacaksa seçin\n"
                "⑤ Program — Windows ile başlatma, tepsi modu, tam çıkış\n\n"
                "Küçük ekranda dikey kaydırmayı unutmayın; her bölüm kendi sekmesindedir."
            ),
            style="CardMuted.TLabel",
            justify=tk.LEFT,
            wraplength=820,
        ).pack(anchor=tk.W, pady=(12, 0))

        # --- Sekme 2: Bağlantı ---
        tab_conn = ttk.Frame(self._notebook, padding=8)
        self._notebook.add(tab_conn, text="2  Bağlantı")

        proto_card = ttk.LabelFrame(tab_conn, text="🔌 Bağlantı türü", padding=12)
        proto_card.pack(fill=tk.X, pady=(0, 8))

        proto_labels = [PROTOCOL_LABELS_TR[p] for p in PROTOCOL_ORDER]
        self.combo_proto = ttk.Combobox(
            proto_card,
            values=proto_labels,
            state="readonly",
            width=56,
        )
        self.combo_proto.set(proto_labels[0])
        self.combo_proto.pack(fill=tk.X, pady=(6, 0))
        self.combo_proto.bind("<<ComboboxSelected>>", self._on_proto_select)
        ToolTip(self.combo_proto, "Önerilen sıra: önce OpenVPN, sonra SSH, sonra HTTP.\nListe bu sıraya göre düzenlendi.")

        pw = ttk.PanedWindow(tab_conn, orient=tk.HORIZONTAL)
        pw.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

        mid = ttk.LabelFrame(pw, text="📝 Bilgileriniz", padding=(10, 12))

        canvas = tk.Canvas(mid, bg=BG_ELEV, highlightthickness=0, bd=0)
        vsb = ttk.Scrollbar(mid, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)

        inner = ttk.Frame(canvas)
        self._form_canvas_win = canvas.create_window((0, 0), window=inner, anchor=tk.NW)

        def _sync_scroll(_e: Any = None) -> None:
            canvas.configure(scrollregion=canvas.bbox("all"))
            try:
                cw = canvas.winfo_width()
                if cw > 1:
                    canvas.itemconfigure(self._form_canvas_win, width=cw)
            except tk.TclError:
                pass

        inner.bind("<Configure>", _sync_scroll)
        canvas.bind("<Configure>", lambda e: _sync_scroll())

        def _wheel(event: tk.Event[Any]) -> str | None:
            if sys.platform == "win32":
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            return "break"

        canvas.bind("<MouseWheel>", _wheel)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        self._form_canvas = canvas
        self.form_inner = inner
        self.form_container = inner

        right = ttk.Frame(pw, padding=0)

        hint_fr = ttk.LabelFrame(right, text="💡 Şu modda ne yapmalıyım?", padding=10)
        hint_fr.pack(fill=tk.BOTH, expand=True)

        self.hint_text = tk.Text(hint_fr, height=14, relief=tk.FLAT)
        configure_hint_widget(self.hint_text)
        self.hint_text.pack(fill=tk.BOTH, expand=True)

        actions = ttk.LabelFrame(right, text="⚡ İşlemler", padding=10)
        actions.pack(fill=tk.X, pady=(10, 0))

        b_go = ttk.Button(actions, text="▶️  Bağlan", style="Accent.TButton", command=self._connect)
        b_go.pack(fill=tk.X, pady=(0, 8))
        ToolTip(b_go, "VPN/proxy sürecini başlatır veya proxy adresini panoya kopyalar.")

        b_stop = ttk.Button(actions, text="⏹️  Durdur", style="Ghost.TButton", command=self._stop_process)
        b_stop.pack(fill=tk.X, pady=(0, 8))
        ToolTip(b_stop, "Bu uygulamanın başlattığı bağlantı sürecini sonlandırır.")

        b_uri = ttk.Button(actions, text="📋  Adresi kopyala", style="Ghost.TButton", command=self._copy_proxy_uri)
        b_uri.pack(fill=tk.X)
        ToolTip(b_uri, "HTTP/SOCKS türlerinde bağlantı satırını panoya alır.")

        pw.add(mid, weight=3)
        pw.add(right, weight=2)

        # --- Sekme 3: Profiller ---
        tab_prof = ttk.Frame(self._notebook, padding=16)
        self._notebook.add(tab_prof, text="3  Profiller")
        profile_card = ttk.LabelFrame(tab_prof, text="📂 Kayıtlı profiller", padding=14)
        profile_card.pack(fill=tk.X)
        self.var_profile_name = tk.StringVar()
        self.combo_profile = ttk.Combobox(profile_card, textvariable=self.var_profile_name, width=52)
        self.combo_profile.pack(fill=tk.X, pady=(6, 0))

        bt_row = ttk.Frame(profile_card)
        bt_row.pack(fill=tk.X, pady=(12, 0))
        b_load = ttk.Button(bt_row, text="📂 Yükle", style="Ghost.TButton", command=self._load_selected_profile)
        b_save = ttk.Button(bt_row, text="💾 Kaydet", style="Ghost.TButton", command=self._save_current_as_profile)
        b_del = ttk.Button(bt_row, text="🗑️ Sil", style="Danger.TButton", command=self._delete_profile)
        b_load.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 4))
        b_save.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=4)
        b_del.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(4, 0))
        ToolTip(b_load, "Listeden seçtiğiniz kayıtlı ayarı forma yükler.")
        ToolTip(b_save, "Şu anki formu bir isimle kaydeder; sonra tek tıkla geri çağırırsınız.")
        ToolTip(b_del, "Bu protokol için seçili profili kalıcı olarak siler.")
        ttk.Label(
            profile_card,
            text="Kayıtlar, geçerli bağlantı türüne göre listelenir. Önce “Bağlantı” sekmesinden türü seçin.",
            style="CardMuted.TLabel",
            wraplength=780,
            justify=tk.LEFT,
        ).pack(anchor=tk.W, pady=(14, 0))

        # --- Sekme 4: Discord ---
        tab_disc = ttk.Frame(self._notebook, padding=16)
        self._notebook.add(tab_disc, text="4  Discord")
        discord_card = ttk.LabelFrame(tab_disc, text="🎮 Discord’un programı (.exe)", padding=14)
        discord_card.pack(fill=tk.X)
        ttk.Label(
            discord_card,
            text=(
                "Proxy’yi yalnızca Discord’a uygulamak için (Proxifier vb.) hangi exe dosyası "
                "kullanılacaksa onu seçin.\n\n"
                "Genelde:\n• Güncelleyici: …\\Discord\\Update.exe\n"
                "• Asıl istemci: …\\Discord\\app-…\\Discord.exe\n\n"
                "Tam VPN (OpenVPN) kullanırken bu yol çoğu zaman zorunlu değildir."
            ),
            style="CardMuted.TLabel",
            justify=tk.LEFT,
            wraplength=780,
        ).pack(anchor=tk.W)
        disc_row = ttk.Frame(discord_card)
        disc_row.pack(fill=tk.X, pady=(12, 0))
        self.entry_discord = ttk.Entry(disc_row, textvariable=self.var_discord_exe)
        self.entry_discord.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(discord_card, text="📂 .exe seç…", style="Ghost.TButton", command=self._browse_discord_exe).pack(
            fill=tk.X, pady=(10, 0)
        )
        disc_bt = ttk.Frame(discord_card)
        disc_bt.pack(fill=tk.X, pady=(8, 0))
        ttk.Button(disc_bt, text="🔎 Otomatik bul", style="Ghost.TButton", command=self._auto_discord_exe).pack(
            side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 4)
        )
        ttk.Button(disc_bt, text="💾 Yolu kaydet", style="Ghost.TButton", command=self._save_discord_exe_setting).pack(
            side=tk.LEFT, expand=True, fill=tk.X, padx=(4, 0)
        )
        ttk.Button(
            discord_card,
            text="🚀 Discord’u bu dosyadan başlat",
            style="Ghost.TButton",
            command=self._launch_discord_exe,
        ).pack(fill=tk.X, pady=(12, 0))
        ToolTip(
            self.entry_discord,
            "Proxifier / benzeri: kuralda bu exe’yi gösterirsiniz.\n"
            "VPN (OpenVPN) kullanıyorsanız genelde tüm trafik zaten tüneldedir.",
        )

        # --- Sekme 5: Program ---
        tab_prog = ttk.Frame(self._notebook, padding=16)
        self._notebook.add(tab_prog, text="5  Program")
        prog_card = ttk.LabelFrame(tab_prog, text="⚙️ Çalışma şekli", padding=14)
        prog_card.pack(fill=tk.X)

        self.var_autostart = tk.BooleanVar(value=bool(self._settings.get("start_with_windows")))
        self.var_start_hidden_tray = tk.BooleanVar(value=bool(self._settings.get("start_hidden_to_tray")))
        self.var_tray_on_close = tk.BooleanVar(value=bool(self._settings.get("minimize_to_tray_on_close")))

        if sys.platform == "win32":
            cb_auto = ttk.Checkbutton(
                prog_card,
                text="🖥️ Windows ile oturum açılışında başlat",
                variable=self.var_autostart,
                command=self._on_autostart_changed,
            )
            cb_auto.pack(anchor=tk.W)
            ToolTip(
                cb_auto,
                "Kayıt defteri “Run” ile dc_proxy otomatik başlar.\n"
                "Tam bir Windows Hizmeti (services.msc) değildir.",
            )
            cb_sh = ttk.Checkbutton(
                prog_card,
                text="👻 Oturum açılışında tepsiye küçült (--hidden)",
                variable=self.var_start_hidden_tray,
                command=self._on_start_hidden_changed,
            )
            cb_sh.pack(anchor=tk.W, pady=(8, 0))
            ToolTip(cb_sh, "Yalnızca otomatik başlatırken pencere açılmaz; simge tepsisinde kalır.")
        else:
            ttk.Label(
                prog_card,
                text="🖥️ Otomatik başlatma bu sistemde kullanılamaz (yalnızca Windows).",
                style="CardMuted.TLabel",
                wraplength=560,
            ).pack(anchor=tk.W)

        cb_close = ttk.Checkbutton(
            prog_card,
            text="📌 Pencereyi kapatınca simge durumunda çalış",
            variable=self.var_tray_on_close,
            command=self._on_tray_on_close_changed,
        )
        cb_close.pack(anchor=tk.W, pady=(10, 0))
        ToolTip(
            cb_close,
            "X’e basınca uygulama kapanmaz; sistem tepsisinde kalır.\n"
            "Çıkmak için tepsi menüsünden veya buradan tam kapatın.",
        )
        ttk.Label(
            prog_card,
            text="Tepsi: pystray + Pillow gerekir. Yoksa pip install ile yükleyin.",
            style="CardMuted.TLabel",
            wraplength=560,
        ).pack(anchor=tk.W, pady=(10, 0))

        quit_row = ttk.Frame(prog_card)
        quit_row.pack(fill=tk.X, pady=(14, 0))
        ttk.Button(quit_row, text="⛔ Uygulamayı tamamen kapat", style="Danger.TButton", command=self._quit_fully).pack(
            fill=tk.X
        )

        self._notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        log_fr = ttk.LabelFrame(root, text="📜 İşlem kaydı (size özet)", padding=(12, 10))
        log_fr.pack(fill=tk.X, expand=False, padx=16, pady=(0, 12))

        self.log = tk.Text(log_fr, height=7, wrap=tk.WORD, state=tk.DISABLED)
        configure_text_widget(self.log)
        self.log.pack(fill=tk.BOTH, expand=True)

        self._rebuild_form()
        self._on_tab_changed()

    def _prev_step(self) -> None:
        nb = self._notebook
        try:
            i = nb.index(nb.select())
            if i > 0:
                nb.select(i - 1)
        except tk.TclError:
            pass

    def _next_step(self) -> None:
        nb = self._notebook
        try:
            i = nb.index(nb.select())
            last = nb.index("end") - 1
            if i < last:
                nb.select(i + 1)
        except tk.TclError:
            pass

    def _on_tab_changed(self, _event: Any = None) -> None:
        nb = self._notebook
        try:
            i = nb.index(nb.select())
            total = nb.index("end")
            name = self._STEP_NAMES[i] if i < len(self._STEP_NAMES) else ""
            self._step_banner.config(text=f"Adım {i + 1} / {total} — {name}")
        except tk.TclError:
            pass

    def _persist_settings_from_vars(self) -> None:
        self._settings["discord_exe"] = (self.var_discord_exe.get() or "").strip()
        self._settings["start_with_windows"] = bool(self.var_autostart.get())
        self._settings["start_hidden_to_tray"] = bool(self.var_start_hidden_tray.get())
        self._settings["minimize_to_tray_on_close"] = bool(self.var_tray_on_close.get())
        profiles_mod.save_settings(self._settings)

    def _on_autostart_changed(self) -> None:
        self._persist_settings_from_vars()
        if sys.platform == "win32":
            from .windows_integration import sync_autostart_with_settings

            ok, msg = sync_autostart_with_settings(self._settings)
            self._log(("✅ " if ok else "⚠️ ") + msg)

    def _on_start_hidden_changed(self) -> None:
        self._persist_settings_from_vars()
        if sys.platform == "win32" and bool(self.var_autostart.get()):
            from .windows_integration import sync_autostart_with_settings

            ok, msg = sync_autostart_with_settings(self._settings)
            self._log(("✅ " if ok else "⚠️ ") + msg)

    def _on_tray_on_close_changed(self) -> None:
        self._persist_settings_from_vars()

    def _ensure_tray_ready(self) -> bool:
        try:
            import pystray  # noqa: F401
            from PIL import Image  # noqa: F401

            from .tray_icon_image import build_icon_image

            build_icon_image()
            return True
        except Exception:
            return False

    def _ensure_tray_running(self) -> None:
        if self._tray_icon is not None:
            return
        import pystray

        from .tray_icon_image import build_icon_image

        image = build_icon_image()
        menu = pystray.Menu(
            pystray.MenuItem("🪟 Pencereyi göster", self._tray_show_window),
            pystray.MenuItem("⛔ Çıkış", self._tray_exit_from_tray),
        )
        self._tray_icon = pystray.Icon("dc_proxy", image, "dc_proxy — Discord proxy", menu)

        def run_icon() -> None:
            assert self._tray_icon is not None
            self._tray_icon.run()

        threading.Thread(target=run_icon, daemon=True).start()

    def _tray_show_window(self, icon: Any = None, item: Any = None) -> None:
        self.after(0, self._show_main_from_tray)

    def _show_main_from_tray(self) -> None:
        self.deiconify()
        self.lift()
        try:
            self.focus_force()
        except tk.TclError:
            pass

    def _tray_exit_from_tray(self, icon: Any = None, item: Any = None) -> None:
        self.after(0, self._quit_fully)

    def _maybe_start_hidden_from_cli(self) -> None:
        if not self._cli_start_hidden:
            return
        if not self._ensure_tray_ready():
            self._log(
                "⚠️ Tepsi kullanılamıyor (pip install pystray Pillow). "
                "--hidden yoksayıldı; pencere açık."
            )
            return
        self.withdraw()
        self._ensure_tray_running()
        self._log("ℹ️ Gizli başlatma: simge tepsisinden pencereyi açabilirsiniz.")

    def _on_user_close_window(self) -> None:
        if not bool(self.var_tray_on_close.get()):
            self._quit_fully()
            return
        if not self._ensure_tray_ready():
            if messagebox.askyesno(
                "Tepsi kullanılamıyor",
                "pystray veya Pillow eksik olabilir (pip install pystray Pillow).\n\n"
                "Şimdilik tamamen çıkmak ister misiniz?",
            ):
                self._quit_fully()
            return
        self.withdraw()
        self._ensure_tray_running()
        self._log("ℹ️ Simge durumunda çalışıyor (tepsi). Çıkmak için tepsi menüsünü kullanın.")

    def _quit_fully(self) -> None:
        self._stop_process(silent=True)
        if self._tray_icon is not None:
            try:
                self._tray_icon.stop()
            except Exception:
                pass
            self._tray_icon = None
        try:
            self.destroy()
        except tk.TclError:
            pass

    def _browse_discord_exe(self) -> None:
        path = filedialog.askopenfilename(
            title="Discord ile ilgili .exe seçin",
            filetypes=[("Windows uygulaması", "*.exe"), ("Tüm dosyalar", "*.*")],
        )
        if path:
            self.var_discord_exe.set(path)
            self._log(f"📎 Seçilen program: {path}")

    def _auto_discord_exe(self) -> None:
        guessed = profiles_mod.guess_discord_exe()
        if guessed:
            self.var_discord_exe.set(guessed)
            self._log(f"🔎 Otomatik bulundu: {guessed}")
            messagebox.showinfo("Tamam", f"Yol dolduruldu:\n{guessed}")
        else:
            messagebox.showinfo(
                "Bulunamadı",
                "Yaygın konumlarda Discord bulunamadı.\n\n"
                "Explorer’da Discord kısayoluna sağ tıklayıp “Dosya konumunu aç” "
                "diyerek .exe yolunu kopyalayabilirsiniz.",
            )

    def _save_discord_exe_setting(self) -> None:
        self._persist_settings_from_vars()
        self._log("💾 Discord program yolu ve çalışma ayarları kaydedildi.")
        messagebox.showinfo("Kaydedildi", "Discord .exe yolu ve seçenekler kaydedildi.")

    def _launch_discord_exe(self) -> None:
        raw = (self.var_discord_exe.get() or "").strip()
        if not raw:
            messagebox.showwarning("Eksik bilgi", "Önce Discord ile ilgili .exe dosyasını seçin.")
            return
        fp = Path(raw)
        if not fp.is_file():
            messagebox.showerror("Dosya yok", f"Bu yol bulunamadı:\n{raw}")
            return
        try:
            subprocess.Popen([str(fp)], cwd=str(fp.parent))
            self._log(f"🚀 Discord (veya seçilen program) başlatıldı:\n   {fp}")
        except OSError as e:
            messagebox.showerror("Başlatılamadı", str(e))

    def _set_hint_for_protocol(self, proto: str) -> None:
        text = PROTOCOL_HINTS_TR.get(proto, "Bu mod için ek bilgi yakında.")
        self.hint_text.config(state=tk.NORMAL)
        self.hint_text.delete("1.0", tk.END)
        self.hint_text.insert(tk.END, text)
        self.hint_text.config(state=tk.DISABLED)

    def _proto_key_from_label(self, label: str) -> str:
        for k, v in PROTOCOL_LABELS_TR.items():
            if v == label:
                return k
        return PROTOCOL_ORDER[0]

    def _on_proto_select(self, _ev: Any = None) -> None:
        self._rebuild_form()

    def _current_protocol_key(self) -> str:
        return self._proto_key_from_label(self.combo_proto.get())

    def _rebuild_form(self) -> None:
        if self._form_frame is not None:
            self._form_frame.destroy()
        self._field_widgets.clear()

        proto = self._current_protocol_key()
        self._set_hint_for_protocol(proto)
        self._load_profile_list()

        self._form_frame = ttk.Frame(self.form_container)
        self._form_frame.pack(fill=tk.BOTH, expand=True)

        rows = fields_for(proto)
        for i, spec in enumerate(rows):
            label = spec.get("label") or spec["name"]
            opt = spec.get("optional")
            lab_txt = label + (" (isteğe bağlı)" if opt else "")
            ttk.Label(self._form_frame, text=lab_txt + ":", style="Form.TLabel").grid(
                row=i, column=0, sticky=tk.NW, padx=(0, 12), pady=6
            )
            key = spec["key"]
            wtype = spec.get("widget", "entry")
            fr = ttk.Frame(self._form_frame)
            fr.grid(row=i, column=1, sticky=tk.EW, pady=6)
            self._form_frame.columnconfigure(1, weight=1)

            if wtype == "entry":
                var = tk.StringVar(value=str(spec.get("default", "")))
                ent = ttk.Entry(fr, textvariable=var)
                ent.pack(fill=tk.X)
                self._field_widgets[key] = var
            elif wtype == "password":
                var = tk.StringVar()
                ent = ttk.Entry(fr, textvariable=var, show="*")
                ent.pack(fill=tk.X)
                self._field_widgets[key] = var
            elif wtype == "text":
                txt = tk.Text(fr, height=5, wrap=tk.WORD)
                txt.configure(
                    bg="#21262d",
                    fg="#e6edf3",
                    insertbackground="#c9d1d9",
                    highlightthickness=1,
                    highlightbackground="#30363d",
                    relief=tk.FLAT,
                    font=("Segoe UI", 10) if sys.platform == "win32" else ("Helvetica", 10),
                    padx=8,
                    pady=8,
                )
                txt.pack(fill=tk.BOTH, expand=True)
                self._field_widgets[key] = txt
            elif wtype == "file":
                var = tk.StringVar()

                def browse(s=spec, v=var):
                    filt = s.get("filter") or [("Tüm dosyalar", "*.*")]
                    path = filedialog.askopenfilename(filetypes=filt)
                    if path:
                        v.set(path)

                ent = ttk.Entry(fr, textvariable=var)
                ent.pack(side=tk.LEFT, fill=tk.X, expand=True)
                btn = ttk.Button(fr, text="📂 Gözat…", style="Ghost.TButton", command=browse)
                btn.pack(side=tk.RIGHT, padx=(8, 0))
                self._field_widgets[key] = var

        self._load_selected_profile()

    def _collect_fields(self) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for key, w in self._field_widgets.items():
            if isinstance(w, tk.Text):
                out[key] = w.get("1.0", tk.END).rstrip()
            else:
                out[key] = w.get()
        return out

    def _apply_fields(self, data: dict[str, Any]) -> None:
        for key, w in self._field_widgets.items():
            val = data.get(key, "")
            if isinstance(w, tk.Text):
                w.delete("1.0", tk.END)
                w.insert(tk.END, str(val))
            elif isinstance(w, tk.StringVar):
                w.set(str(val))

    def _profile_list_names(self) -> list[str]:
        proto = self._current_protocol_key()
        return sorted(
            {p["name"] for p in self._profiles if p.get("protocol") == proto},
            key=str.lower,
        )

    def _load_profile_list(self) -> None:
        self.combo_profile["values"] = self._profile_list_names()

    def _save_current_as_profile(self) -> None:
        name = messagebox.askstring("💾 Profil kaydet", "Bu ayarlara vereceğiniz kısa isim (ör. Ev VPN):")
        if not name or not name.strip():
            return
        name = name.strip()
        proto = self._current_protocol_key()
        data = self._collect_fields()
        for i, p in enumerate(self._profiles):
            if p.get("protocol") == proto and p.get("name") == name:
                self._profiles[i] = {"id": p["id"], "name": name, "protocol": proto, "data": data}
                break
        else:
            self._profiles.append({"id": str(uuid4()), "name": name, "protocol": proto, "data": data})
        profiles_mod.save_profiles(self._profiles)
        self._load_profile_list()
        self.var_profile_name.set(name)
        self._log(f"✅ Profil kaydedildi: “{name}” ({proto})")

    def _load_selected_profile(self) -> None:
        name = self.var_profile_name.get().strip()
        proto = self._current_protocol_key()
        names = self._profile_list_names()
        if name and name not in names:
            self.var_profile_name.set("")
            name = ""
        if not name:
            return
        for p in self._profiles:
            if p.get("protocol") == proto and p.get("name") == name:
                self._apply_fields(p.get("data") or {})
                self._log(f"📂 Profil yüklendi: “{name}”")
                return

    def _delete_profile(self) -> None:
        name = self.var_profile_name.get().strip()
        proto = self._current_protocol_key()
        if not name:
            messagebox.showinfo("ℹ️ Bilgi", "Önce silinecek profili listeden seçin.")
            return
        if not messagebox.askyesno("🗑️ Silinsin mi?", f"“{name}” profili kalıcı olarak silinsin mi?"):
            return
        self._profiles = [p for p in self._profiles if not (p.get("protocol") == proto and p.get("name") == name)]
        profiles_mod.save_profiles(self._profiles)
        self.var_profile_name.set("")
        self._load_profile_list()
        self._log(f"🗑️ Silindi: “{name}”")

    def _connect(self) -> None:
        proto = self._current_protocol_key()
        fields = self._collect_fields()
        cmd, warn = build_preview_command(proto, fields)
        if warn:
            self._log(warn)
        if cmd:
            try:
                self._stop_process()
                self._current_pid = start_detached(cmd)
                self._log("▶️ Komut: " + " ".join(cmd))
                self._log(f"✅ Süreç başladı (PID {self._current_pid.pid}).")
            except Exception as e:  # noqa: BLE001
                messagebox.showerror("❌ Hata", str(e))
                self._log(str(e))
        else:
            uri = proxy_url_for(proto, fields)
            if uri:
                self._log("📋 Proxy adresi panoya yazıldı:\n   " + uri)
                _copy_to_clipboard(self, uri)
                messagebox.showinfo("✅ Tamam", "Proxy bağlantı satırı panoya kopyalandı.\nUygun programda yapıştırabilirsiniz.")
            elif warn:
                messagebox.showwarning("⚠️ Dikkat", warn)
            else:
                messagebox.showwarning("⚠️ Eksik bilgi", "Önce zorunlu alanları doldurun veya dosya seçin.")

    def _stop_process(self, *, silent: bool = False) -> None:
        if self._current_pid is None:
            if not silent:
                self._log("ℹ️ Durdurulacak aktif süreç yok.")
            return
        proc = self._current_pid
        self._current_pid = None
        try:
            if proc.poll() is None:
                if sys.platform == "win32":
                    subprocess.run(
                        ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                        capture_output=True,
                        check=False,
                    )
                    self._log(f"⏹️ Süreç sonlandırıldı (PID {proc.pid}).")
                else:
                    proc.terminate()
                    proc.wait(timeout=5)
                    self._log(f"⏹️ Süreç sonlandırıldı (PID {proc.pid}).")
        except Exception as e:  # noqa: BLE001
            self._log(f"⚠️ Durdurma: {e}")

    def _copy_proxy_uri(self) -> None:
        proto = self._current_protocol_key()
        uri = proxy_url_for(proto, self._collect_fields())
        if uri:
            _copy_to_clipboard(self, uri)
            self._log("📋 Panoya kopyalandı:\n   " + uri)
            messagebox.showinfo("✅ Kopyalandı", "Adres panoya alındı.")
        elif proto == "ssh_tunnel":
            d = self._collect_fields()
            bind = (d.get("socks_bind") or "127.0.0.1").strip()
            port = (d.get("socks_port") or "1080").strip()
            u = f"socks5://{bind}:{port}"
            _copy_to_clipboard(self, u)
            self._log("📋 SSH SOCKS önerisi:\n   " + u)
            messagebox.showinfo("✅ Kopyalandı", "Yerel SOCKS adresi panoya yazıldı.")
        else:
            messagebox.showinfo(
                "ℹ️ Bilgi",
                "Bu bağlantı türü için tek satırlık adres üretilemedi veya eksik alan var.\nÖnce bilgileri tamamlayın.",
            )

    def _log(self, line: str) -> None:
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END, line + "\n")
        self.log.see(tk.END)
        self.log.config(state=tk.DISABLED)


def run() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="dc_proxy — Discord için proxy / VPN profilleri")
    parser.add_argument(
        "--hidden",
        action="store_true",
        help="Başlangıçta ana pencereyi gösterme (sistem tepsisi; oturum açılışı ile uyumlu)",
    )
    ns = parser.parse_args()
    app = DcProxyApp(start_hidden=ns.hidden)
    app.mainloop()
