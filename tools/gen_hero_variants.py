# -*- coding: utf-8 -*-
"""saketto / ヒーロー背景画像バリエーション生成

社長指示: 他の画像も試してみたい
現状 hero.png（米粒・麹・washi）に対し、別方向の候補を複数生成して比較する。

CLAUDE.md ルール:
- 必ず Vertex AI 経由（クレカ直課金禁止）
- gemini-3-pro-image-preview / location="global"
- 蔵固有の画像は生成しない（素材・抽象イメージのみ）

実行: cd ツール/saketto_repo/tools && python gen_hero_variants.py
出力: saketto_repo/assets/images/hero_*.png
"""

import os
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
IMG_DIR = REPO_ROOT / "assets" / "images"
IMG_DIR.mkdir(parents=True, exist_ok=True)

project = os.environ.get("GOOGLE_CLOUD_PROJECT")
if not project:
    print("ERROR: GOOGLE_CLOUD_PROJECT 環境変数が未設定")
    sys.exit(1)

from google import genai
client = genai.Client(vertexai=True, project=project, location="global")

STYLE = ("Editorial magazine still-life photography. Warm cream paper background "
         "(color #F5F0E7), sumi ink black accents, subtle rust red (#B33A2A) highlights, "
         "wood brown (#8B7355) shadows. Soft diffused natural window light from upper left. "
         "Generous negative space, minimal Japanese aesthetic, magazine quality. "
         "No text, no logos, no signage, no specific brewery or brand marks.")
LANDSCAPE = STYLE + " Landscape orientation 16:9."

# 背景として薄く敷くので、余白が広く・主題が右寄り・暗すぎないものが向く
IMAGES = [
    ("hero_nigori",
     "An elegant editorial still-life: cloudy white nigori-style craft sake (doburoku) "
     "in a clear small glass, gentle swirling rice sediment suspended in the milky liquid, "
     "placed on warm cream handmade washi paper. A few loose golden rice grains beside it. " + LANDSCAPE),

    ("hero_kioke",
     "Atmospheric editorial detail of a traditional Japanese wooden fermentation vat (kioke) — "
     "beautiful cedar wood grain, iron hoop, soft shadow — viewed from above at an angle on a "
     "cream-toned studio surface. Calm, crafted, artisanal mood. Generous empty space. " + LANDSCAPE),

    ("hero_moromi",
     "Macro editorial close-up of fermenting sake mash (moromi) — golden rice grains and "
     "white koji blooming in gently bubbling cloudy liquid, tiny fermentation bubbles catching "
     "soft light. Warm cream and amber tones, painterly and organic. " + LANDSCAPE),

    ("hero_ingredients",
     "Editorial flat-lay overhead: the building blocks of craft sake arranged with generous "
     "spacing on warm cream washi paper — a small mound of golden rice, white koji culture, "
     "a few green hop cones, a slice of yellow yuzu, a sprig of herb. Muted natural colors, "
     "calm composition, lots of negative space. " + LANDSCAPE),
]


def extract_image_bytes(response):
    if not response.candidates:
        return None
    for part in response.candidates[0].content.parts:
        if hasattr(part, "inline_data") and part.inline_data:
            return part.inline_data.data
    return None


def gen_one(name, prompt):
    out_path = IMG_DIR / f"{name}.png"
    if out_path.exists():
        print(f"  skip (exists): {name}.png")
        return True
    try:
        resp = client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=prompt,
        )
        img_bytes = extract_image_bytes(resp)
        if not img_bytes:
            print(f"  x {name}: no image data")
            return False
        out_path.write_bytes(img_bytes)
        print(f"  ok {name}.png ({len(img_bytes)//1024} KB)")
        return True
    except Exception as e:
        print(f"  x {name}: {type(e).__name__}: {e}")
        return False


def main():
    print(f"生成中... ({len(IMAGES)} 枚)")
    ok = 0
    for name, prompt in IMAGES:
        if gen_one(name, prompt):
            ok += 1
        time.sleep(1)
    print(f"\n完了: {ok}/{len(IMAGES)}")


if __name__ == "__main__":
    main()
