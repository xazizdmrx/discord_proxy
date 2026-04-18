# -*- coding: utf-8 -*-
"""Sistem tepsisi için basit PNG benzeri PIL görüntüsü."""

from __future__ import annotations


def build_icon_image():
    """pystray için küçük kare ikon."""
    from PIL import Image, ImageDraw, ImageFont

    size = 64
    img = Image.new("RGBA", (size, size), (13, 17, 23, 255))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([4, 4, size - 4, size - 4], radius=14, fill=(88, 166, 255, 255))
    try:
        font = ImageFont.truetype("segoeui.ttf", 28)
    except OSError:
        font = ImageFont.load_default()
    text = "D"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text(((size - tw) / 2, (size - th) / 2 - 2), text, fill=(13, 17, 23, 255), font=font)
    return img
