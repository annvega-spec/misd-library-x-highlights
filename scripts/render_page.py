#!/usr/bin/env python3
"""Render Black & Gold X highlights page from posts.json (static, Thrillshare-safe)."""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / "posts.json"
LIBS = ROOT / "libraries-x.json"
OUT = ROOT / "index.html"


def esc(s):
    return html.escape(str(s or ""), quote=True)


def main():
    libs = json.loads(LIBS.read_text())["libraries"]
    data = {"updated": None, "posts": []}
    if POSTS.exists():
        try:
            data = json.loads(POSTS.read_text())
        except Exception:
            pass
    by_handle = {p["handle"].lower(): p for p in (data.get("posts") or []) if p.get("handle")}

    cards = []
    for lib in libs:
        h = lib["handle"]
        row = by_handle.get(h.lower()) or {}
        post = row.get("post") or {}
        profile = "https://x.com/%s" % h
        if post.get("text") or post.get("media"):
            created = (post.get("created_at") or "")[:16].replace("T", " ")
            media_html = ""
            for i, mu in enumerate((post.get("media") or [])[:2]):
                media_html += (
                    '<div class="tweet-media"><img src="%s" alt="Post image %s" loading="lazy" /></div>'
                    % (esc(mu), i + 1)
                )
            body = (
                '%s'
                '<p class="tweet-text">%s</p>'
                '<div class="tweet-meta">%s UTC</div>'
                '<a class="btn" href="%s" target="_blank" rel="noopener noreferrer">View on X</a>'
            ) % (
                media_html,
                esc(post.get("text") or ""),
                esc(created),
                esc(post.get("url") or profile),
            )
        else:
            err = row.get("error") or "awaiting_api"
            if not data.get("updated") or err == "awaiting_api":
                note = "Connect X API to load latest posts."
            else:
                note = "No recent posts found."
            body = (
                '<p class="tweet-text muted">%s</p>'
                '<a class="btn" href="%s" target="_blank" rel="noopener noreferrer">Open @%s on X</a>'
            ) % (esc(note), esc(profile), esc(h))

        cards.append(
            (
                '<article class="x-card">'
                '<div class="x-card-head">'
                "<h2>%s</h2>"
                '<a class="handle" href="%s" target="_blank" rel="noopener noreferrer">@%s</a>'
                "</div>"
                '<div class="x-card-body">%s</div>'
                "</article>"
            )
            % (esc(lib["name"]), esc(profile), esc(h), body)
        )

    updated = data.get("updated") or "—"
    n = len(libs)
    page = """<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <meta http-equiv=\"refresh\" content=\"1800\" />
  <meta name=\"color-scheme\" content=\"dark\" />
  <title>McAllen ISD · Library X Highlights</title>
  <style>
    :root { --black:#0a0a0a; --gold:#FFC000; --card:#161616; --border:rgba(255,192,0,.4); --muted:#c8c8c8; --font:\"Segoe UI\",system-ui,-apple-system,Roboto,Arial,sans-serif; }
    * { box-sizing:border-box; }
    body { margin:0; background:var(--black); color:#fff; font-family:var(--font); }
    a { color:var(--gold); text-decoration:none; }
    a:hover { text-decoration:underline; }
    .x-header { text-align:center; padding:18px 12px 14px; background:linear-gradient(180deg,#000,#111); border-bottom:3px solid var(--gold); }
    .x-badge { display:inline-flex; width:44px; height:44px; border-radius:50%; border:2px solid var(--gold); color:var(--gold); align-items:center; justify-content:center; font-weight:800; font-size:.72rem; margin-bottom:8px; }
    h1 { margin:0; font-size:1.45rem; } h1 span { color:var(--gold); }
    .tagline { margin:6px 0 0; color:#ddd; font-size:.88rem; }
    .meta { margin-top:8px; color:var(--muted); font-size:.78rem; }
    .x-wrap { max-width:1100px; margin:0 auto; padding:14px 12px 22px; }
    .x-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(260px,1fr)); gap:14px; }
    @media (min-width:900px) { .x-grid { grid-template-columns:repeat(3,1fr); } }
    @media (min-width:1100px) { .x-grid { grid-template-columns:repeat(4,1fr); } }
    .x-card { background:var(--card); border:1px solid var(--border); border-radius:12px; overflow:hidden; min-height:220px; display:flex; flex-direction:column; box-shadow:0 8px 20px rgba(0,0,0,.4); }
    .x-card-head { padding:10px 12px; border-bottom:1px solid rgba(255,192,0,.25); background:rgba(255,192,0,.06); }
    .x-card-head h2 { margin:0 0 4px; font-size:.9rem; }
    .handle { font-size:.78rem; font-weight:600; }
    .x-card-body { padding:12px; flex:1; display:flex; flex-direction:column; gap:10px; }
    .tweet-text { margin:0; font-size:.88rem; line-height:1.4; white-space:pre-wrap; }
    .tweet-text.muted { color:var(--muted); }
    .tweet-meta { font-size:.72rem; color:var(--muted); }
    .tweet-media { width:100%; border-radius:8px; overflow:hidden; background:#0d0d0d; }
    .tweet-media img { display:block; width:100%; height:auto; max-height:220px; object-fit:cover; }
    .btn { display:inline-block; align-self:flex-start; margin-top:auto; padding:8px 14px; border-radius:999px; background:var(--gold); color:#000 !important; font-weight:800; font-size:.8rem; text-decoration:none !important; }
    .x-footer { text-align:center; padding:12px; font-size:.72rem; color:#888; border-top:1px solid rgba(255,192,0,.2); }
  </style>
</head>
<body>
  <header class=\"x-header\">
    <div class=\"x-badge\">MISD</div>
    <h1>Library <span>X Highlights</span></h1>
    <p class=\"tagline\">Black &amp; Gold · Latest post from each library account</p>
    <p class=\"meta\"><strong>__N__</strong> accounts · Updated __UPDATED__ · Refreshes every 30 minutes</p>
  </header>
  <main class=\"x-wrap\"><div class=\"x-grid\">
__CARDS__
  </div></main>
  <footer class=\"x-footer\">McAllen ISD Library Services · Powered by official X API · Token never exposed in the page</footer>
</body>
</html>
""".replace("__N__", str(n)).replace("__UPDATED__", esc(updated)).replace("__CARDS__", "\n".join(cards))
    OUT.write_text(page)
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
