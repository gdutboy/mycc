#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

"""
Draft - 文章初稿生成脚本

根据大纲生成文章初稿模板，引导写作流程。

使用方法：
    python draft.py "主题"                        # 命令行
    python draft.py --topic "主题" --outline "大纲"  # 指定大纲
    python draft.py --file outline.md            # 从大纲文件读取
    python draft.py --interactive                # 交互模式
"""
import os
import sys
import argparse
import re

# 颜色
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RED = '\033[91m'
RESET = '\033[0m'


def banner():
    print(f"""
{BLUE}╔═══════════════════════════════════════════════════╗
║        ✍️ Draft - 文章初稿生成                     ║
║           根据大纲生成初稿，引导写作流程           ║
╚═══════════════════════════════════════════════════╝{RESET}
    """)


def parse_outline(outline_text):
    """解析大纲文本"""
    sections = []
    current_section = None

    lines = outline_text.strip().split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 一级标题
        if line.startswith('## '):
            if current_section:
                sections.append(current_section)
            current_section = {
                'title': line[3:].strip(),
                'level': 1,
                'points': []
            }
        # 二级标题
        elif line.startswith('### '):
            if current_section:
                current_section['points'].append({
                    'title': line[4:].strip(),
                    'level': 2,
                    'content': ''
                })
        # 无序列表
        elif line.startswith('- ') or line.startswith('* '):
            if current_section:
                current_section['points'].append({
                    'title': line[2:].strip(),
                    'level': 2,
                    'content': ''
                })
        # 数字列表
        elif re.match(r'^\d+\.\s', line):
            if current_section:
                current_section['points'].append({
                    'title': re.sub(r'^\d+\.\s', '', line),
                    'level': 2,
                    'content': ''
                })

    if current_section:
        sections.append(current_section)

    return sections


def generate_draft_template(topic, sections, style='默认'):
    """生成初稿模板"""
    draft = f"""# {topic}

---

## 引言

【引言写作引导】
- 用一个故事、数据或现象引入主题
- 点明这篇文章要解决什么问题
- 告诉读者能获得什么价值

> 你的引言内容...

---

"""

    for i, section in enumerate(sections):
        draft += f"## {section['title']}\n\n"

        if section['points']:
            for point in section['points']:
                if isinstance(point, dict):
                    draft += f"### {point['title']}\n\n"
                    draft += f"【写作要点】\n- 要点1\n- 要点2\n- 例子：\n\n> 在这里写下你的内容...\n\n"
                else:
                    draft += f"- {point}\n"
        else:
            draft += f"【写作要点】\n- 要点1\n- 要点2\n- 例子：\n\n> 在这里写下你的内容...\n\n"

        draft += "---\n\n"

    draft += f"""## 总结

【总结写作引导】
- 回顾核心观点（一句话概括）
- 给出具体的行动建议（1-2条）
- 留一个开放性问题或思考

> 你的总结内容...

---

## 写作风格指南

当前风格：{style}

- 口语化表达，多用短句
- 每个观点配一个具体例子
- 有态度、有温度、不端着
- 保持实用为主，不过度华丽
"""

    return draft


def format_output(topic, draft, sections):
    """格式化输出"""
    output = f"""
{GREEN}╔═══════════════════════════════════════════════════╗
║                   ✍️ 初稿模板生成                      ║
╚═══════════════════════════════════════════════════╝{RESET}

{YELLOW}【主题】{RESET}
{topic}

{YELLOW}【章节数】{RESET}
{len(sections)} 个章节

{GREEN}【初稿模板】{RESET}

{draft}

{YELLOW}【后续流程】{RESET}
1. 填充每个章节的具体内容
2. 用 polish 精修语言
3. 用 gzh 排版发布

"""

    return output


def main():
    parser = argparse.ArgumentParser(description='Draft - 文章初稿生成')
    parser.add_argument('topic', nargs='?', help='文章主题')
    parser.add_argument('--topic', '-t', metavar='TOPIC', help='文章主题')
    parser.add_argument('--outline', '-o', metavar='OUTLINE', help='大纲内容')
    parser.add_argument('--file', '-f', metavar='FILE', help='从大纲文件读取')
    parser.add_argument('--style', '-s', metavar='STYLE', default='默认', help='写作风格')
    parser.add_argument('--interactive', '-i', action='store_true', help='交互模式')

    args = parser.parse_args()

    # 读取内容
    topic = None
    outline_text = None

    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 第一行是标题，后面是大纲
                lines = content.strip().split('\n')
                topic = lines[0].replace('#', '').strip() if lines else '未命名主题'
                outline_text = '\n'.join(lines[1:]) if len(lines) > 1 else ''
        except Exception as e:
            print(f"{RED}读取文件失败: {e}{RESET}")
            return
    elif args.topic:
        topic = args.topic
        outline_text = args.outline
    elif args.topic is None:
        banner()
        print("请输入文章主题：")
        topic = sys.stdin.readline().strip()
        print("请输入大纲（可选，直接回车跳过）：")
        outline_text = sys.stdin.read()

    if not topic:
        print(f"{RED}主题不能为空{RESET}")
        return

    # 如果没有大纲，生成默认大纲
    if not outline_text or not outline_text.strip():
        outline_text = """## 引言

## 问题引入

## 原因分析

## 解决方案

## 案例展示

## 总结行动

## 总结"""

    # 解析大纲
    sections = parse_outline(outline_text)
    if not sections:
        sections = [{'title': '正文', 'level': 1, 'points': []}]

    # 生成初稿模板
    draft = generate_draft_template(topic, sections, args.style)

    # 输出
    print(format_output(topic, draft, sections))


if __name__ == '__main__':
    main()
