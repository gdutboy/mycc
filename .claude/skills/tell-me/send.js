#!/usr/bin/env node
/**
 * 飞书通知脚本 - 跨平台版本
 * 用法:
 *   node send.js "标题" "内容" [颜色]
 *   node send.js --file "标题" "文件路径" [颜色]
 *   node send.js --image-url "标题" "图片URL" [颜色]
 *
 * 颜色: blue(默认), green, orange, red
 */

const fs = require('fs');
const path = require('path');

function parseArgs(argv) {
  const imageUrlIndex = argv.indexOf('--image-url');
  if (imageUrlIndex !== -1 && argv.length > imageUrlIndex + 2) {
    return {
      mode: 'image-url',
      title: argv[imageUrlIndex + 1],
      imageUrl: argv[imageUrlIndex + 2],
      color: argv[imageUrlIndex + 3] || 'blue',
    };
  }

  const fileIndex = argv.indexOf('--file');
  if (fileIndex !== -1 && argv.length > fileIndex + 2) {
    return {
      mode: 'file',
      title: argv[fileIndex + 1],
      filePath: argv[fileIndex + 2],
      color: argv[fileIndex + 3] || 'blue',
    };
  }

  const [, , title, rawContent, color = 'blue'] = argv;
  return {
    mode: 'text',
    title,
    content: rawContent ? rawContent.replace(/\\n/g, '\n') : rawContent,
    color,
  };
}

function loadContent(parsed) {
  if (parsed.mode === 'file') {
    return fs.readFileSync(parsed.filePath, 'utf8');
  }

  if (parsed.mode === 'image-url') {
    return `🖼️ 图片链接：${parsed.imageUrl}\n\n[点击查看原图](${parsed.imageUrl})`;
  }

  return parsed.content;
}

function loadWebhook() {
  const configPath = path.join(__dirname, 'config.json');
  const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  return config.webhook;
}

function buildCard(title, content, color) {
  const headerTemplates = {
    blue: 'blue',
    green: 'green',
    orange: 'orange',
    red: 'red',
  };

  return {
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
}

async function sendCard(webhook, card) {
  const res = await fetch(webhook, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(card),
  });

  const data = await res.json();
  if (data.code !== 0) {
    throw new Error(data.msg || '飞书返回未知错误');
  }
}

async function main() {
  let parsed;

  try {
    parsed = parseArgs(process.argv);
  } catch (err) {
    console.error('❌ 参数解析失败:', err.message);
    process.exit(1);
  }

  if (!parsed.title || (parsed.mode !== 'image-url' && !parsed.content && !parsed.filePath) || (parsed.mode === 'image-url' && !parsed.imageUrl)) {
    console.error('用法: node send.js "标题" "内容" [颜色]');
    console.error('   或: node send.js --file "标题" "文件路径" [颜色]');
    console.error('   或: node send.js --image-url "标题" "图片URL" [颜色]');
    process.exit(1);
  }

  let content;
  try {
    content = loadContent(parsed);
  } catch (err) {
    console.error('❌ 无法读取文件:', err.message);
    process.exit(1);
  }

  let webhook;
  try {
    webhook = loadWebhook();
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

  try {
    const card = buildCard(parsed.title, content, parsed.color);
    await sendCard(webhook, card);
    console.log('✅ 发送成功');
  } catch (err) {
    console.error('❌ 发送失败:', err.message);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = {
  parseArgs,
  loadContent,
  buildCard,
};
