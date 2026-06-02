# -*- coding: utf-8 -*-
"""saketto のOGP共有画像（assets/images/og.png, 1200x630）を生成。
米色地に墨の "saketto." ワードマーク＋発酵朱ドット＋タグライン。世界観準拠・SNS共有用。
使い方:  python gen_ogimage.py
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT = REPO_ROOT / "assets" / "images" / "og.png"

BG = (245, 240, 231)        # 米色 #F5F0E7
INK = (22, 16, 14)          # 墨 #16100E
INK_SOFT = (61, 54, 51)     # #3D3633
WARM = (122, 100, 71)       # #7A6447
VERMILION = (168, 53, 31)   # 発酵朱 #A8351F
LINE = (192, 182, 158)      # #C0B69E

MINCHO = [
    "C:/Windows/Fonts/yumin.ttf", "C:/Windows/Fonts/yuminl.ttf",
    "C:/Windows/Fonts/msmincho.ttc", "C:/Windows/Fonts/BIZ-UDMinchoM.ttc",
    "C:/Windows/Fonts/georgia.ttf", "C:/Windows/Fonts/times.ttf",
]
GOTHIC = [
    "C:/Windows/Fonts/YuGothR.ttc", "C:/Windows/Fonts/meiryo.ttc",
    "C:/Windows/Fonts/msgothic.ttc", "C:/Windows/Fonts/arial.ttf",
]


def font(cands, size):
    for p in cands:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def main():
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # 外枠の細罫（米色紙＋墨の縁取り。線は全周で統一）
    m = 40
    d.rectangle([m, m, W - m, H - m], outline=LINE, width=2)

    # 上部ラベル
    label = font(GOTHIC, 26)
    d.text((W / 2, 150), "C R A F T   S A K E   D A T A B A S E",
           font=label, fill=WARM, anchor="mm")

    # ワードマーク "saketto" ＋ 朱ドット（中央）
    wm = font(MINCHO, 150)
    word = "saketto"
    bbox = d.textbbox((0, 0), word, font=wm)
    ww = bbox[2] - bbox[0]
    cx = W / 2
    d.text((cx, 312), word, font=wm, fill=INK, anchor="mm")
    # 朱ドット（ワードマーク右下）
    dot_r = 17
    dot_x = cx + ww / 2 + 34
    dot_y = 312 + 52
    d.ellipse([dot_x - dot_r, dot_y - dot_r, dot_x + dot_r, dot_y + dot_r], fill=VERMILION)

    # タグライン
    tag = font(MINCHO, 38)
    d.text((W / 2, 452), "クラフトサケの図鑑", font=tag, fill=INK_SOFT, anchor="mm")
    sub = font(GOTHIC, 25)
    d.text((W / 2, 512), "副原料・蔵・地域・ジャンルで、米の新ジャンルを探す",
           font=sub, fill=WARM, anchor="mm")

    img.save(OUT)
    print(f"  {OUT.relative_to(REPO_ROOT)}  ({W}x{H})")


if __name__ == "__main__":
    main()
