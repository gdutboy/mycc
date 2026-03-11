/**
 * evolve/scan.mjs
 * GitHub 扫描 + Gap 分析 + 报告生成
 *
 * 用法：
 *   node scan.mjs              # 完整扫描，输出报告
 *   node scan.mjs --dry-run    # 只打印，不写日志
 */

import { readFileSync, existsSync, readdirSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __dir = dirname(fileURLToPath(import.meta.url));
const SKILL_DIR = join(__dir, '..');
const PROJECT_DIR = join(__dir, '../../../../');  // mycc 根目录
const WATCHLIST_PATH = join(__dir, 'watchlist.md');
const SKILLS_DIR = join(PROJECT_DIR, '.claude/skills');
const LOG_PATH = join(PROJECT_DIR, '0-Skill-Platform/evolve-log.md');
const TELL_ME_CONFIG = join(PROJECT_DIR, '.claude/skills/tell-me/config.json');

// cc 架构关键词，用于相关性评分
const CC_KEYWORDS = [
  'claude', 'claude-code', 'agent', 'skill', 'mcp', 'memory', 'prompt',
  'llm', 'ai', 'instinct', 'orchestrat', 'automation', 'tool-use',
  'workflow', 'multi-agent', 'subagent', 'context', 'hook',
];

// ─── parseWatchlist ──────────────────────────────────────────────────────────

/**
 * 解析 watchlist.md，返回关注仓库列表
 * 格式：- owner/repo | 状态 | 备注
 */
export function parseWatchlist(md) {
  const result = [];
  for (const line of md.split('\n')) {
    const trimmed = line.trim();
    if (!trimmed.startsWith('-') || trimmed.startsWith('<!--')) continue;
    const content = trimmed.replace(/^-\s*/, '');
    const parts = content.split('|').map(s => s.trim());
    if (parts.length < 2) continue;
    const repo = parts[0];
    if (!repo.includes('/')) continue;
    result.push({
      repo,
      status: parts[1] || '未知',
      note: parts[2] || '',
    });
  }
  return result;
}

// ─── scoreRepo ───────────────────────────────────────────────────────────────

/**
 * 对仓库打分（0-100），决定优先级
 */
export function scoreRepo(repo, currentSkills = []) {
  let score = 0;
  const desc = (repo.description || '').toLowerCase();
  const name = (repo.name || '').toLowerCase();

  // 已覆盖直接降分
  if (repo.watchlistStatus === '已覆盖') return 10;

  // Star 数评分（最高 30 分）
  const stars = repo.stars || 0;
  if (stars >= 50000) score += 30;
  else if (stars >= 10000) score += 22;
  else if (stars >= 1000) score += 14;
  else if (stars >= 100) score += 6;

  // 关键词相关性（最高 40 分）
  let keywordHits = 0;
  for (const kw of CC_KEYWORDS) {
    if (name.includes(kw) || desc.includes(kw)) keywordHits++;
  }
  score += Math.min(keywordHits * 8, 40);

  // 活跃度（最高 20 分）
  const days = repo.updatedDaysAgo ?? 999;
  if (days <= 3) score += 20;
  else if (days <= 14) score += 14;
  else if (days <= 60) score += 6;

  // watchlist 必看加权（最高 10 分）
  if (repo.watchlistStatus === '必看') score += 10;
  else if (repo.watchlistStatus === '观望') score += 4;

  return Math.min(score, 100);
}

// ─── formatReport ────────────────────────────────────────────────────────────

/**
 * 生成飞书报告文本
 */
export function formatReport(candidates, date) {
  if (!candidates || candidates.length === 0) {
    return `📊 cc 自进化巡检 ${date}\n\n今日无新发现，保持现状。`;
  }

  const worthy = candidates.filter(c => c.recommendation === '值得引入');
  const watch = candidates.filter(c => c.recommendation === '观望');
  const covered = candidates.filter(c => c.recommendation === '已覆盖');

  let lines = [`📊 cc 自进化巡检 ${date}\n`];

  if (worthy.length) {
    lines.push('✅ 值得引入');
    for (const c of worthy) {
      lines.push(`  • ${c.repo}（⭐${formatStars(c.stars)}）`);
      lines.push(`    ${c.reason}`);
    }
    lines.push('');
  }

  if (watch.length) {
    lines.push('👀 观望');
    for (const c of watch) {
      lines.push(`  • ${c.repo}（⭐${formatStars(c.stars)}）`);
      lines.push(`    ${c.reason}`);
    }
    lines.push('');
  }

  if (covered.length) {
    lines.push('⏭️ 已覆盖');
    for (const c of covered) {
      lines.push(`  • ${c.repo} — ${c.reason}`);
    }
    lines.push('');
  }

  if (worthy.length) {
    lines.push('回复"升级 <repo名>"立即开发，或"备用 <repo名>"记录观望。');
  }

  return lines.join('\n');
}

function formatStars(n) {
  if (!n) return '?';
  if (n >= 1000) return `${(n / 1000).toFixed(1)}k`;
  return String(n);
}

// ─── GitHub 数据抓取 ──────────────────────────────────────────────────────────

async function fetchTrending() {
  try {
    const res = await fetch('https://github.com/trending?since=daily&spoken_language_code=', {
      headers: { 'User-Agent': 'cc-evolve-scanner/1.0' },
      signal: AbortSignal.timeout(15000),
    });
    const html = await res.text();

    // 提取仓库信息
    const repoPattern = /<h2[^>]*>\s*<a\s+href="\/([^"]+)"[^>]*>/g;
    const starsPattern = /(\d[\d,]*)\s*stars today/g;
    const descPattern = /<p[^>]*class="[^"]*col-9[^"]*"[^>]*>\s*([\s\S]*?)\s*<\/p>/g;

    const repos = [];
    let match;
    const hrefs = [];
    while ((match = repoPattern.exec(html)) !== null) {
      hrefs.push(match[1].trim());
    }

    const stars = [];
    while ((match = starsPattern.exec(html)) !== null) {
      stars.push(parseInt(match[1].replace(/,/g, ''), 10));
    }

    for (let i = 0; i < hrefs.length; i++) {
      repos.push({
        name: hrefs[i],
        repo: hrefs[i],
        description: '',
        stars: stars[i] || 0,
        updatedDaysAgo: 1,
      });
    }
    return repos.slice(0, 25);
  } catch (e) {
    console.error('[Trending] 抓取失败:', e.message);
    return [];
  }
}

