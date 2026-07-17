/**
 * LayIt AI proxy
 *
 * Keeps the Anthropic key server-side and deliberately exposes only LayIt's
 * image-analysis tasks. This is not a replacement for App Attest, but it
 * prevents the Worker from acting as an arbitrary public Anthropic proxy.
 */

const ALLOWED_ORIGINS = new Set([
  'https://layit.pages.dev',
]);
const LOOPBACK_ORIGIN = /^http:\/\/localhost:(8787|8788|8789|8790)$/;
const ALLOWED_TASKS = new Set(['label-scan', 'label-vision', 'pattern-classify']);
const MAX_BODY_CHARS = 2_500_000;
const MAX_IMAGE_CHARS = 2_200_000;
const RATE_WINDOW_MS = 10 * 60 * 1000;
const RATE_LIMIT = 30;
const recentRequests = new Map();

const LABEL_PROMPT = `Read this tile product box label and return ONLY valid JSON with these fields:
name, brand, shape, nomW, nomH, actW, actH, grout, material, piecesPerBox,
coverageSqFt, barcode, subShape, subW, subH, subGr.

Use inches for every dimension. Width is the shorter side and height is the
longer side. Convert cm and mm to inches. shape must be square, rectangle,
hexagon, herringbone, or mosaic. For a mosaic, nomW/nomH are sheet dimensions
and subShape/subW/subH/subGr describe the individual pieces. If actual size is
missing, use nominal size minus the grout joint. Use null when a value cannot
be read. Do not invent label text. Return JSON only, with no markdown.`;

const PATTERN_PROMPT = `Analyze this tile or tile-pattern photo and return ONLY valid JSON with:
pattern_id, pattern_name, wallpaper_group, category, tile_shape_description,
has_filler_pieces, filler_description, estimated_coverage, spacing, confidence.

Choose pattern_id from hex, penny, fishscale, square, diamond, rectangle,
arabesque, ogee, starcross, octdot, rhombus, triangle, quatrefoil, kite, leaf,
dragonscale, capsule, picket, chevron, basketweave, pinwheel, herringbone when
possible. category must be regular, geometric, curvilinear, or organic.
spacing must contain numeric colFactor, rowFactor, oddRowOffsetX and boolean
flipOddRows. confidence and estimated_coverage must be between 0 and 1.
Return JSON only, with no markdown.`;

function corsHeaders(origin) {
  return {
    'Access-Control-Allow-Origin': origin,
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, X-LayIt-AI-Task, X-LayIt-AI-Profile',
    'Access-Control-Max-Age': '86400',
    'Vary': 'Origin',
  };
}

function jsonResponse(origin, status, payload, extraHeaders = {}) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'Cache-Control': 'no-store',
      'X-Content-Type-Options': 'nosniff',
      ...corsHeaders(origin),
      ...extraHeaders,
    },
  });
}

function isAllowedOrigin(origin) {
  return ALLOWED_ORIGINS.has(origin) || LOOPBACK_ORIGIN.test(origin);
}

function enforceRateLimit(key) {
  const now = Date.now();
  const cutoff = now - RATE_WINDOW_MS;
  const prior = (recentRequests.get(key) || []).filter((timestamp) => timestamp > cutoff);
  if (prior.length >= RATE_LIMIT) {
    recentRequests.set(key, prior);
    return false;
  }
  prior.push(now);
  recentRequests.set(key, prior);

  // Bound per-isolate memory. Cloudflare may run multiple isolates, so this is
  // intentionally a best-effort abuse brake rather than a billing guarantee.
  if (recentRequests.size > 2000) {
    for (const [entryKey, timestamps] of recentRequests) {
      if (!timestamps.some((timestamp) => timestamp > cutoff)) recentRequests.delete(entryKey);
    }
  }
  return true;
}

function validateAndBuildRequest(body, task) {
  if (!body || typeof body !== 'object' || !Array.isArray(body.messages) || body.messages.length !== 1) {
    throw new Error('Invalid request shape');
  }
  const message = body.messages[0];
  if (message.role !== 'user' || !Array.isArray(message.content)) {
    throw new Error('Invalid message');
  }

  const image = message.content.find((item) => item && item.type === 'image');
  const source = image && image.source;
  if (!source || source.type !== 'base64' || source.media_type !== 'image/jpeg') {
    throw new Error('A JPEG image is required');
  }
  if (typeof source.data !== 'string' || source.data.length < 32 || source.data.length > MAX_IMAGE_CHARS) {
    throw new Error('Image is empty or too large');
  }
  if (!/^[A-Za-z0-9+/]+={0,2}$/.test(source.data)) {
    throw new Error('Image data is not valid base64');
  }

  const isPattern = task === 'pattern-classify';
  return {
    model: 'claude-sonnet-4-6',
    max_tokens: isPattern ? 900 : 800,
    messages: [{
      role: 'user',
      content: [
        { type: 'image', source: { type: 'base64', media_type: 'image/jpeg', data: source.data } },
        { type: 'text', text: isPattern ? PATTERN_PROMPT : LABEL_PROMPT },
      ],
    }],
  };
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin') || '';
    if (!isAllowedOrigin(origin)) {
      return new Response('Forbidden origin', { status: 403, headers: { 'Cache-Control': 'no-store' } });
    }

    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: corsHeaders(origin) });
    }
    if (request.method !== 'POST') {
      return jsonResponse(origin, 405, { error: { message: 'Method not allowed' } }, { Allow: 'POST, OPTIONS' });
    }
    if (!env.ANTHROPIC_API_KEY) {
      return jsonResponse(origin, 503, { error: { message: 'AI scanning is temporarily unavailable' } });
    }

    const task = request.headers.get('X-LayIt-AI-Task') || '';
    if (!ALLOWED_TASKS.has(task)) {
      return jsonResponse(origin, 400, { error: { message: 'Unsupported AI task' } });
    }

    const contentLength = Number(request.headers.get('Content-Length') || 0);
    if (contentLength > MAX_BODY_CHARS) {
      return jsonResponse(origin, 413, { error: { message: 'Image is too large' } });
    }

    const clientKey = request.headers.get('CF-Connecting-IP') || 'unknown';
    if (!enforceRateLimit(clientKey)) {
      return jsonResponse(
        origin,
        429,
        { error: { message: 'Too many scans. Please try again in a few minutes.' } },
        { 'Retry-After': '600' },
      );
    }

    let upstreamBody;
    try {
      const rawBody = await request.text();
      if (rawBody.length > MAX_BODY_CHARS) throw new Error('Request is too large');
      upstreamBody = validateAndBuildRequest(JSON.parse(rawBody), task);
    } catch (error) {
      return jsonResponse(origin, 400, { error: { message: error.message || 'Invalid request' } });
    }

    try {
      const response = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': env.ANTHROPIC_API_KEY,
          'anthropic-version': '2023-06-01',
        },
        body: JSON.stringify(upstreamBody),
        signal: AbortSignal.timeout(45_000),
      });
      const data = await response.text();
      return new Response(data, {
        status: response.status,
        headers: {
          'Content-Type': 'application/json; charset=utf-8',
          'Cache-Control': 'no-store',
          'X-Content-Type-Options': 'nosniff',
          ...corsHeaders(origin),
        },
      });
    } catch (error) {
      return jsonResponse(origin, 502, { error: { message: 'AI service did not respond. Please try again.' } });
    }
  },
};
