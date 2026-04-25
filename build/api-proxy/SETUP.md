# LayIt API Proxy Setup (5 minutes)

## Why
LayIt's release build does not embed an AI API key. The app calls a Cloudflare Worker proxy, and the proxy keeps the Anthropic key on Cloudflare's servers.

## Steps

1. Go to **[dash.cloudflare.com](https://dash.cloudflare.com)**
2. Sign up (free) or log in
3. Click **Workers & Pages** → **Create** → **Create Worker**
4. Name it `layit-api`
5. Paste the contents of `worker.js` into the editor
6. Click **Deploy**
7. Go to **Settings** → **Variables and Secrets** → **Add**
   - Variable name: `ANTHROPIC_API_KEY`
   - Value: your API key (the sk-ant-api03... one)
   - Click **Encrypt** (important!)
8. Click **Save and Deploy**

Your proxy URL is now: `https://layit-api.YOUR-SUBDOMAIN.workers.dev`

## Update the app

Set `LayItAIProxyURL` in `LayIt-iOS/Info.plist` to your Worker URL:

```
<key>LayItAIProxyURL</key>
<string>https://layit-api.YOUR-SUBDOMAIN.workers.dev</string>
```

No API key is sent by the app. No `anthropic-dangerous-direct-browser-access` header is used. The proxy handles Anthropic auth server-side.

Before spending on marketing, add Cloudflare rate limiting or another abuse-control layer for this Worker because the endpoint is public.

## Cost
Cloudflare Workers free tier: 100,000 requests/day. More than enough.
