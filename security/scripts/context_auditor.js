#!/usr/bin/env node
/**
 * Context Auditor (v0)
 * - Reads core context files
 * - Estimates token usage (chars/4 heuristic)
 * - Flags bloat candidates with simple heuristics
 * - Produces a markdown report under /security/proposals/
 *
 * Safety: read-only.
 */

const fs = require('fs');
const path = require('path');

const WORKSPACE = '/data/workspace';
const OUT_DIR = path.join(WORKSPACE, 'security', 'proposals');

const FILES = [
  'SOUL.md',
  'USER.md',
  'IDENTITY.md',
  'TOOLS.md',
  'AGENTS.md',
  'MEMORY.md',
  'HEARTBEAT.md'
].map(f => path.join(WORKSPACE, f));

function estTokens(s){
  return Math.ceil(s.length / 4);
}

function topLongestSections(md){
  // naive split by headings
  const parts = md.split(/\n(?=#{1,6} )/g);
  const scored = parts
    .map(p => ({ text: p.trim(), chars: p.length, tokens: estTokens(p) }))
    .filter(x => x.text.length > 0)
    .sort((a,b)=>b.tokens-a.tokens);
  return scored.slice(0,5);
}

function repeatedLines(md){
  const lines = md.split('\n').map(l=>l.trim()).filter(l=>l.length>=20);
  const map = new Map();
  for (const l of lines){
    map.set(l, (map.get(l)||0)+1);
  }
  const reps = [...map.entries()].filter(([,c])=>c>=2)
    .sort((a,b)=>b[1]-a[1])
    .slice(0,10)
    .map(([line,count])=>({line,count}));
  return reps;
}

function ts(){
  const d=new Date();
  const pad=n=>String(n).padStart(2,'0');
  return `${d.getUTCFullYear()}${pad(d.getUTCMonth()+1)}${pad(d.getUTCDate())}-${pad(d.getUTCHours())}${pad(d.getUTCMinutes())}`;
}

function main(){
  if (!fs.existsSync(OUT_DIR)) fs.mkdirSync(OUT_DIR, {recursive:true});

  const rows = [];
  let totalTokens = 0;

  for (const f of FILES){
    if (!fs.existsSync(f)) continue;
    const md = fs.readFileSync(f,'utf8');
    const tokens = estTokens(md);
    totalTokens += tokens;

    rows.push({
      file: path.basename(f),
      chars: md.length,
      lines: md.split('\n').length,
      estTokens: tokens,
      longest: topLongestSections(md),
      repeats: repeatedLines(md)
    });
  }

  const outPath = path.join(OUT_DIR, `context-audit-${ts()}.md`);

  const mdOut = [];
  mdOut.push(`# Context Auditor Report (v0)\n`);
  mdOut.push(`Generated (UTC): ${new Date().toISOString()}\n`);
  mdOut.push(`Scope: core context files in ${WORKSPACE}\n`);
  mdOut.push(`## Summary\n`);
  mdOut.push(`- Estimated fixed-context tokens (chars/4 heuristic): **~${totalTokens} tokens** per turn (excluding chat history + tool outputs).\n`);
  mdOut.push(`- Goal suggestion: keep fixed-context <= **2,000 tokens**; move low-frequency content to /security/reference and load on-demand.\n`);

  mdOut.push(`## Per-file breakdown\n`);
  for (const r of rows){
    mdOut.push(`### ${r.file}\n`);
    mdOut.push(`- chars: ${r.chars}\n- lines: ${r.lines}\n- est tokens: ~${r.estTokens}\n`);

    mdOut.push(`**Top longest sections (naive heading split):**\n`);
    for (const s of r.longest){
      const preview = s.text.replace(/\s+/g,' ').slice(0,160);
      mdOut.push(`- ~${s.tokens} tokens | ${preview}${s.text.length>160?'…':''}\n`);
    }

    if (r.repeats.length){
      mdOut.push(`\n**Repeated lines (potential redundancy):**\n`);
      for (const rep of r.repeats){
        mdOut.push(`- x${rep.count}: ${rep.line.slice(0,180)}${rep.line.length>180?'…':''}\n`);
      }
    }

    mdOut.push(`\n**Bloat candidates (heuristic):**\n`);
    const candidates=[];
    if (r.estTokens > 1500) candidates.push('File is large for fixed context; consider splitting into “active” + archive/reference.');
    if (r.file === 'MEMORY.md') candidates.push('Long-term memory tends to accrete; move historical sections to archive and keep only durable facts + active objectives.');
    if (r.file === 'AGENTS.md') candidates.push('Coordination docs can be referenced on-demand; keep only the minimal operating contract in fixed context.');
    if (r.file === 'SOUL.md') candidates.push('Keep identity/voice compact; move long explanations to reference.');
    if (!candidates.length) candidates.push('No obvious red flags beyond normal size; still consider trimming if over budget.');
    for (const c of candidates) mdOut.push(`- ${c}\n`);
    mdOut.push('\n');
  }

  mdOut.push(`## Proposed next step (requires approval)\n`);
  mdOut.push(`1) Create /security/reference/context/ and move low-frequency text there.\n`);
  mdOut.push(`2) Reduce fixed context to a “thin core” (SOUL/USER/AGENTS/MEMORY trimmed).\n`);
  mdOut.push(`3) Generate a patch for review; only apply after explicit YES.\n`);

  fs.writeFileSync(outPath, mdOut.join(''), 'utf8');
  process.stdout.write(outPath + '\n');
}

main();
