#!/usr/bin/env node
/**
 * 采集系统协调器
 * 自动发现 collectors/*.mjs，并行运行，合并输出统一 JSON
 *
 * 用法：
 *   node collect.mjs                    # 运行全部 collector
 *   node collect.mjs --sources fxb,trends  # 只运行指定的
 *   node collect.mjs --save /path/to/dir   # 同时保存各源 JSON 到目录
 */

import { readdir, readFile } from 'fs/promises';
import { existsSync } from 'fs';
import { spawn } from 'child_process';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { writeFile, mkdir } from 'fs/promises';

const __dirname = dirname(fileURLToPath(import.meta.url));
const COLLECTORS_DIR = join(__dirname, 'collectors');
const CONFIG_DIR = join(__dirname, '..', 'config');
const TIMEOUT_MS = 60000; // 单个 collector 最大 60 秒

// 加载 JSON 配置（文件不存在时返回默认值）
async function loadConfig(filename, defaultVal) {
  const p = join(CONFIG_DIR, filename);
  if (!existsSync(p)) return defaultVal;
  try {
    return JSON.parse(await readFile(p, 'utf-8'));
  } catch {
    return defaultVal;
  }
}

// c9: 来源白名单过滤（domains 为空则不过滤）
function applyWhitelist(items, domains) {
  if (!domains || domains.length === 0) return { items, filtered: 0 };
  let filtered = 0;
  const kept = items.filter(item => {
    if (!item.url) return true; // 无 URL 的条目保留
    try {
      const hostname = new URL(item.url).hostname;
      const pass = domains.some(d => hostname === d || hostname.endsWith('.' + d));
      if (!pass) filtered++;
      return pass;
    } catch {
      return true;
    }
  });
  return { items: kept, filtered };
}

// c11: 关键词黑名单过滤
function applyBlacklist(items, keywords) {
  if (!keywords || keywords.length === 0) return { items, filtered: 0 };
  let filtered = 0;
  const kept = items.filter(item => {
    const text = `${item.title || ''} ${item.summary || ''}`;
    const hit = keywords.some(kw => text.includes(kw));
    if (hit) filtered++;
    return !hit;
  });
  return { items: kept, filtered };
}

// 解析命令行参数
function parseArgs() {
  const args = process.argv.slice(2);
  const result = { sources: null, saveDir: null };

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--sources' && args[i + 1]) {
      result.sources = args[++i].split(',');
    } else if (args[i] === '--save' && args[i + 1]) {
      result.saveDir = args[++i];
    }
  }

  return result;
}

// 运行单个 collector，返回解析后的 JSON
function runCollector(scriptPath) {
  return new Promise((resolve) => {
    let stdout = '';
    let stderr = '';

    const proc = spawn('node', [scriptPath], {
      timeout: TIMEOUT_MS,
      stdio: ['ignore', 'pipe', 'pipe'],
    });

    proc.stdout.on('data', (d) => { stdout += d; });
    proc.stderr.on('data', (d) => { stderr += d; });

    proc.on('close', (code) => {
      if (stderr) console.error(stderr.trim());

      try {
        resolve(JSON.parse(stdout));
      } catch {
        const name = scriptPath.split('/').pop().replace('.mjs', '');
        resolve({
          source: name,
          timestamp: new Date().toISOString(),
          metadata: { total_fetched: 0, error: `parse_error: exit code ${code}` },
          items: [],
        });
      }
    });

    proc.on('error', (err) => {
      const name = scriptPath.split('/').pop().replace('.mjs', '');
      resolve({
        source: name,
        timestamp: new Date().toISOString(),
        metadata: { total_fetched: 0, error: err.message },
        items: [],
      });
    });
  });
}

async function main() {
  const { sources: requestedSources, saveDir } = parseArgs();

  // 发现所有 collector
  const files = (await readdir(COLLECTORS_DIR))
    .filter(f => f.endsWith('.mjs') && !f.startsWith('_'))
    .sort();

  // 过滤
  const toRun = requestedSources
    ? files.filter(f => requestedSources.includes(f.replace('.mjs', '')))
    : files;

  if (toRun.length === 0) {
    console.error('[collect] No collectors to run');
    console.log(JSON.stringify({ collected_at: new Date().toISOString(), sources: [] }));
    return;
  }

  console.error(`[collect] Running ${toRun.length} collectors: ${toRun.map(f => f.replace('.mjs', '')).join(', ')}`);

  // 并行运行
  const results = await Promise.all(
    toRun.map(f => runCollector(join(COLLECTORS_DIR, f)))
  );

  // 保存各源 JSON（如果指定了 --save）
  if (saveDir) {
    await mkdir(saveDir, { recursive: true });
    for (const r of results) {
      await writeFile(
        join(saveDir, `${r.source}.json`),
        JSON.stringify(r, null, 2),
        'utf-8'
      );
    }
    console.error(`[collect] Saved raw JSON to ${saveDir}`);
  }

  // 加载过滤配置
  const whitelistCfg = await loadConfig('source-whitelist.json', { domains: [] });
  const blacklistCfg = await loadConfig('keyword-blacklist.json', { keywords: [] });
  let totalWhiteFiltered = 0;
  let totalBlackFiltered = 0;

  // 对每个 source 的 items 应用白名单 + 黑名单过滤
  for (const r of results) {
    if (!Array.isArray(r.items)) continue;
    const w = applyWhitelist(r.items, whitelistCfg.domains);
    const b = applyBlacklist(w.items, blacklistCfg.keywords);
    r.items = b.items;
    totalWhiteFiltered += w.filtered;
    totalBlackFiltered += b.filtered;
    if (r.metadata) {
      r.metadata.total_fetched = r.items.length;
    }
  }

  if (totalWhiteFiltered > 0) console.error(`[collect] 白名单过滤: ${totalWhiteFiltered} 条`);
  if (totalBlackFiltered > 0) console.error(`[collect] 黑名单过滤: ${totalBlackFiltered} 条`);

  // 统计
  for (const r of results) {
    const status = r.metadata?.error ? `error: ${r.metadata.error}` : `${r.metadata?.total_fetched || 0} items`;
    console.error(`[collect]   ${r.source}: ${status}`);
  }

  // 输出合并结果
  const output = {
    collected_at: new Date().toISOString(),
    sources: results,
  };

  console.log(JSON.stringify(output));
}

main().catch(err => {
  console.error(`[collect] Fatal: ${err.message}`);
  process.exit(1);
});
