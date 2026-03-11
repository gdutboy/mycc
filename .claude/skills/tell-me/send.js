#!/usr/bin/env node
/**
 * 飞书通知脚本 - 跨平台版本
 * 用法: node send.js "标题" "内容" [颜色]
 * 颜色: blue(默认), green, orange, red
 */

const fs = require('fs');
const path = require('path');

let title, content, color = 'blue';

// 检查是否有 --file 参数
const fileIndex = process.argv.indexOf('--file');
if (fileIndex !== -1 && process.argv.length > fileIndex + 2) {
  // --file 模式：读取文件内容
  title = process.argv[fileIndex + 1];
  const filePath = process.argv[fileIndex + 2];
  color = process.argv[fileIndex + 3] || 'blue';

  try {
    content = fs.readFileSync(filePath, 'utf8');
  } catch (err) {
    console.error('❌ 无法读取文件:', err.message);
    process.exit(1);
  }
} else {
  // 普通模式
  [, , title, content, color = 'blue'] = process.argv;
  // 命令行参数中的 \n 是字面字符串，转成真换行
  if (content) content = content.replace(/\\n/g, '\n');
}

if (!title || !content) {
  console.error('用法: node send.js "标题" "内容" [颜色]');
  console.error('   或: node send.js --file "标题" "文件路径" [颜色]');
  process.exit(1);
}

// 读取配置文件
const configPath = path.join(__dirname, 'config.json');

let webhook;
try {
  const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  webhook = config.webhook;
} catch (err) {
  console.error('❌ 无法读取配置文件:', err.message);
  process.exit(1);
}

if (!webhook || webhook === 'YOUR_FEISHU_WEBHOOK_HERE') {
  console.error('❌ 飞书 webhook 未配置');
  console.error('');
  console.error('请在 config.json 中配置 webhook 地址');
  console.error('详见：.claude/skills/tell-me/配置SOP.md');
  process.exit(1);
}

// Schema 2.0 颜色映射
const headerTemplates = {
  blue: 'blue',
  green: 'green',
  orange: 'orange',
  red: 'red',
};

const card = {
  msg_type: 'interactive',
  card: {
    schema: '2.0',
    config: { wide_screen_mode: true },
    header: {
      title: { content: `📌 ${title}`, tag: 'plain_text' },
      template: headerTemplates[color] || 'blue',
    },
    body: {
      elements: [
        { tag: 'markdown', content },
        { tag: 'hr' },
        {
          tag: 'markdown',
          content: `⏰ ${new Date().toLocaleString('zh-CN')}`,
          text_size: 'notation',
        },
      ],
    },
  },
};

fetch(webhook, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(card)
})
  .then(res => res.json())
  .then(data => {
    if (data.code === 0) {
      console.log('✅ 发送成功');
    } else {
      console.error('❌ 发送失败:', data.msg);
      process.exit(1);
    }
  })
  .catch(err => {
    console.error('❌ 请求失败:', err.message);
    process.exit(1);
  });
