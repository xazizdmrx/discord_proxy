# -*- coding: utf-8 -*-
"""Koyu tema (ttk + kök pencere) — yalnızca dc_proxy arayüzü."""

from __future__ import annotations

import sys
import tkinter as tk
from tkinter import ttk
from typing import Any

# Palet: yüksek kontrast, sade
BG = "#0d1117"
BG_ELEV = "#161b22"
SURFACE = "#21262d"
BORDER = "#30363d"
FG = "#e6edf3"
FG_MUTED = "#8b949e"
ACCENT = "#58a6ff"
ACCENT_HOVER = "#79b8ff"
DANGER = "#f85149"
SUCCESS = "#3fb950"
INSERT = "#c9d1d9"

FONTS: dict[str, Any] = {
    "title": ("Segoe UI", 20, "bold") if sys.platform == "win32" else ("Helvetica", 20, "bold"),
    "subtitle": ("Segoe UI", 10) if sys.platform == "win32" else ("Helvetica", 10),
    "body": ("Segoe UI", 10) if sys.platform == "win32" else ("Helvetica", 10),
    "small": ("Segoe UI", 9) if sys.platform == "win32" else ("Helvetica", 9),
    "mono": ("Cascadia Code", 9) if sys.platform == "win32" else ("Consolas", 9),
}


def apply_dark_root(root: tk.Tk) -> None:
    root.configure(bg=BG)
    try:
        root.option_add("*Dialog.msg.font", FONTS["body"])
        root.option_add("*Dialog.msg.wrapLength", "440")
    except tk.TclError:
        pass


def configure_hint_widget(w: tk.Text) -> None:
    w.configure(
        bg=BG_ELEV,
        fg=FG_MUTED,
        insertbackground=BG_ELEV,
        highlightthickness=0,
        relief="flat",
        padx=8,
        pady=10,
        font=FONTS["small"],
        wrap=tk.WORD,
        cursor="arrow",
        selectbackground=ACCENT,
        selectforeground="#0d1117",
    )


def configure_text_widget(w: tk.Text) -> None:
    w.configure(
        bg=SURFACE,
        fg=FG,
        insertbackground=INSERT,
        highlightthickness=1,
        highlightbackground=BORDER,
        highlightcolor=ACCENT,
        relief="flat",
        padx=10,
        pady=8,
        font=FONTS["mono"],
        selectbackground=ACCENT,
        selectforeground="#0d1117",
    )


