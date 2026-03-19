#!/usr/bin/env node
/**
 * Upload tile presets to Firebase using REST API (no service account needed)
 *
 * Uses Firebase Realtime Database REST API with anonymous auth.
 * This matches the same auth pattern the LayIt app uses.
 *
 * Usage:
 *   node upload-rest.js output/master_presets.json
 *   node upload-rest.js output/master_presets.json --force    (overwrite existing)
 *   node upload-rest.js output/master_presets.json --dry-run  (preview only)
 */

import { readFileSync } from 'fs';
import { resolve } from 'path';

const DB_URL = 'https://paint-calc-sync-default-rtdb.firebaseio.com';
const FIREBASE_API_KEY = 'AIzaSyD9zQQgRApSqfeBougnIUVEAYupp8i-bgY';

async function signInAnonymous() {
  // Firebase anonymous sign-in via REST API
  const resp = await fetch(
    `https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=${FIREBASE_API_KEY}`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ returnSecureToken: true })
    }
  );
  if (!resp.ok) {
    console.log('Anonymous auth not required for this database, proceeding without auth');
    return null;
  }
  const data = await resp.json();
  return data.idToken;
}

async function checkExists(barcode, token) {
  const url = `${DB_URL}/tiledb/${barcode}.json${token ? `?auth=${token}` : ''}`;
  const resp = await fetch(url);
  const data = await resp.json();
  // Firebase returns {error: "Permission denied"} for unauthorized reads
  if (data && data.error) return false; // Can't tell, assume doesn't exist
  return data !== null;
}

async function uploadPreset(barcode, entry, token) {
  const url = `${DB_URL}/tiledb/${barcode}.json${token ? `?auth=${token}` : ''}`;
  const resp = await fetch(url, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(entry)
  });
  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(`Upload failed for ${barcode}: ${resp.status} ${text}`);
  }
  return await resp.json();
}

async function main() {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.log('Usage: node upload-rest.js <preset-file.json> [--force] [--dry-run]');
    process.exit(0);
  }

  const filepath = resolve(args[0]);
  const force = args.includes('--force');
  const dryRun = args.includes('--dry-run');

  console.log(`\nLayIt Tile Database Uploader (REST API)`);
  console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
  console.log(`Input:  ${filepath}`);
  console.log(`Mode:   ${dryRun ? 'DRY RUN (no writes)' : force ? 'FORCE (overwrite)' : 'Normal (skip existing)'}`);
  console.log('');

  const raw = readFileSync(filepath, 'utf-8');
  const data = JSON.parse(raw);

  // Filter out meta keys and comment keys
  const presets = {};
  for (const [key, val] of Object.entries(data)) {
    if (key.startsWith('_')) continue; // Skip _meta, _comment_*, etc.
    if (typeof val !== 'object' || val === null) continue;
    presets[key] = val;
  }

  const total = Object.keys(presets).length;
  console.log(`Found ${total} presets to upload.\n`);

  // Try anonymous auth
  let token = null;
  try {
    token = await signInAnonymous();
    if (token) console.log('Authenticated anonymously.\n');
  } catch (e) {
    console.log('Proceeding without authentication.\n');
  }

  let uploaded = 0, skipped = 0, failed = 0;

  for (const [barcode, entry] of Object.entries(presets)) {
    try {
      // Check if exists
      if (!force) {
        const exists = await checkExists(barcode, token);
        if (exists) {
          console.log(`  ⏭  ${barcode}: exists, skipping`);
          skipped++;
          continue;
        }
      }

      // Add metadata
      const enrichedEntry = {
        ...entry,
        addedAt: new Date().toISOString(),
        status: 'live'
      };

      if (dryRun) {
        console.log(`  📝 ${barcode}: would upload — ${entry.name || 'unnamed'}`);
        uploaded++;
      } else {
        await uploadPreset(barcode, enrichedEntry, token);
        console.log(`  ✓  ${barcode}: uploaded — ${entry.name || 'unnamed'}`);
        uploaded++;
      }

      // Rate limit
      if (!dryRun) await new Promise(r => setTimeout(r, 100));
    } catch (err) {
      console.log(`  ✗  ${barcode}: FAILED — ${err.message}`);
      failed++;
    }
  }

  console.log(`\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
  console.log(`Uploaded: ${uploaded}  |  Skipped: ${skipped}  |  Failed: ${failed}  |  Total: ${total}`);
  if (dryRun) console.log('(DRY RUN — no changes made)');
  console.log('');
}

main();
