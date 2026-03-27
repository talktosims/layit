/**
 * Upload validated tile presets to Firebase Realtime Database
 *
 * Usage:
 *   node upload.js output/all_presets.json
 *   node upload.js output/012345678901.json
 *
 * This writes to the tiledb path in Firebase,
 * separate from the paint-calc app data.
 */

import { initializeApp } from 'firebase-admin/app';
import { getDatabase } from 'firebase-admin/database';
import { readFileSync } from 'fs';

// Firebase config — same project as paint-calc but using layit/ namespace
const app = initializeApp({
  databaseURL: 'https://paint-calc-sync-default-rtdb.firebaseio.com'
});

const db = getDatabase(app);

async function uploadPresets(filepath) {
  console.log(`Reading: ${filepath}`);
  const raw = readFileSync(filepath, 'utf-8');
  const data = JSON.parse(raw);

  // Determine format: single result or combined presets
  let presets = {};

  if (data.formatted) {
    // Single scrape result
    if (!data.formatted.barcode) {
      console.error('No barcode in this result, skipping');
      return;
    }
    presets[data.formatted.barcode] = data.formatted.entry;
  } else {
    // Combined presets (barcode → entry map)
    presets = data;
  }

  const count = Object.keys(presets).length;
  console.log(`Uploading ${count} preset(s) to tiledb...`);

  // Write each preset individually so we don't overwrite existing entries
  for (const [barcode, entry] of Object.entries(presets)) {
    const ref = db.ref(`tiledb/${barcode}`);

    // Check if already exists
    const existing = await ref.get();
    if (existing.exists()) {
      console.log(`  ${barcode}: already exists, skipping (use --force to overwrite)`);
      continue;
    }

    // Add metadata
    entry.addedAt = new Date().toISOString();
    entry.status = 'live'; // Pre-validated entries go straight to live

    await ref.set(entry);
    console.log(`  ${barcode}: uploaded ✓ (${entry.name})`);
  }

  console.log('\nDone!');
  process.exit(0);
}

const args = process.argv.slice(2);

if (args.length === 0) {
  console.log('Usage: node upload.js <preset-file.json>');
  console.log('');
  console.log('Uploads validated tile presets to Firebase tiledb');
  process.exit(0);
}

uploadPresets(args[0]);
