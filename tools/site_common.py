# -*- coding: utf-8 -*-
"""saketto 全ページ共通の <head> パーツ（GA タグ・年齢ゲート）。
各 gen_*.py がここを import して head に差し込む。手書きの index.html は
このファイルの定義に合わせて手で揃える（GA_ID を変えたら両方直すこと）。
"""

# GA4 測定ID。社長から本番IDを受領したらここを差し替えて全ページ再生成する。
# 内部トラフィック（自分のアクセス）の除外は GIN-DB と同様に GA 管理画面側で行う：
#   管理 → データストリーム → タグ設定 → 内部トラフィックの定義（自宅IPを登録）
#   → 管理 → データフィルタ → 「Internal Traffic」を有効化
# コード側は標準 gtag のままでよい（IP除外はサーバー/管理画面側で完結）。
GA_ID = "G-REYY1OPEK2"


def analytics_head():
    """GA4 gtag.js ブロック。絶対URLなのでページ階層に依存しない。"""
    return (
        "<!-- Google tag (gtag.js) -->\n"
        f'<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>\n'
        "<script>\n"
        "  window.dataLayer = window.dataLayer || [];\n"
        "  function gtag(){dataLayer.push(arguments);}\n"
        "  gtag('js', new Date());\n"
        f"  gtag('config', '{GA_ID}');\n"
        "</script>"
    )


def age_gate_tag(prefix="../"):
    """年齢ゲート読み込み。prefix はリポジトリルートからの相対（サブディレクトリは "../"、ルートは ""）。"""
    return f'<script src="{prefix}assets/age-gate.js" defer></script>'


def head_extra(prefix="../"):
    """head 末尾（</head> 直前）に入れる共通ブロック。"""
    return analytics_head() + "\n" + age_gate_tag(prefix)
