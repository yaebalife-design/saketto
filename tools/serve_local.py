# -*- coding: utf-8 -*-
"""ローカル確認用サーバ（Cloudflare Pages と同じURL解決をする）

Cloudflare Pages は拡張子なしのURL `/brand/haccoba-0` で `brand/haccoba-0.html` を
返し、`.html` 付きでアクセスすると拡張子なしへ308でリダイレクトする。
python -m http.server は逆の挙動（.html だけ200）なので、そのままでは
本番と同じ状態を確認できない。このサーバは本番の挙動を再現する。

    cd ツール/saketto_repo && python tools/serve_local.py [ポート]
"""
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class PagesHandler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def do_GET(self):
        if self._redirect_html():
            return
        super().do_GET()

    def do_HEAD(self):
        if self._redirect_html():
            return
        super().do_HEAD()

    def _redirect_html(self):
        """/x.html → /x へ308（本番と同じ）。"""
        path = urlparse(self.path).path
        if path.endswith(".html") and not path.endswith("/index.html"):
            new = path[: -len(".html")]
            q = urlparse(self.path).query
            self.send_response(308)
            self.send_header("Location", new + (("?" + q) if q else ""))
            self.end_headers()
            return True
        return False

    def translate_path(self, path):
        """拡張子なしのURLを .html / index.html へ解決する。"""
        p = unquote(urlparse(path).path)
        local = os.path.normpath(os.path.join(ROOT, p.lstrip("/")))
        if os.path.isdir(local):
            idx = os.path.join(local, "index.html")
            if os.path.exists(idx):
                return idx
        if not os.path.exists(local):
            cand = local + ".html"
            if os.path.exists(cand):
                return cand
        return local

    def end_headers(self):
        # 本番の _headers に合わせた最低限のキャッシュ指定
        if self.path.startswith("/assets/images/"):
            self.send_header("Cache-Control", "public, max-age=604800")
        elif self.path.startswith("/assets/"):
            self.send_header("Cache-Control", "public, max-age=86400")
        else:
            self.send_header("Cache-Control", "public, max-age=3600, must-revalidate")
        super().end_headers()

    def log_message(self, fmt, *args):
        sys.stderr.write("%s %s\n" % (self.address_string(), fmt % args))


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    print(f"saketto local server (Cloudflare Pages 互換) → http://127.0.0.1:{port}/")
    ThreadingHTTPServer(("127.0.0.1", port), PagesHandler).serve_forever()
