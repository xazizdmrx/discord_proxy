# -*- coding: utf-8 -*-
"""Windows yardımcıları."""

from __future__ import annotations

import sys


def is_windows_admin() -> bool:
    """Geçerli süreç yükseltilmiş (Yönetici) oturumda mı?"""
    if sys.platform != "win32":
        return True
    try:
        import ctypes

        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False
