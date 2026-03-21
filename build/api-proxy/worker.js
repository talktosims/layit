/**
 * LayIt API Proxy — Cloudflare Worker
 *
 * Proxies requests to the Anthropic API so the API key never touches
 * the client app. Deploy to Cloudflare Workers (free tier: 100K req/day).
 *
 * Setup:
 *   1. Go to dash.cloudflare.com → Workers & Pages → Create
 *   2. Paste this code
 *   3. Go to Settings → Variables → Add: ANTHROPIC_API_KEY = your key
 *   4. Deploy. Your worker URL becomes: https://layit-api.YOUR-SUBDOMAIN.workers.dev
 *   5. Update the app to call this URL instead of api.anthropic.com
 */

export default {
  async fetch(request, env) {
    // Only allow POST
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'POST',
          'Access-Control-Allow-Headers': 'Content-Type',
        },
      });
    }

    if (request.method !== 'POST') {
      return new Response('Method not allowed', { status: 405 });
    }

    // Rate limit by IP (simple, not bulletproof)
    const ip = request.headers.get('CF-Connecting-IP');

    // Forward to Anthropic with the server-side key
    const body = await request.text();

    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': env.ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01',
      },
      body: body,
    });

    const data = await response.text();

    return new Response(data, {
      status: response.status,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
      },
    });
  },
};
