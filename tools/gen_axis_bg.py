# -*- coding: utf-8 -*-
"""saketto / 5軸カードの背景画像生成

社長指示: 各軸カードに（ヒーローのように）薄い背景を敷きたい
薄く敷く前提なので、余白・光が多く抽象的な素材イメージにする。

CLAUDE.md: Vertex AI経由 / gemini-3-pro-image-preview / location=global / 蔵固有画像NG
実行: cd ツール/saketto_repo/tools && python gen_axis_bg.py
出力: saketto_repo/assets/images/axis_*.png
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
    print("ERROR: GOOGLE_CLOUD_PROJECT 未設定")
    sys.exit(1)

from google import genai
client = genai.Client(vertexai=True, project=project, location="global")

STYLE = ("Editorial magazine still-life photography. Warm cream paper background "
         "(color #F5F0E7), sumi ink black accents, subtle rust red (#B33A2A) highlights, "
         "wood brown (#8B7355) shadows. Soft diffused natural light. "
         "Very generous negative space and bright empty areas (this image will be shown "
         "faded behind text, so keep it airy and low-contrast). Minimal Japanese aesthetic. "
         "Vertical portrait 3:4 orientation. No text, no logos, no signage, no brand marks.")

IMAGES = [
    ("axis_sub",
     "A soft, airy overhead arrangement of craft sake side-ingredients on cream washi paper — "
     "a couple of green hop cones, a slice of yellow yuzu, a few scattered tea leaves and "
     "golden rice grains, placed sparsely with lots of empty space. " + STYLE),

    ("axis_kura",
     "A quiet sake brewery atmosphere — a wooden brewing paddle resting beside a cedar wooden "
     "tub, soft window light, artisanal and calm. No building exterior, no people. "
     "Lots of empty cream space. " + STYLE),

    ("axis_region",
     "A faint, atmospheric Japanese countryside — misty terraced rice fields and soft distant "
     "mountains in muted warm tones, with a large bright misty sky as negative space. " + STYLE),

    ("axis_genre",
     "A calm sparse row of diverse Japanese drinking vessels — a clear glass, a small ceramic "
     "cup, a tiny flask — different styles arranged with wide spacing on a cream surface, "
     "soft light. " + STYLE),

    ("axis_avail",
     "A few craft sake bottles softly arranged on a cream-toned shelf, one loosely wrapped in "
     "pale paper, soft light, minimal and quiet, with lots of empty space. " + STYLE),
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
