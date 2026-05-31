# -*- coding: utf-8 -*-
"""saketto のファビコンを生成（PIL）。ブランドマーク "saketto." を象る：
   墨(#1B1818)の角丸ベース + 米色(#F4EFE6)のセリフ "s" + 発酵朱(#B8493A)のドット。
   favicon.svg は手書き（鮮明・モダンブラウザ＋Google用）。本スクリプトは互換用の
   favicon.ico / favicon-32.png / apple-touch-icon.png(180) を出力する。
   使い方:  python gen_favicon.py
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = Path(__file__).resolve().parent.parent

INK = (27, 24, 24, 255)        # 墨 #1B1818
RICE = (244, 239, 230, 255)    # 米色 #F4EFE6
VERMILION = (184, 73, 58, 255) # 発酵朱 #B8493A

# セリフ（明朝寄り）フォント候補。最初に見つかったものを使う。
FONT_CANDIDATES = [
    "C:/Windows/Fonts/BIZ-UDMinchoM.ttc",
    "C:/Windows/Fonts/yumin.ttf",       # 游明朝
    "C:/Windows/Fonts/msmincho.ttc",    # MS明朝
    "C:/Windows/Fonts/georgia.ttf",
    "C:/Windows/Fonts/times.ttf",
]


def load_font(size):
    for p in FONT_CANDIDATES:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def render(S):
    """一辺 S px のアイコンを描いて返す。"""
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # 角丸の墨ベース
    d.rounded_rectangle([0, 0, S - 1, S - 1], radius=int(S * 0.22), fill=INK)
    # セリフ "s"
    font = load_font(int(S * 0.62))
    d.text((S * 0.42, S * 0.50), "s", font=font, fill=RICE, anchor="mm")
    # 発酵朱のドット（"saketto." のピリオド）
    r = S * 0.085
    cx, cy = S * 0.75, S * 0.64
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=VERMILION)
    return img


def main():
    master = render(256)
    # apple-touch-icon（角丸はOS側で処理されるが米色背景ではなく墨ベースのまま）
    master.resize((180, 180), Image.LANCZOS).save(REPO_ROOT / "apple-touch-icon.png")
    # 32px PNG
    master.resize((32, 32), Image.LANCZOS).save(REPO_ROOT / "favicon-32.png")
    # ICO（複数サイズ同梱）
    master.save(REPO_ROOT / "favicon.ico",
                sizes=[(16, 16), (32, 32), (48, 48)])
    print("  favicon.ico / favicon-32.png / apple-touch-icon.png  生成完了")
    print("  ※ favicon.svg は手書き（別管理）")


if __name__ == "__main__":
    main()
