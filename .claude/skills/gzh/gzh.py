#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

"""
GZH - 公众号排版渲染脚本

将 Markdown 文章渲染成公众号可用的格式。

使用方法：
    python gzh.py "Markdown内容"           # 命令行
    python gzh.py --file file.md         # 从文件读取
    python gzh.py --interactive           # 交互模式
"""
import os
import sys
import argparse
import re

# 颜色
GREEN = '\033[92m'
BLUE = '\033[94m'
RESET = '\033[0m'


def banner():
    print(f"""
{BLUE}╔═══════════════════════════════════════════════════╗
║        📱 GZH - 公众号排版渲染                     ║
║           将 Markdown 渲染成公众号格式             ║
╚═══════════════════════════════════════════════════╝{RESET}
    """)


# CSS 样式
GZH_CSS = """
<style>
/* 全局 */
body {
    font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
    font-size: 15px;
    line-height: 1.8;
    color: #2c2c2c;
}

/* 标题 */
h1 {
    font-size: 16px;
    font-weight: bold;
    text-align: center;
    margin: 24px 0 16px;
}

h2 {
    font-size: 15px;
    font-weight: bold;
    margin: 20px 0 12px;
}

h3 {
    font-size: 14px;
    font-weight: bold;
    margin: 16px 0 8px;
}

/* 段落 */
p {
    margin-bottom: 16px;
}

/* 引用 */
blockquote {
    border-left: 3px solid #3b82f6;
    background: #f8f9fa;
    padding: 12px 16px;
    margin: 16px 0;
    font-style: italic;
    color: #555;
}

/* 代码 */
code {
    background: #f1f1f1;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'SF Mono', Monaco, Consolas, monospace;
    font-size: 13px;
}

pre {
    background: #1e1e1e;
    color: #d4d4d4;
    padding: 16px;
    border-radius: 8px;
    overflow-x: auto;
    margin: 16px 0;
}

pre code {
    background: none;
    padding: 0;
    color: inherit;
}

/* 列表 */
ul, ol {
    padding-left: 24px;
    margin: 12px 0;
}

li {
    margin: 4px 0;
}

/* 分割线 */
hr {
    border: none;
    border-top: 1px solid #e0e0e0;
    margin: 24px 0;
}

/* 加粗 */
strong {
    font-weight: 600;
}

/* 链接 */
a {
    color: #4a9eff;
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}
</style>
"""


def parse_markdown(md):
    """解析 Markdown 并返回 HTML"""
    lines = md.split('\n')
    html_lines = []
    in_code_block = False
    in_list = False

    for line in lines:
        # 代码块
        if line.startswith('```'):
            if in_code_block:
                html_lines.append('</code></pre>')
                in_code_block = False
            else:
                lang = line[3:].strip()
                html_lines.append(f'<pre><code class="language-{lang}">')
                in_code_block = True
            continue

        if in_code_block:
            html_lines.append(line)
            continue

        # 标题
        if line.startswith('### '):
            html_lines.append(f'<h3>{line[4:]}</h3>')
        elif line.startswith('## '):
            html_lines.append(f'<h2>{line[3:]}</h2>')
        elif line.startswith('# '):
            html_lines.append(f'<h1>{line[2:]}</h1>')

        # 分割线
        elif line.strip() in ['---', '***', '___']:
            html_lines.append('<hr>')

        # 引用
        elif line.startswith('> '):
            html_lines.append(f'<blockquote>{line[2:]}</blockquote>')

        # 无序列表
        elif line.startswith('- ') or line.startswith('* '):
            html_lines.append(f'<li>{line[2:]}</li>')
            in_list = True

        # 有序列表
        elif re.match(r'^\d+\.\s', line):
            html_lines.append(f'<li>{line[line.find(".")+2:]}</li>')
            in_list = True

        # 空行
        elif not line.strip():
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            continue

        # 正文
        else:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            # 处理行内格式
            processed = process_inline(line)
            html_lines.append(f'<p>{processed}</p>')

    return '\n'.join(html_lines)


def process_inline(text):
    """处理行内格式：加粗、斜体、代码、链接"""
    # 代码
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)

    # 加粗
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)

    # 斜体
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)

    # 链接
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)

    return text


def render_gzh(md, wrap_html=True):
    """渲染公众号格式"""
    html = parse_markdown(md)

    if wrap_html:
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>公众号排版</title>
    {GZH_CSS}
</head>
<body>
{html}
</body>
</html>"""

    return html


def main():
    parser = argparse.ArgumentParser(description='GZH - 公众号排版渲染')
    parser.add_argument('content', nargs='?', help='Markdown 内容')
    parser.add_argument('--file', '-f', metavar='FILE', help='从文件读取')
    parser.add_argument('--output', '-o', metavar='FILE', help='输出到文件')
    parser.add_argument('--preview', '-p', action='store_true', help='生成可预览的 HTML')
    parser.add_argument('--copy', '-c', action='store_true', help='生成可直接复制的文本')

    args = parser.parse_args()

    # 读取内容
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"{RED}读取文件失败: {e}{RESET}")
            return
    elif args.content:
        content = args.content
    else:
        banner()
        print("请输入 Markdown 内容（输入完成后按 Ctrl+D 或 Ctrl+Z）：")
        content = sys.stdin.read()

    # 渲染
    html = render_gzh(content, wrap_html=args.preview)

    # 输出
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"{GREEN}已保存到: {args.output}{RESET}")
    elif args.copy:
        # 生成可复制到公众号的文本
        print(html)
    else:
        # 默认输出 HTML
        print(html)


if __name__ == '__main__':
    main()
