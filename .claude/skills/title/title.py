#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

"""
Title - 公众号标题生成脚本

根据文章主题生成吸引人的标题。

使用方法：
    python title.py "主题"              # 生成默认标题
    python title.py "主题" --style q   # 疑问风格
    python title.py "主题" --style n   # 数字风格
    python title.py "主题" --style s   # 故事风格
    python title.py --interactive       # 交互模式
"""
import os
import sys
import argparse
import random

# 颜色
GREEN = '\033[92m'
BLUE = '\033[94m'
RESET = '\033[0m'


def banner():
    print(f"""
{BLUE}╔═══════════════════════════════════════════════════╗
║        📝 Title - 公众号标题生成                      ║
║           为你的文章生成吸引人的标题                ║
╚═══════════════════════════════════════════════════╝{RESET}
    """)


# 标题模板库
TITLE_TEMPLATES = {
    'default': [
        ('我是怎么用 {topic} 的？', '引发好奇，让人想知道答案'),
        ('{topic} 实战经验分享', '明确价值，实用导向'),
        ('从 0 到 1：我的 {topic} 方法论', '成长故事，体系化'),
        ('一个人就是一个团队：{topic} 实践', '对比强烈，有冲击力'),
        ('你真的会用 {topic} 吗？', '引发思考，激发好奇心'),
        ('{topic} 的 5 个技巧', '数字具体，易于点击'),
        ('关于 {topic}，我想说的话', '真诚分享，有温度'),
        ('{topic} 入门指南', '明确受众，降低门槛'),
        ('为什么 {topic} 很重要？', '引发思考，强调价值'),
        ('{topic} 的正确打开方式', '解决痛点，实用导向')
    ],
    'question': [
        ('{topic} 到底是什么？', '本质探讨'),
        ('{topic} 真的有用吗？', '质疑引发好奇'),
        ('为什么都在说 {topic}？', '从众心理'),
        ('{topic} 适合你吗？', '代入感'),
        ('{topic} 怎么入门？', '实用导向'),
        ('{topic} 难不难？', '消除顾虑'),
        ('{topic} 值不值得学？', '价值评估')
    ],
    'number': [
        ('{topic} 的 3 个核心技巧', '数字具体'),
        ('5 分钟了解 {topic}', '时间量化，降低门槛'),
        ('{topic} 必知的 10 个点', '全面但可执行'),
        ('从 0 到 1 学 {topic}', '成长路径'),
        ('{topic} 入门到精通', '进阶路径'),
        ('{topic} 的 5 大误区', '规避风险'),
        ('3 个 {topic} 案例详解', '案例驱动')
    ],
    'story': [
        ('我是怎么学会 {topic} 的', '亲身经历，有说服力'),
        ('我的 {topic} 进化之路', '成长故事'),
        ('{topic} 给我带来了什么', '现身说法'),
        ('从新手到专家：{topic} 之路', '进阶故事'),
        ('我与 {topic} 的故事', '情感连接'),
        ('{topic} 改变了我的生活', '影响深远')
    ]
}


def generate_titles(topic, style='default', count=5):
    """生成标题"""
    templates = TITLE_TEMPLATES.get(style, TITLE_TEMPLATES['default'])

    # 随机选择
    selected = random.sample(templates, min(count, len(templates)))

    # 格式化
    titles = []
    for template, desc in selected:
        title = template.format(topic=topic)
        titles.append((title, desc))

    return titles


def format_output(titles, topic):
    """格式化输出"""
    output = f"""
{GREEN}📝 标题候选 - 主题：{topic}{RESET}

"""

    for i, (title, desc) in enumerate(titles, 1):
        output += f"### {i}. {title}\n"
        output += f"   特点：{desc}\n\n"

    output += f"""
{BLUE}💡 标题原则{RESET}
1. 引发好奇：让人想点进来
2. 明确价值：让人知道能得到什么
3. 营造氛围：情绪感强
4. 简洁有力：不超过 25 字
"""

    return output


def interactive_mode():
    """交互模式"""
    banner()

    print(f"""
{BLUE}📝 标题生成器{RESET}

请输入文章主题：
""")

    topic = input("> ").strip()

    if not topic:
        print(f"{GREEN}主题不能为空{RESET}")
        return

    print(f"""
选择风格：
1. 默认风格（平衡）
2. 疑问风格（引发好奇）
3. 数字风格（具体量化）
4. 故事风格（亲身经历）
""")

    style_choice = input("选择 [1]: ").strip() or '1'

    style_map = {
        '1': 'default',
        '2': 'question',
        '3': 'number',
        '4': 'story'
    }

    style = style_map.get(style_choice, 'default')
    titles = generate_titles(topic, style)

    print(format_output(titles, topic))


def main():
    parser = argparse.ArgumentParser(description='Title - 公众号标题生成')
    parser.add_argument('topic', nargs='?', help='文章主题')
    parser.add_argument('--style', '-s', choices=['q', 'n', 's', 'default'],
                        help='风格: q=疑问, n=数字, s=故事, default=默认')
    parser.add_argument('--count', '-c', type=int, default=5, help='生成数量')
    parser.add_argument('--interactive', '-i', action='store_true', help='交互模式')

    args = parser.parse_args()

    if args.interactive or not args.topic:
        interactive_mode()
        return

    style_map = {'q': 'question', 'n': 'number', 's': 'story', 'default': 'default'}
    style = style_map.get(args.style, 'default')

    titles = generate_titles(args.topic, style, args.count)
    print(format_output(titles, args.topic))


if __name__ == '__main__':
    main()
