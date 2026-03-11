#!/usr/bin/env node
/**
 * A股要闻 Collector
 * 数据源：新浪财经
 */

import { fetchWithRetry, makeResult } from '../lib/fetcher.mjs';

const SOURCE_NAME = 'cn-stock';

async function fetchSinaStock() {
  const url = 'https://finance.sina.com.cn/stock/';
  const res = await fetchWithRetry(url, { timeout: 15000 });
  const html = await res.text();

  const items = [];
  // 匹配财经新闻链接
  const regex = /href="(https?:\/\/finance\.sina\.com\.cn\/stock\/[^"]+)"[^>]*>([^<]{6,40})<\/a>/g;
  let match;
  let count = 0;

  while ((match = regex.exec(html)) !== null && count < 15) {
    const href = match[1];
    const title = match[2].trim();

    // 过滤掉无关链接
    if (title.length > 6 && !title.includes('更多') && !title.includes('>>')) {
      // 过滤掉日期开头的
      if (!/^\[/.test(title)) {
        items.push({
          title: title,
          url: href,
          summary: '',
          meta: { source: '新浪财经' }
        });
        count++;
      }
    }
  }

  // 去重
  const seen = new Set();
  return items.filter(item => {
    if (seen.has(item.title)) return false;
    seen.add(item.title);
    return true;
  });
}

async function fetchEastmoney() {
  const url = 'https://stock.eastmoney.com/a/cywjh.html';
  const res = await fetchWithRetry(url, { timeout: 15000 });
  const html = await res.text();

  const items = [];
  // 匹配东方财富新闻
  const regex = /title="([^"]{8,50})"[^>]+href="(https?:\/\/[^"]+\.shtml)"/g;
  let match;
  let count = 0;

  while ((match = regex.exec(html)) !== null && count < 10) {
    const title = match[1].trim();
    const href = match[2];

    // 过滤
    if (title.length > 8 && !title.includes('详情') && !title.includes('更多')) {
      if (href.includes('eastmoney')) {
        items.push({
          title: title,
          url: href,
          summary: '',
          meta: { source: '东方财富' }
        });
        count++;
      }
    }
  }

  return items;
}

async function main() {
  const allItems = [];
  const errors = [];

  try {
    const sina = await fetchSinaStock();
    allItems.push(...sina);
  } catch (e) {
    errors.push({ source: '新浪财经', error: e.message });
  }

  try {
    const em = await fetchEastmoney();
    allItems.push(...em);
  } catch (e) {
    errors.push({ source: '东方财富', error: e.message });
  }

  // 去重
  const seen = new Set();
  const uniqueItems = allItems.filter(item => {
    if (seen.has(item.title)) return false;
    seen.add(item.title);
    return true;
  });

  console.log(JSON.stringify(makeResult(SOURCE_NAME, uniqueItems, {
    total: uniqueItems.length,
    errors: errors.length > 0 ? errors : undefined
  })));
}

main().catch(err => {
  console.log(JSON.stringify(makeResult(SOURCE_NAME, [], { error: err.message })));
});
