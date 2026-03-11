#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

"""
Polish - 文章精修脚本

打磨文章语言，提升可读性和说服力。

使用方法：
    python polish.py "文章内容"           # 命令行
    python polish.py --file file.md     # 从文件读取
    python polish.py --interactive       # 交互模式
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
║        ✨ Polish - 文章精修                       ║
║           打磨文章语言，提升可读性和说服力         ║
╚═══════════════════════════════════════════════════╝{RESET}
    """)


# 常见冗余表达
REDUNDANT_PATTERNS = [
    (r'这个这个', '这个'),
    (r'那个那个', '那个'),
    (r'然后呢然后呢', '然后'),
    (r'其实呢其实呢', '其实'),
    (r'就是', ''),
    (r'的那个', '的'),
]


def check_redundant(text):
    """检查冗余表达"""
    issues = []
    for pattern, fix in REDUNDANT_PATTERNS:
        if re.search(pattern, text):
            issues.append(f"发现冗余: '{pattern}' -> '{fix}'")
    return issues


def check_sentence_structure(text):
    """检查句式结构"""
    issues = []

    # 检查过长句子
    sentences = re.split(r'[。！？]', text)
    for i, s in enumerate(sentences):
        if len(s) > 50:
            issues.append(f"第{i+1}句过长，建议拆分")

    return issues


def check_transitions(text):
    """检查过渡词"""
    transitions = {
        '首先': '✅ 有过渡',
        '然后': '✅ 有过渡',
        '最后': '✅ 有过渡',
        '第一': '✅ 有过渡',
        '第二': '✅ 有过渡',
        '第三': '✅ 有过渡'
    }

    found = []
    for word, status in transitions.items():
        if word in text:
            found.append(f"{word}: {status}")

    if not found:
        return ["⚠️ 建议添加过渡词：首先、然后、最后"]

    return found


def check_logic_chain(text):
    """检查逻辑链"""
    issues = []

    # 检查因果关系
    if '因为' in text and '所以' not in text:
        issues.append("⚠️ 有'因为'但缺少'所以'")
    if '所以' in text and '因为' not in text:
        issues.append("⚠️ 有'所以'但缺少'因为'")

    return issues


def check_memory_points(text):
    """检查记忆点"""
    points = []

    # 数字列表
    if re.search(r'\d+[、.]\s*\S+', text):
        points.append("✅ 有数字列表")

    # 总结句
    if '总之' in text or '总的来说' in text:
        points.append("✅ 有总结")

    return points if points else ["⚠️ 建议添加记忆点"]


def polish_article(text):
    """精修文章"""
    changes = {
        'redundant': [],
        'structure': [],
        'transitions': [],
        'logic': [],
        'memory': []
    }

    # 1. 去除冗余
    polished = text
    for pattern, fix in REDUNDANT_PATTERNS:
        if re.search(pattern, polished):
            changes['redundant'].append(f"去除冗余: '{pattern}' -> '{fix}'")
            polished = re.sub(pattern, fix, polished)

    # 2. 检查句式
    changes['structure'] = check_sentence_structure(text)

    # 3. 检查过渡词
    changes['transitions'] = check_transitions(text)

    # 4. 检查逻辑
    changes['logic'] = check_logic_chain(text)

    # 5. 检查记忆点
    changes['memory'] = check_memory_points(text)

    return polished, changes


def format_output(original, polished, changes):
    """格式化输出"""
    output = f"""
{GREEN}╔═══════════════════════════════════════════════════╗
║                    ✨ 精修结果                      ║
╚═══════════════════════════════════════════════════╝{RESET}

{GREEN}【精修后的文章】{RESET}

{polished}

{GREEN}【修改说明】{RESET}
"""

    if changes['redundant']:
        output += f"""
{YELLOW}1. 去除冗余{RESET}"""
        for c in changes['redundant']:
            output += f"\n   • {c}"

    if changes['structure']:
        output += f"""
{YELLOW}2. 句式优化{RESET}"""
        for c in changes['structure']:
            output += f"\n   • {c}"

    if changes['transitions']:
        output += f"""
{YELLOW}3. 过渡检查{RESET}"""
        for c in changes['transitions']:
            output += f"\n   • {c}"

    if changes['logic']:
        output += f"""
{YELLOW}4. 逻辑检查{RESET}"""
        for c in changes['logic']:
            output += f"\n   • {c}"

    if changes['memory']:
        output += f"""
{YELLOW}5. 记忆点{RESET}"""
        for c in changes['memory']:
            output += f"\n   • {c}"

    output += f"""

{GREEN}【精修原则】{RESET}
• 保持作者原意
• 不要过度华丽
• 实用为主
"""

    return output


def main():
    parser = argparse.ArgumentParser(description='Polish - 文章精修')
    parser.add_argument('content', nargs='?', help='文章内容')
    parser.add_argument('--file', '-f', metavar='FILE', help='从文件读取')
    parser.add_argument('--interactive', '-i', action='store_true', help='交互模式')

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
        print("请输入需要精修的文章（输入完成后按 Ctrl+D）：")
        content = sys.stdin.read()

    if not content.strip():
        print(f"{RED}内容不能为空{RESET}")
        return

    # 精修
    polished, changes = polish_article(content)

    # 输出
    print(format_output(content, polished, changes))


if __name__ == '__main__':
    main()
