# LayIt API Proxy Setup (5 minutes)

## Why
The API key is currently hardcoded in WebAppView.swift. Anyone who decompiles the app can steal it. This proxy keeps the key on Cloudflare's servers.

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

In `index.html`, change the two fetch calls from:
```
fetch('https://api.anthropic.com/v1/messages', {
    headers: {
        'x-api-key': _AI_API_KEY,
        'anthropic-dangerous-direct-browser-access': 'true'
    ...
```

To:
```
fetch('https://layit-api.YOUR-SUBDOMAIN.workers.dev', {
    headers: {
        'Content-Type': 'application/json'
    ...
```

No API key in the request. No `anthropic-dangerous-direct-browser-access` header. The proxy handles auth server-side.

Then remove the API key from `WebAppView.swift` entirely.

## Cost
Cloudflare Workers free tier: 100,000 requests/day. More than enough.
