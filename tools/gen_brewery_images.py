# -*- coding: utf-8 -*-
"""saketto / 蔵ごとのヘッダーイメージ生成（Vertex AI）

CLAUDE.md ルール：
- 必ずVertex AI経由・gemini-3-pro-image-preview
- 蔵固有の建物・看板・ロゴは描かない（素材・土地・製法を連想させる風景/静物のみ）
- ページ側に「画像はイメージ」表記を入れる（gen_brewery_pages.py 側で対応）

シーンは各蔵の一次ソース確認済みデータ（所在地・副原料・製法）から構成。
実行: cd ツール/saketto_repo/tools && python gen_brewery_images.py
出力: saketto_repo/assets/images/brewery/{slug}.png → 別途WebP変換して参照
"""

import time
from pathlib import Path

# gen_images.py の共通スタイル・クライアントを流用（Vertex AI設定もそちらで検証済み）
from gen_images import STYLE, client, extract_image_bytes

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "assets" / "images" / "brewery"
OUT_DIR.mkdir(parents=True, exist_ok=True)

LANDSCAPE = STYLE + " Landscape orientation 16:9."

# slug → その蔵を連想させるシーン（建物・看板・人物・文字は禁止）
SCENES = {
    "ine-to-agave":
        "Golden rice ears and a single sculptural blue-green agave leaf arranged together "
        "on warm washi paper, with a distant impression of a northern sea cape light. ",
    "haccoba":
        "Fresh green hop cones entwined with golden rice ears on washi paper, "
        "evoking an old northern village craft revived. ",
    "lagoon":
        "A misty freshwater lagoon at dawn bordered by rice fields, soft morning light "
        "on still water, reeds in silhouette. ",
    "librom":
        "Bright editorial flat-lay of strawberries, tomatoes and fresh herbs with a small "
        "glass of cloudy sake, southern light. ",
    "konohanano":
        "A ceramic cup of milky-white cloudy doburoku on washi paper, sumi ink accents, "
        "quiet downtown craft atmosphere in still-life form. ",
    "happy-taro":
        "A wooden bowl of milky doburoku beside polished rice grains, lake-country "
        "atmosphere with soft water reflections in the background blur. ",
    "heiroku":
        "Northern orchard fruits — a pear, grapes and a small apple — beside golden rice "
        "sheaf on washi, layered autumn light. ",
    "pukupuku":
        "Close detail of a traditional wooden kioke fermentation barrel with hop cones "
        "and rice scattered on washi, warm wood tones. ",
    "adachi-noujo":
        "Terraced rice paddies at dusk with warm evening glow, a farm field melting into "
        "soft twilight, gentle and quiet. ",
    "nondo":
        "A misty river valley with rice fields and folktale-like fog drifting through "
        "mountains, muted northern light. ",
    "fermenteria":
        "Modern clear glass fermentation vessels with gently bubbling white moromi, "
        "clean minimal still-life, soft daylight. ",
    "yamane":
        "Green tea leaves, a honey dipper with golden honey, and sprouted brown rice "
        "arranged on washi paper, forest-edge calm. ",
    "heiwa-kabutocho":
        "A small ceramic cup of milky doburoku on dark polished stone, sumi-black "
        "minimalism with a faint warm city light bokeh. ",
    "heiwa-namba":
        "Azuki red beans and black soybeans scattered beside a glass of milky doburoku "
        "on washi, warm and convivial. ",
    "tokyo-station":
        "Seasonal fruits — mango, apple, grapes and peach — beside a small glass of "
        "milky doburoku, refined travel-gift still-life. ",
    "iyasaka":
        "Mounds of pure white koji rice on washi paper, snow-country minimalism, "
        "soft cold light with warm paper tones. ",
    "sakenova":
        "A piece of golden honeycomb, a red apple, a mikan and strawberries arranged "
        "sparsely on cream washi, playful but minimal. ",
    "linne":
        "Three small piles of grain — barley ears, dark buckwheat seeds, polished rice — "
        "in a row on washi paper, botanical-study calm. ",
    "amanosato":
        "A quiet night-sky gradient over a dim rice field, one warm lantern-like glow "
        "of light low in the frame, serene winter night mood. ",
    "nomu":
        "Green shikuwasa citrus fruits and sugarcane stalks in bright southern island "
        "light, a hint of turquoise sea in the far blur. ",
    "salmon-brewery":
        "A clear cold river current over smooth stones with autumn light, golden rice "
        "sheaf resting on washi at the water's edge. ",
    "tsuchiura":
        "Lotus leaves and reeds at the edge of a wide lake, soft overcast light, "
        "quiet water-country stillness. ",
    "hakutsuru-sakecraft":
        "A precise row of small modern tasting glasses with pale golden and cloudy "
        "sake gradients, laboratory-clean minimalism. ",
    "dejima-hosendo":
        "Soft sea waves and drifting clouds rendered like a washi-paper collage, a folded "
        "paper fan resting at the edge, harbor-town light. ",
    "cultiva":
        "Several distinct varieties of rice ears laid side by side for comparison on "
        "washi paper, coastal farmland light. ",
}


def main():
    print(f"蔵バナー生成中... ({len(SCENES)} 枚)")
    ok = 0
    for slug, scene in SCENES.items():
        out_path = OUT_DIR / f"{slug}.png"
        if out_path.exists():
            print(f"  skip (exists): {slug}.png")
            ok += 1
            continue
        try:
            resp = client.models.generate_content(
                model="gemini-3-pro-image-preview",
                contents=scene + LANDSCAPE,
            )
            img_bytes = extract_image_bytes(resp)
            if not img_bytes:
                print(f"  ✗ {slug}: no image data")
                continue
            out_path.write_bytes(img_bytes)
            print(f"  ✓ {slug}.png ({len(img_bytes)//1024} KB)")
            ok += 1
        except Exception as e:
            print(f"  ✗ {slug}: {type(e).__name__}: {e}")
        time.sleep(15)  # gemini-3-pro-image-preview の分間クォータが小さいため間隔を空ける
    print(f"\n✓ 完了: {ok}/{len(SCENES)}")


if __name__ == "__main__":
    main()
