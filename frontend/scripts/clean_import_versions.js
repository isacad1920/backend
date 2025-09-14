#!/usr/bin/env node
/**
 * Clean version-suffixed imports like "lucide-react@0.487.0" or
 * "@radix-ui/react-select@2.1.6" into plain package names.
 * Also handles class-variance-authority and similar patterns.
 */

import { readdirSync, statSync, readFileSync, writeFileSync } from 'fs';
import { join, extname } from 'path';

const ROOT = process.argv[2] || '.';
const exts = new Set(['.ts', '.tsx', '.js', '.jsx']);
const importPattern = /from\s+['"]([^'"]+)['"]/g;

function stripVersion(spec) {
  // If there's an '@' in middle of path after the scope/package, like package@1.2.3
  // Convert occurrences like: name@version or @scope/name@version -> remove trailing @version
  // Avoid removing leading scope '@'
  // Strategy: split by '/'; for each segment after possible scope, if it contains '@' and not at start of the whole string, strip suffix after second '@'
  // Simpler: capture patterns '@[0-9].*' at end of segment and remove.
  return spec.replace(/(@[^/]+)@\d[^/]+/g, (_, pre) => pre)
             .replace(/([^@/]+)@\d[^/]+/g, (_, pre) => pre);
}

function processFile(fp) {
  const original = readFileSync(fp, 'utf8');
  let changed = false;
  const updated = original.replace(importPattern, (m, spec) => {
    if (spec.includes('@') && /@\d/.test(spec)) {
      const clean = stripVersion(spec);
      if (clean !== spec) {
        changed = true;
        return m.replace(spec, clean);
      }
    }
    return m;
  });
  if (changed) {
    writeFileSync(fp, updated, 'utf8');
    console.log('Updated', fp);
  }
}

function walk(dir) {
  for (const entry of readdirSync(dir)) {
    if (entry.startsWith('.')) continue;
    const full = join(dir, entry);
    const st = statSync(full);
    if (st.isDirectory()) {
      if (entry === 'node_modules') continue;
      walk(full);
    } else if (exts.has(extname(entry))) {
      processFile(full);
    }
  }
}

walk(join(ROOT, 'components'));
console.log('Import version cleaning complete.');
