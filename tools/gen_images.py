# -*- coding: utf-8 -*-
"""saketto / Vertex AI 画像生成スクリプト

CLAUDE.md ルール（親100_クロードコード経営/CLAUDE.md）：
- 必ずVertex AI経由（クレカ直課金禁止）
- gemini-3-pro-image-preview を使用
- 蔵固有の画像は生成しない（地域風景・素材イメージのみ）

実行: cd ツール/saketto_repo/tools && python gen_images.py
出力: saketto_repo/assets/images/*.png
"""

import os
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent  # saketto_repo/
IMG_DIR = REPO_ROOT / "assets" / "images"
IMG_DIR.mkdir(parents=True, exist_ok=True)


# Vertex AI 必須
project = os.environ.get("GOOGLE_CLOUD_PROJECT")
if not project:
    print("ERROR: GOOGLE_CLOUD_PROJECT 環境変数が未設定")
    print("       set GOOGLE_CLOUD_PROJECT=project-8a27859f-c39d-4d42-8c4")
    sys.exit(1)

from google import genai
client = genai.Client(vertexai=True, project=project, location="global")


# 共通スタイル（saketto世界観：warm cream × sumi × 朱）
STYLE = ("Editorial magazine still-life photography. Warm cream paper background "
         "(color #F5F0E7), sumi ink black accents, subtle rust red (#B33A2A) highlights, "
         "wood brown (#8B7355) shadows. Soft diffused natural window light from upper left. "
         "Generous negative space, minimal Japanese aesthetic, magazine quality. "
         "No text, no logos, no signage, no specific brewery or brand marks.")

LANDSCAPE = STYLE + " Landscape orientation 16:9."
SQUARE = STYLE + " Square composition 1:1."


IMAGES = [

    # ─── ランディングのヒーロー ───
    ("hero",
     "An elegant editorial still-life: golden Japanese rice grains spilled across "
     "warm cream-colored handmade washi paper, with delicate white koji mold (kome-koji) "
     "culture visible nearby. Hints of fermentation — a single bubble or two of clear "
     "moromi liquid. " + LANDSCAPE),

    # ─── 副原料カテゴリ（5枚） ───
    ("sub_hop",
     "Editorial flat-lay: fresh green hop flower cones (humulus lupulus) arranged on "
     "warm cream handmade washi paper. A small sumi calligraphy brush nearby for accent. " + SQUARE),

    ("sub_fruit",
     "Editorial flat-lay: mixed Japanese fruits — small Japanese pears (nashi), yellow yuzu "
     "citrus, dark red apple, small dark grapes — arranged on warm cream washi paper with "
     "muted natural colors. " + SQUARE),

    ("sub_tea_herb",
     "Editorial flat-lay: Japanese tea elements — a small mound of bright green matcha powder, "
     "dried jasmine tea flowers, small clusters of sansho pepper berries, kuromoji leaves — "
     "arranged on cream washi paper. " + SQUARE),

    ("sub_rice",
     "Editorial still-life: a single beautiful golden ear of rice paddy (kome) laid on warm "
     "cream washi paper, with delicate white koji mold spores visible at the base. Soft side "
     "lighting emphasizing the texture of the grain. " + SQUARE),

    ("sub_special",
     "Editorial flat-lay: Japanese specialty ingredients — a small white ceramic dish of "
     "amber agave syrup, a glass jar of golden honey, a tiny black ceramic bowl of dark miso "
     "paste — arranged elegantly on warm cream washi paper. " + SQUARE),

    # ─── 地域カバー（6枚） ───
    ("region_tohoku",
     "Atmospheric landscape of a remote snowy mountain village in northeastern Japan "
     "(Tohoku region) in soft golden hour light. Distant snow-covered peaks, bare winter "
     "trees, a single thatched roof in the far distance. No people. " + LANDSCAPE),

    ("region_kanto",
     "Atmospheric editorial shot of a quiet alley in old Tokyo (Kanto region) at warm dawn. "
     "Soft mist, traditional wooden lattice doors, paper lanterns barely lit. No people, "
     "no readable signage. " + LANDSCAPE),

    ("region_chubu",
     "Atmospheric landscape of quiet Japanese mountain village rice terraces (tanada) in "
     "Chubu region, in soft morning light. Mist hanging over emerald paddies. No people. " + LANDSCAPE),

    ("region_kansai",
     "Atmospheric editorial detail of traditional Kyoto (Kansai region) wooden machiya "
     "architecture — shoji screen, weathered wooden post, hanging noren cloth — in warm "
     "morning light. No people, no readable signage. " + LANDSCAPE),

    ("region_kyushu",
     "Atmospheric coastal Kyushu landscape — quiet harbor at dawn, rocky shore, distant "
     "mountains, traditional wooden fishing boat in the distance. No people. " + LANDSCAPE),

    ("region_okinawa",
     "Atmospheric subtropical Okinawan coast at gentle dawn — coral sand, gentle waves, "
     "distant palm tree silhouettes. Warm cream tones with hints of turquoise. No people. " + LANDSCAPE),

]


def extract_image_bytes(response):
    """Vertex AI 応答から画像バイトを抽出"""
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
            print(f"  ✗ {name}: no image data in response")
            return False
        out_path.write_bytes(img_bytes)
        print(f"  ✓ {name}.png ({len(img_bytes)//1024} KB)")
        return True
    except Exception as e:
        print(f"  ✗ {name}: {type(e).__name__}: {e}")
        return False


def main():
    print(f"生成中... ({len(IMAGES)} 枚)")
    ok = 0
    for name, prompt in IMAGES:
        if gen_one(name, prompt):
            ok += 1
        time.sleep(1)  # rate limit保険
    print(f"\n✓ 完了: {ok}/{len(IMAGES)}")


if __name__ == "__main__":
    main()
