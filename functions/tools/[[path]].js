// 2026-10-22 セキュリティ点検: Pages がリポジトリ直下をそのまま配信するため、
// サイト生成用の tools/（Pythonスクリプト・JSON）が誰でも読めていた。
// Functions は静的ファイルより先に動くので、/tools/ 以下は全部 404 にする。
export function onRequest() {
  return new Response("Not Found", { status: 404, headers: { "content-type": "text/plain; charset=utf-8" } });
}
