const test = require('node:test');
const assert = require('node:assert/strict');

const { parseArgs, loadContent, buildCard } = require('./send.js');

test('parseArgs 解析文本模式参数', () => {
  const parsed = parseArgs(['node', 'send.js', '标题', 'line1\\nline2', 'green']);

  assert.equal(parsed.mode, 'text');
  assert.equal(parsed.title, '标题');
  assert.equal(parsed.content, 'line1\nline2');
  assert.equal(parsed.color, 'green');
});

test('parseArgs 解析文件模式参数', () => {
  const parsed = parseArgs(['node', 'send.js', '--file', '日报', '/tmp/a.md', 'orange']);

  assert.equal(parsed.mode, 'file');
  assert.equal(parsed.title, '日报');
  assert.equal(parsed.filePath, '/tmp/a.md');
  assert.equal(parsed.color, 'orange');
});

test('parseArgs 解析图片 URL 模式参数', () => {
  const parsed = parseArgs(['node', 'send.js', '--image-url', '配图', 'https://img.example/a.png', 'blue']);

  assert.equal(parsed.mode, 'image-url');
  assert.equal(parsed.title, '配图');
  assert.equal(parsed.imageUrl, 'https://img.example/a.png');
  assert.equal(parsed.color, 'blue');
});

test('loadContent 在图片 URL 模式下生成稳妥文本内容', () => {
  const content = loadContent({ mode: 'image-url', imageUrl: 'https://img.example/cat.png' });

  assert.doesNotMatch(content, /^!\[/);
  assert.match(content, /图片链接：https:\/\/img\.example\/cat\.png/);
  assert.match(content, /\[点击查看原图\]\(https:\/\/img\.example\/cat\.png\)/);
});

test('buildCard 构建 interactive 卡片结构', () => {
  const card = buildCard('测试标题', '测试内容', 'red');

  assert.equal(card.msg_type, 'interactive');
  assert.equal(card.card.header.title.content, '📌 测试标题');
  assert.equal(card.card.header.template, 'red');
  assert.equal(card.card.body.elements[0].tag, 'markdown');
  assert.equal(card.card.body.elements[0].content, '测试内容');
});
