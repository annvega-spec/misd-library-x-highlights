#!/usr/bin/env python3
"""Fetch latest X posts for MISD libraries using official API v2. Requires X_BEARER_TOKEN."""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIBS = ROOT / "libraries-x.json"
OUT = ROOT / "posts.json"
CACHE = ROOT / ".cache-user-ids.json"
APIS = ("https://api.x.com/2", "https://api.twitter.com/2")


def http_get(url: str, token: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": "Bearer " + token,
            "User-Agent": "MISD-Library-X-Highlights/1.0",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError("HTTP %s for %s: %s" % (e.code, url, body[:500])) from e


def lookup_user_id(handle: str, token: str, cache: dict):
    key = handle.lower()
    if key in cache:
        return cache[key]
    q = urllib.parse.quote(handle)
    last = None
    for base in APIS:
        try:
            data = http_get(
                "%s/users/by/username/%s?user.fields=profile_image_url,name,username" % (base, q),
                token,
            )
            uid = (data.get("data") or {}).get("id")
            if uid:
                cache[key] = uid
                return uid
        except Exception as ex:
            last = ex
    print("WARN: could not resolve @%s: %s" % (handle, last), file=sys.stderr)
    return None


def media_urls_from_response(tweet: dict, includes: dict) -> list:
    """Collect photo/video preview URLs for a tweet from expansions."""
    media_by_key = {}
    for m in (includes or {}).get("media") or []:
        key = m.get("media_key")
        if key:
            media_by_key[key] = m
    urls = []
    keys = ((tweet.get("attachments") or {}).get("media_keys")) or []
    for key in keys:
        m = media_by_key.get(key) or {}
        mtype = m.get("type")
        if mtype == "photo":
            u = m.get("url") or m.get("preview_image_url")
            if u:
                urls.append(u)
        elif mtype in ("video", "animated_gif"):
            u = m.get("preview_image_url") or m.get("url")
            if u:
                urls.append(u)
    return urls


def latest_tweet(user_id: str, token: str):
    params = urllib.parse.urlencode(
        {
            "max_results": "5",
            "exclude": "replies,retweets",
            "tweet.fields": "created_at,text,public_metrics,attachments,entities",
            "expansions": "attachments.media_keys",
            "media.fields": "url,preview_image_url,type,width,height,alt_text",
        }
    )
    params2 = urllib.parse.urlencode(
        {
            "max_results": "5",
            "tweet.fields": "created_at,text,public_metrics,attachments,entities",
            "expansions": "attachments.media_keys",
            "media.fields": "url,preview_image_url,type,width,height,alt_text",
        }
    )
    last = None
    for params_s in (params, params2):
        for base in APIS:
            try:
                data = http_get("%s/users/%s/tweets?%s" % (base, user_id, params_s), token)
                rows = data.get("data") or []
                if not rows:
                    continue
                # Prefer a tweet that has media when available in the batch
                includes = data.get("includes") or {}
                chosen = rows[0]
                for t in rows:
                    if ((t.get("attachments") or {}).get("media_keys")):
                        chosen = t
                        break
                return {
                    "id": chosen.get("id"),
                    "text": chosen.get("text"),
                    "created_at": chosen.get("created_at"),
                    "url": "https://x.com/i/web/status/%s" % chosen.get("id"),
                    "media": media_urls_from_response(chosen, includes),
                }
            except Exception as ex:
                last = ex
                continue
    print("WARN: tweets for %s failed: %s" % (user_id, last), file=sys.stderr)
    return None


def main() -> int:
    token = os.environ.get("X_BEARER_TOKEN") or os.environ.get("TWITTER_BEARER_TOKEN")
    if not token:
        print("ERROR: set X_BEARER_TOKEN", file=sys.stderr)
        return 1

    libs = json.loads(LIBS.read_text())["libraries"]
    cache = {}
    if CACHE.exists():
        try:
            cache = json.loads(CACHE.read_text())
        except Exception:
            cache = {}

    posts = []
    for lib in libs:
        handle = lib["handle"]
        uid = lookup_user_id(handle, token, cache)
        time.sleep(0.4)
        item = {
            "name": lib["name"],
            "handle": handle,
            "library_id": lib.get("id"),
            "profile_url": "https://x.com/%s" % handle,
            "post": None,
            "error": None,
        }
        if not uid:
            item["error"] = "user_not_found"
        else:
            tw = latest_tweet(uid, token)
            time.sleep(0.4)
            if tw:
                item["post"] = tw
            else:
                item["error"] = "no_recent_posts"
        posts.append(item)
        print("@%s: %s" % (handle, "OK" if item["post"] else item["error"]))

    CACHE.write_text(json.dumps(cache, indent=2) + "\n")
    payload = {
        "updated": datetime.now(timezone.utc).isoformat(),
        "source": "x-api-v2",
        "posts": posts,
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print("Wrote %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
