#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const defaultManifest = '/Users/Sims/Desktop/expandit/products/layit/manifest.json';
const manifestPath = path.resolve(process.argv[2] || defaultManifest);
const assetRootArgIndex = process.argv.indexOf('--asset-root');
const productRoot = assetRootArgIndex >= 0
  ? path.resolve(process.argv[assetRootArgIndex + 1])
  : path.dirname(manifestPath);
const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));

const accuracyRank = {
  vendor_step_verified: 5,
  datasheet_parametric: 4,
  measured_parametric: 3,
  estimated_package_model: 2,
  photo_only_placeholder: 1,
  logical_placeholder: 0,
  unknown: 0
};

function readGlbJson(filePath) {
  const buf = fs.readFileSync(filePath);
  if (buf.toString('ascii', 0, 4) !== 'glTF') {
    throw new Error(`Not a GLB file: ${filePath}`);
  }
  let offset = 12;
  while (offset < buf.length) {
    const length = buf.readUInt32LE(offset);
    const type = buf.readUInt32LE(offset + 4);
    offset += 8;
    if (type === 0x4e4f534a) {
      return JSON.parse(buf.slice(offset, offset + length).toString('utf8'));
    }
    offset += length;
  }
  throw new Error(`No JSON chunk in GLB: ${filePath}`);
}

function glbBounds(modelPath) {
  const json = readGlbJson(path.join(productRoot, modelPath));
  const min = [Infinity, Infinity, Infinity];
  const max = [-Infinity, -Infinity, -Infinity];

  for (const mesh of json.meshes || []) {
    for (const primitive of mesh.primitives || []) {
      const accessorIndex = primitive.attributes?.POSITION;
      if (accessorIndex == null) continue;
      const accessor = json.accessors?.[accessorIndex];
      if (!accessor?.min || !accessor?.max) continue;
      for (let axis = 0; axis < 3; axis++) {
        min[axis] = Math.min(min[axis], accessor.min[axis]);
        max[axis] = Math.max(max[axis], accessor.max[axis]);
      }
    }
  }

  if (!Number.isFinite(min[0]) || !Number.isFinite(max[0])) {
    throw new Error(`No POSITION bounds in GLB: ${modelPath}`);
  }

  return {
    min: min.map(v => v * 1000),
    max: max.map(v => v * 1000),
    size_mm: min.map((v, i) => (max[i] - v) * 1000)
  };
}

function componentDims(component) {
  if (component.measured_size_mm) {
    const [w, d, h] = component.measured_size_mm;
    return { w, d, h, source: 'measured_size_mm' };
  }
  if (component.primitive?.size_mm) {
    const [w, d, h] = component.primitive.size_mm;
    return { w, d, h, source: 'primitive.size_mm' };
  }
  if (component.model) {
    const bounds = glbBounds(component.model);
    const [w, d, h] = bounds.size_mm;
    return { w, d, h, source: component.model };
  }
  return { w: 0, d: 0, h: 0, source: 'unknown' };
}

function footprintBox(component, phaseId) {
  const dims = componentDims(component);
  const [x, y] = component.position_mm || [0, 0];
  const radians = (component.rotation_deg || 0) * Math.PI / 180;
  const width = Math.abs(dims.w * Math.cos(radians)) + Math.abs(dims.d * Math.sin(radians));
  const depth = Math.abs(dims.w * Math.sin(radians)) + Math.abs(dims.d * Math.cos(radians));
  return {
    ref: component.ref,
    phaseId,
    accuracy: component.model_accuracy || (component.primitive ? 'photo_only_placeholder' : 'unknown'),
    source: dims.source,
    width,
    depth,
    height: dims.h,
    x1: x - width / 2,
    x2: x + width / 2,
    y1: y - depth / 2,
    y2: y + depth / 2
  };
}

function pinIndexFor(component) {
  return new Set((component.pins || []).map(pin => `${component.ref}.${pin.id}`));
}

const components = [];
const pinIds = new Set();
for (const phase of manifest.phases || []) {
  for (const component of phase.components || []) {
    components.push({ phaseId: phase.id, component });
    for (const pinId of pinIndexFor(component)) pinIds.add(pinId);
  }
}

