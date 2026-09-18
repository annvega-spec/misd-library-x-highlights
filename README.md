# McAllen ISD Library X Highlights

Black & Gold latest-post grid for Thrillshare.

**Live:** https://annvega-spec.github.io/misd-library-x-highlights/

## How it works
1. GitHub Action every **30 minutes**
2. Official **X API v2** with secret `X_BEARER_TOKEN` (never in the public page)
3. Writes `posts.json` and rebuilds static `index.html`

## IT setup
1. https://developer.x.com/ — create app, buy pay-per-use credits (no free timeline reads in 2026)
2. Copy **Bearer Token**
3. Repo → Settings → Secrets and variables → Actions → `X_BEARER_TOKEN`
4. Actions → **Fetch X posts** → Run workflow

## Thrillshare iframe
```html
<iframe
  src="https://annvega-spec.github.io/misd-library-x-highlights/"
  title="McAllen ISD Library X Highlights"
  width="100%"
  height="980"
  style="border:0;width:100%;min-height:800px;background:#0a0a0a;"
  loading="lazy"
></iframe>
```
