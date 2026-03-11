/**
 * evolve/scan.mjs 测试
 * 运行：node scan.test.mjs
 */

import { strict as assert } from 'assert';
import { parseWatchlist, scoreRepo, formatReport } from './scan.mjs';

let passed = 0;
let failed = 0;

function test(name, fn) {
  try {
    fn();
    console.log(`  ✅ ${name}`);
    passed++;
  } catch (e) {
    console.log(`  ❌ ${name}`);
    console.log(`     ${e.message}`);
    failed++;
  }
}

// ─── parseWatchlist ───────────────────────────────────────────

console.log('\n📋 parseWatchlist');

test('解析正常条目', () => {
  const md = `
## 关注列表
- anthropics/anthropic-cookbook | 必看 | AI SDK 实践
- mem0ai/mem0 | 已覆盖 | 记忆系统
`;
  const list = parseWatchlist(md);
  assert.equal(list.length, 2);
  assert.equal(list[0].repo, 'anthropics/anthropic-cookbook');
  assert.equal(list[0].status, '必看');
  assert.equal(list[1].status, '已覆盖');
});

test('忽略注释行和空行', () => {
  const md = `
<!-- 这是注释 -->

- a/b | 观望 | 描述
`;
  const list = parseWatchlist(md);
  assert.equal(list.length, 1);
});

test('格式错误条目跳过', () => {
  const md = `
- 没有分隔符的行
- a/b | 观望 | 正常行
`;
  const list = parseWatchlist(md);
  assert.equal(list.length, 1);
  assert.equal(list[0].repo, 'a/b');
});

// ─── scoreRepo ────────────────────────────────────────────────

console.log('\n⭐ scoreRepo');

test('高 star + Claude 相关 → 高分', () => {
  const repo = {
    name: 'everything-claude-code',
    description: 'Everything about Claude Code skills and agents',
    stars: 68700,
    updatedDaysAgo: 1,
  };
  const score = scoreRepo(repo, ['memory', 'agent']);
  assert.ok(score >= 80, `期望 >=80，实际 ${score}`);
});

test('低 star + 无关 → 低分', () => {
  const repo = {
    name: 'random-tool',
    description: 'A random CLI tool',
    stars: 50,
    updatedDaysAgo: 300,
  };
  const score = scoreRepo(repo, ['memory', 'agent']);
  assert.ok(score < 40, `期望 <40，实际 ${score}`);
});

test('已在 watchlist 已覆盖 → 降分', () => {
  const repo = {
    name: 'mem0ai/mem0',
    description: 'Memory for AI agents',
    stars: 49200,
    updatedDaysAgo: 2,
    watchlistStatus: '已覆盖',
  };
  const score = scoreRepo(repo, ['memory']);
  assert.ok(score < 50, `已覆盖项目应降分，实际 ${score}`);
});

// ─── formatReport ─────────────────────────────────────────────

console.log('\n📝 formatReport');

test('报告包含三档分类', () => {
  const candidates = [
    { repo: 'a/worth-it', score: 85, reason: '理由A', recommendation: '值得引入' },
    { repo: 'b/watch', score: 60, reason: '理由B', recommendation: '观望' },
    { repo: 'c/covered', score: 20, reason: '理由C', recommendation: '已覆盖' },
  ];
  const report = formatReport(candidates, '2026-03-10');
  assert.ok(report.includes('值得引入'), '应包含值得引入');
  assert.ok(report.includes('观望'), '应包含观望');
  assert.ok(report.includes('已覆盖'), '应包含已覆盖');
  assert.ok(report.includes('2026-03-10'), '应包含日期');
});

test('无候选时报告不为空', () => {
  const report = formatReport([], '2026-03-10');
  assert.ok(report.length > 0);
  assert.ok(report.includes('今日无新发现') || report.includes('暂无'));
});

test('报告包含 repo 名称', () => {
  const candidates = [
    { repo: 'anthropics/awesome-claude', score: 90, reason: '测试理由', recommendation: '值得引入' },
  ];
  const report = formatReport(candidates, '2026-03-10');
  assert.ok(report.includes('anthropics/awesome-claude'));
});

// ─── 汇总 ─────────────────────────────────────────────────────

console.log(`\n结果：${passed} 通过，${failed} 失败\n`);
if (failed > 0) process.exit(1);
