#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

"""
Outline - 文章大纲生成脚本

根据主题生成结构化的文章大纲。

使用方法：
    python outline.py "文章主题"              # 命令行
    python outline.py --topic "主题"          # 显式指定主题
    python outline.py --file file.md         # 从文件读取
    python outline.py --interactive          # 交互模式
"""
import os
import sys
import argparse

# 颜色
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RED = '\033[91m'
RESET = '\033[0m'


def banner():
    print(f"""
{BLUE}╔═══════════════════════════════════════════════════╗
║        📝 Outline - 文章大纲生成                   ║
║           根据主题生成结构化的大纲                 ║
╚═══════════════════════════════════════════════════╝{RESET}
    """)


# 文章类型模板
ARTICLE_TEMPLATES = {
    '干货文': {
        'structure': ['问题引入', '原因分析', '解决方案', '案例展示', '总结行动'],
        'focus': '实用性强，提供可直接落地的方法'
    },
    '观点文': {
        'structure': ['现象描述', '观点抛出', '论证1', '论证2', '论证3', '结论'],
        'focus': '观点鲜明，论证有力'
    },
    '故事文': {
        'structure': ['背景', '冲突', '转折', '高潮', '结局', '启示'],
        'focus': '情节生动，有情感共鸣'
    },
    '科普文': {
        'structure': ['概念引入', '原理讲解', '应用场景', '案例说明', '展望'],
        'focus': '通俗易懂，降低理解门槛'
    }
}


def analyze_topic(topic, audience=None, article_type=None):
    """分析主题，生成大纲"""
    # 确定文章类型
    if not article_type:
        # 根据主题自动判断
        if any(kw in topic for kw in ['怎么', '如何', '方法', '技巧', '攻略']):
            article_type = '干货文'
        elif any(kw in topic for kw in ['观点', '看法', '认为', '角度']):
            article_type = '观点文'
        elif any(kw in topic for kw in ['故事', '经历', '历程']):
            article_type = '故事文'
        else:
            article_type = '干货文'

    template = ARTICLE_TEMPLATES.get(article_type, ARTICLE_TEMPLATES['干货文'])

    # 生成大纲
    outline = {
        'title': f"关于{topic}的深度思考",
        'type': article_type,
        'focus': template['focus'],
        'sections': []
    }

    # 引言
    outline['sections'].append({
        'title': '引言',
        'level': 1,
        'content': [
            '引入主题，点明读者能获得什么价值',
            '引发共鸣或好奇'
        ]
    })

    # 正文部分
    structure = template['structure']
    for i, section in enumerate(structure):
        outline['sections'].append({
            'title': section,
            'level': 1,
            'content': [
                f'展开{section}要点',
                '提供案例或数据支撑'
            ]
        })

    # 总结
    outline['sections'].append({
        'title': '总结',
        'level': 1,
        'content': [
            '回顾核心观点',
            '给出行动建议',
            '引发下一步思考'
        ]
    })

    return outline


def format_outline(outline):
    """格式化输出大纲"""
    output = f"""
{GREEN}╔═══════════════════════════════════════════════════╗
║                    📝 大纲生成结果                  ║
╚═══════════════════════════════════════════════════╝{RESET}

{YELLOW}【文章标题】{RESET}
{outline['title']}

{YELLOW}【文章类型】{RESET}
{outline['type']} - {outline['focus']}

{YELLOW}【大纲结构】{RESET}
"""

    for section in outline['sections']:
        if section['level'] == 1:
            output += f"\n## {section['title']}\n"
            for point in section['content']:
                output += f"- {point}\n"

    output += f"""
{GREEN}【使用说明】{RESET}
• 此大纲可直接用于 draft 写初稿
• 可用 polish 精修初稿
• 可用 gzh 排版发布
"""

    return output


def main():
    parser = argparse.ArgumentParser(description='Outline - 文章大纲生成')
    parser.add_argument('topic', nargs='?', help='文章主题')
    parser.add_argument('--topic', '-t', metavar='TOPIC', help='文章主题')
    parser.add_argument('--audience', '-a', metavar='AUDIENCE', help='目标读者')
    parser.add_argument('--type', '-y', metavar='TYPE', help='文章类型：干货文/观点文/故事文/科普文')
    parser.add_argument('--file', '-f', metavar='FILE', help='从文件读取')
    parser.add_argument('--interactive', '-i', action='store_true', help='交互模式')

    args = parser.parse_args()

    # 读取内容
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 从文件第一行提取主题
                topic = content.strip().split('\n')[0].replace('#', '').strip()
        except Exception as e:
            print(f"{RED}读取文件失败: {e}{RESET}")
            return
    elif args.topic:
        topic = args.topic
    elif args.content:
        topic = args.content
    else:
        banner()
        print("请输入文章主题（输入完成后按 Ctrl+D）：")
        topic = sys.stdin.read().strip()

    if not topic:
        print(f"{RED}主题不能为空{RESET}")
        return

    # 生成大纲
    outline = analyze_topic(topic, args.audience, args.type)

    # 输出
    print(format_outline(outline))


if __name__ == '__main__':
    main()