def apply_dark_style(style: ttk.Style) -> None:
    style.theme_use("clam")

    style.configure(".", background=BG, foreground=FG, font=FONTS["body"])

    style.configure("TFrame", background=BG)
    style.configure("Card.TFrame", background=BG_ELEV, relief="flat")
    style.configure("Elev.TFrame", background=BG_ELEV)

    style.configure("TLabel", background=BG, foreground=FG)
    style.configure("Muted.TLabel", background=BG, foreground=FG_MUTED, font=FONTS["small"])
    style.configure("Title.TLabel", background=BG, foreground=FG, font=FONTS["title"])
    style.configure("Subtitle.TLabel", background=BG, foreground=FG_MUTED, font=FONTS["subtitle"])
    style.configure("Card.TLabel", background=BG_ELEV, foreground=FG)
    style.configure("CardMuted.TLabel", background=BG_ELEV, foreground=FG_MUTED, font=FONTS["small"])
    style.configure("Accent.TLabel", background=BG_ELEV, foreground=ACCENT, font=FONTS["body"])

    style.configure("Form.TLabel", background=BG_ELEV, foreground=FG, font=FONTS["body"])
    style.configure("FormMuted.TLabel", background=BG_ELEV, foreground=FG_MUTED, font=FONTS["small"])

    style.configure(
        "TLabelframe",
        background=BG_ELEV,
        foreground=ACCENT,
        bordercolor=BORDER,
        relief="solid",
        borderwidth=1,
    )
    style.configure("TLabelframe.Label", background=BG_ELEV, foreground=ACCENT, font=("Segoe UI", 10, "bold") if sys.platform == "win32" else ("Helvetica", 10, "bold"))

    style.configure(
        "Accent.TButton",
        background=ACCENT,
        foreground="#0d1117",
        borderwidth=0,
        focuscolor=ACCENT,
        font=("Segoe UI", 10, "bold") if sys.platform == "win32" else ("Helvetica", 10, "bold"),
        padding=(16, 10),
    )
    style.map(
        "Accent.TButton",
        background=[("active", ACCENT_HOVER), ("pressed", ACCENT_HOVER), ("disabled", BORDER)],
        foreground=[("disabled", FG_MUTED)],
    )

    style.configure(
        "Ghost.TButton",
        background=SURFACE,
        foreground=FG,
        borderwidth=1,
        relief="flat",
        padding=(12, 8),
    )
    style.configure("Ghost.TButton", focuscolor=SURFACE)
    style.map(
        "Ghost.TButton",
        background=[("active", "#2d333b"), ("pressed", BORDER)],
        foreground=[
            ("active", FG),
            ("pressed", FG),
            ("disabled", FG_MUTED),
        ],
        focuscolor=[("focus", SURFACE)],
    )

    style.configure(
        "Danger.TButton",
        background=SURFACE,
        foreground=DANGER,
        borderwidth=1,
        padding=(12, 8),
        focuscolor=SURFACE,
    )
    style.map(
        "Danger.TButton",
        background=[("active", "#2d333b"), ("pressed", BORDER)],
        foreground=[("active", DANGER), ("pressed", DANGER)],
        focuscolor=[("focus", SURFACE)],
    )

    # Çalışma şekli vb.: hover’da metin kaybolmasın (clam varsayılanı bazen fg’yi silik yapıyor)
    style.configure(
        "TCheckbutton",
        background=BG_ELEV,
        foreground=FG,
        borderwidth=0,
        focustickness=1,
        focuscolor=BORDER,
        indicatorrelief="flat",
        indicatorbackground=SURFACE,
        indicatorforeground=ACCENT,
        padding=(2, 4),
    )
    style.map(
        "TCheckbutton",
        background=[("active", BG_ELEV), ("disabled", BG_ELEV)],
        foreground=[("active", FG), ("disabled", FG_MUTED)],
        indicatorcolor=[
            ("selected pressed", ACCENT_HOVER),
            ("selected", ACCENT),
            ("pressed", FG_MUTED),
            ("!selected", SURFACE),
        ],
    )

    style.configure(
        "TEntry",
        fieldbackground=SURFACE,
        foreground=FG,
        insertcolor=INSERT,
        borderwidth=1,
        relief="flat",
    )
    style.map("TEntry", fieldbackground=[("disabled", BORDER)])

    style.configure(
        "TCombobox",
        fieldbackground=SURFACE,
        foreground=FG,
        borderwidth=1,
        arrowcolor=FG,
        padding=4,
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", SURFACE), ("disabled", BORDER)],
        selectbackground=[("readonly", ACCENT)],
        selectforeground=[("readonly", "#0d1117")],
    )

    style.configure("Horizontal.TScrollbar", troughcolor=BG_ELEV, background=BORDER, bordercolor=BG_ELEV)
    style.configure("Vertical.TScrollbar", troughcolor=BG_ELEV, background=BORDER, bordercolor=BG_ELEV)

    style.configure(
        "TNotebook",
        background=BG,
        borderwidth=0,
        tabmargins=[8, 4, 6, 0],
    )
    style.configure(
        "TNotebook.Tab",
        background=SURFACE,
        foreground=FG,
        padding=[14, 8],
        borderwidth=0,
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", BG_ELEV), ("active", "#2d333b")],
        foreground=[
            ("selected", ACCENT),
            ("active", FG),
            ("!selected", FG_MUTED),
        ],
    )