async function fetchRepoInfo(repoPath) {
  try {
    const res = await fetch(`https://api.github.com/repos/${repoPath}`, {
      headers: { 'User-Agent': 'cc-evolve-scanner/1.0', 'Accept': 'application/vnd.github.v3+json' },
      signal: AbortSignal.timeout(10000),
    });
    if (!res.ok) return null;
    const data = await res.json();
    const updated = new Date(data.updated_at);
    const daysAgo = Math.floor((Date.now() - updated) / 86400000);
    return {
      name: repoPath,
      repo: repoPath,
      description: data.description || '',
      stars: data.stargazers_count || 0,
      updatedDaysAgo: daysAgo,
    };
  } catch {
    return null;
  }
}

// ─── 读取当前 skills ──────────────────────────────────────────────────────────

function getCurrentSkills() {
  try {
    return readdirSync(SKILLS_DIR);
  } catch {
    return [];
  }
}

// ─── 主流程 ───────────────────────────────────────────────────────────────────

export async function runScan() {
  const date = new Date().toISOString().slice(0, 10);
  console.log(`[evolve] 开始巡检 ${date}`);

  // 1. 读取 watchlist
  let watchlist = [];
  if (existsSync(WATCHLIST_PATH)) {
    watchlist = parseWatchlist(readFileSync(WATCHLIST_PATH, 'utf-8'));
    console.log(`[evolve] watchlist: ${watchlist.length} 个仓库`);
  }

  // 2. 读取当前 skills
  const currentSkills = getCurrentSkills();

  // 3. 并行抓取 trending + watchlist 详情
  console.log('[evolve] 抓取 GitHub Trending...');
  const [trending, watchlistDetails] = await Promise.all([
    fetchTrending(),
    Promise.all(
      watchlist
        .filter(w => w.status !== '已覆盖')
        .map(w => fetchRepoInfo(w.repo).then(info => info ? { ...info, watchlistStatus: w.status } : null))
    ),
  ]);

  // 合并去重
  const seen = new Set();
  const allRepos = [];
  for (const r of [...watchlistDetails.filter(Boolean), ...trending]) {
    const key = r.repo || r.name;
    if (!seen.has(key)) {
      seen.add(key);
      allRepos.push(r);
    }
  }

  // 4. 打分 + 分类
  const candidates = allRepos
    .map(r => {
      const score = scoreRepo(r, currentSkills);
      let recommendation;
      if (r.watchlistStatus === '已覆盖') recommendation = '已覆盖';
      else if (score >= 70) recommendation = '值得引入';
      else if (score >= 40) recommendation = '观望';
      else recommendation = '已覆盖';

      // 生成理由
      const kws = CC_KEYWORDS.filter(k =>
        (r.description || '').toLowerCase().includes(k) ||
        (r.name || '').toLowerCase().includes(k)
      );
      const reason = kws.length
        ? `涉及 ${kws.slice(0, 3).join('、')}，与 cc 架构高度相关`
        : (r.watchlistStatus === '已覆盖' ? '现有 skill 已覆盖' : '相关性待评估');

      return { ...r, score, recommendation, reason };
    })
    .filter(r => r.recommendation !== '已覆盖' || r.watchlistStatus === '已覆盖')
    .sort((a, b) => b.score - a.score)
    .slice(0, 15);

  // 5. 生成报告
  const report = formatReport(candidates, date);
  console.log('\n' + report);

  // 6. 推送飞书通知
  await sendFeishu(report);

  return { report, candidates, date };
}

// ─── 飞书通知 ─────────────────────────────────────────────────────────────────

async function sendFeishu(content) {
  let webhook;
  try {
    const cfg = JSON.parse(readFileSync(TELL_ME_CONFIG, 'utf-8'));
    webhook = cfg.webhook;
  } catch {
    console.warn('[evolve] 飞书配置读取失败，跳过推送');
    return;
  }

  if (!webhook || webhook.includes('YOUR_FEISHU')) {
    console.warn('[evolve] 飞书 webhook 未配置，跳过推送');
    return;
  }

  const card = {
    msg_type: 'interactive',
    card: {
      header: {
        title: { content: '🧬 cc 自进化巡检报告', tag: 'plain_text' },
        template: 'blue',
      },
      elements: [
        { tag: 'div', text: { content, tag: 'lark_md' } },
        { tag: 'note', elements: [{ tag: 'plain_text', content: `⏰ ${new Date().toLocaleString('zh-CN')}` }] },
      ],
    },
  };

  try {
    const res = await fetch(webhook, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(card),
      signal: AbortSignal.timeout(10000),
    });
    const data = await res.json();
    if (data.code === 0) {
      console.log('[evolve] 飞书推送成功 ✅');
    } else {
      console.error('[evolve] 飞书推送失败:', data.msg);
    }
  } catch (e) {
    console.error('[evolve] 飞书推送异常:', e.message);
  }
}

// CLI 入口
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  runScan().catch(e => {
    console.error('[evolve] 扫描失败:', e);
    process.exit(1);
  });
}