const boxes = components.map(({ phaseId, component }) => footprintBox(component, phaseId));
const counts = {
  components: components.length,
  primitives: components.filter(({ component }) => !!component.primitive).length,
  glbModels: components.filter(({ component }) => !!component.model).length,
  missingAccuracy: components.filter(({ component }) => !component.model_accuracy).length,
  missingSourceRefs: components.filter(({ component }) => !(component.source_refs || []).length).length
};

const byAccuracy = {};
for (const { component } of components) {
  const key = component.model_accuracy || (component.primitive ? 'photo_only_placeholder' : 'unknown');
  byAccuracy[key] = (byAccuracy[key] || 0) + 1;
}

const overlaps = [];
for (let i = 0; i < boxes.length; i++) {
  for (let j = i + 1; j < boxes.length; j++) {
    const a = boxes[i];
    const b = boxes[j];
    const overlapX = Math.min(a.x2, b.x2) - Math.max(a.x1, b.x1);
    const overlapY = Math.min(a.y2, b.y2) - Math.max(a.y1, b.y1);
    if (overlapX > 0 && overlapY > 0) {
      overlaps.push({
        a: a.ref,
        b: b.ref,
        phases: [a.phaseId, b.phaseId],
        overlap_mm: [Number(overlapX.toFixed(2)), Number(overlapY.toFixed(2))]
      });
    }
  }
}

const missingEndpoints = [];
for (const phase of manifest.phases || []) {
  for (const connection of phase.connections || []) {
    for (const endpoint of [connection.from, connection.to]) {
      if (endpoint && !pinIds.has(endpoint)) {
        missingEndpoints.push({ phase: phase.id, endpoint });
      }
    }
  }
}

const lowTrust = components
  .filter(({ component }) => accuracyRank[component.model_accuracy || 'unknown'] < accuracyRank.measured_parametric)
  .map(({ phaseId, component }) => ({
    phase: phaseId,
    ref: component.ref,
    accuracy: component.model_accuracy || (component.primitive ? 'photo_only_placeholder' : 'unknown'),
    reason: component.primitive ? 'primitive placeholder' : 'model not yet source-verified'
  }));

function printMarkdown() {
  console.log(`# LayIt Geometry Audit\n`);
  console.log(`Manifest: ${manifestPath}`);
  console.log(`Product: ${manifest.product || manifest.id || 'unknown'}\n`);

  console.log(`## Summary\n`);
  console.log(`- Components: ${counts.components}`);
  console.log(`- Procedural primitives: ${counts.primitives}`);
  console.log(`- GLB models: ${counts.glbModels}`);
  console.log(`- Missing model_accuracy: ${counts.missingAccuracy}`);
  console.log(`- Missing source_refs: ${counts.missingSourceRefs}`);
  console.log(`- Footprint overlaps found: ${overlaps.length}`);
  console.log(`- Missing connection endpoints: ${missingEndpoints.length}\n`);

  console.log(`## Accuracy Counts\n`);
  for (const [level, count] of Object.entries(byAccuracy).sort()) {
    console.log(`- ${level}: ${count}`);
  }
  console.log('');

  console.log(`## Low-Trust Components\n`);
  if (!lowTrust.length) console.log(`None.`);
  for (const item of lowTrust) {
    console.log(`- Phase ${item.phase} ${item.ref}: ${item.accuracy} (${item.reason})`);
  }
  console.log('');

  console.log(`## Footprint Overlaps\n`);
  if (!overlaps.length) console.log(`None.`);
  for (const item of overlaps) {
    console.log(`- ${item.a} vs ${item.b}: ${item.overlap_mm[0]} x ${item.overlap_mm[1]} mm`);
  }
  console.log('');

  console.log(`## Missing Connection Endpoints\n`);
  if (!missingEndpoints.length) console.log(`None.`);
  for (const item of missingEndpoints) {
    console.log(`- Phase ${item.phase}: ${item.endpoint}`);
  }
}

if (process.argv.includes('--json')) {
  console.log(JSON.stringify({ counts, byAccuracy, overlaps, missingEndpoints, lowTrust }, null, 2));
} else {
  const outIndex = process.argv.indexOf('--out');
  if (outIndex >= 0) {
    const outPath = path.resolve(process.argv[outIndex + 1]);
    const lines = [];
    const originalLog = console.log;
    console.log = (...args) => lines.push(args.join(' '));
    printMarkdown();
    console.log = originalLog;
    fs.writeFileSync(outPath, `${lines.join('\n')}\n`);
    console.log(`Wrote ${outPath}`);
  } else {
    printMarkdown();
  }
}
