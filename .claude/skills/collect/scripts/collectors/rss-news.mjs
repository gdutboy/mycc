#!/usr/bin/env node
/**
 * 时政热点 RSS Collector
 * 数据源：新华网、人民网、央视新闻等主流媒体
 *
 * 用法：
 *   node rss-news.mjs                                           # 采集（默认 24h）
 *   node rss-news.mjs --extract /path/to/rss-news.json 3,8     # 按序号提取
 *   node rss-news.mjs --index /path/to/rss-news.json           # 打印索引列表
 */

import { fetchFeeds } from '../lib/rss-parser.mjs';
import { makeResult, extractItems } from '../lib/fetcher.mjs';

const SOURCE_NAME = 'rss-news';

const FEEDS = [
  { name: 'BBC中文', url: 'https://feeds.bbci.co.uk/zhongwen/simp/rss.xml', enabled: true },
  { name: '纽约时报中文', url: 'https://cn.nytimes.com/rss/', enabled: true },
  { name: '联合早报', url: 'https://www.zaobao.com.sg/rss/zbsg.xml', enabled: true },
  { name: 'BBC中文', url: 'https://feeds.bbci.co.uk/news/world/rss.xml', enabled: false }, // 英文对照
];

// --extract 格式化
function formatExtract(item, idx) {
  const m = item.meta || {};
  const lines = [];
  lines.push(`### [rss-news:${idx}] ${item.title}`);
  lines.push('');
  lines.push(`**来源**：${m.feedName || '-'} | **日期**：${item.pubDate || '-'}`);
  if (item.url) lines.push(`**链接**：${item.url}`);
  lines.push('');
  if (item.summary) {
    lines.push(item.summary);
    lines.push('');
  }
  return lines.join('\n');
}

// --index 格式化
function printIndex(data) {
  const items = data.items || [];
  console.log(`## ${SOURCE_NAME} 索引（共 ${items.length} 条）\n`);
  for (let i = 0; i < items.length; i++) {
    const item = items[i];
    const feedName = item.meta?.feedName || '-';
    const date = item.pubDate ? item.pubDate.slice(0, 10) : '-';
    console.log(`[${i}] [${feedName}] ${item.title} (${date})`);
  }
}

async function main() {
  const extFlag = process.argv.indexOf('--extract');
  if (extFlag !== -1) {
    const jsonPath = process.argv[extFlag + 1];
    const indices = process.argv[extFlag + 2];
    if (!jsonPath || !indices) {
      console.error('Usage: node rss-news.mjs --extract <json> <idx,idx,...|all>');
      process.exit(1);
    }
    return extractItems(jsonPath, indices, formatExtract, SOURCE_NAME);
  }

  const idxFlag = process.argv.indexOf('--index');
  if (idxFlag !== -1) {
    const jsonPath = process.argv[idxFlag + 1];
    if (!jsonPath) {
      console.error('Usage: node rss-news.mjs --index <json>');
      process.exit(1);
    }
    const { readFile } = await import('fs/promises');
    const raw = await readFile(jsonPath, 'utf-8');
    printIndex(JSON.parse(raw));
    return;
  }

  // 采集模式
  const { items, errors } = await fetchFeeds(FEEDS, { hoursBack: 24 });

  const metadata = {
    feeds: FEEDS.filter(f => f.enabled !== false).map(f => f.name),
  };
  if (errors.length > 0) {
    metadata.errors = errors;
  }

  console.log(JSON.stringify(makeResult(SOURCE_NAME, items, metadata)));
}

main().catch(err => {
  console.log(JSON.stringify(makeResult(SOURCE_NAME, [], { error: err.message })));
});
