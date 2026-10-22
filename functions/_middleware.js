// 2026-10-22 セキュリティ点検: Pages がリポジトリ直下をそのまま配信するため、
// サイト生成用の tools/（Pythonスクリプト・JSON）が誰でも読めていた。
// /tools/ だけを関数で塞ぐと %74ools のような %表記で素通りされる（静的配信側はデコードしてから探す）ので、
// デコードしたパスで判定する。それ以外はそのまま静的ファイル・既存の関数へ渡す。
export async function onRequest({ request, next }) {
  let path;
  try {
    path = decodeURIComponent(new URL(request.url).pathname);
  } catch (e) {
    return new Response("Bad Request", { status: 400 });
  }
  const p = path.split("\\").join("/").replace(/\/{2,}/g, "/").toLowerCase();
  if (p === "/tools" || p.startsWith("/tools/")) {
    return new Response("Not Found", { status: 404, headers: { "content-type": "text/plain; charset=utf-8" } });
  }
  return next();
}
