#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

"""
Create System - 创作系统路由脚本

根据任务类型自动路由到对应的创作技能。

使用方法：
    python create-system.py --title "主题"         # 生成标题
    python create-system.py --outline "主题"      # 生成大纲
    python create-system.py --draft "主题"        # 写初稿
    python create-system.py --polish "文章内容"   # 精修文章
    python create-system.py --gzh "文章内容"       # 公众号排版
    python create-system.py --full "主题"         # 完整流程
"""
import os
import sys
import argparse

# 颜色
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def banner():
    print(f"""
{BLUE}╔═══════════════════════════════════════════════════╗
║        🎨 Create System - 创作系统路由             ║
║           根据任务类型自动路由到对应技能            ║
╚═══════════════════════════════════════════════════╝{RESET}
    """)


# 技能映射
SKILLS = {
    'title': {
        'name': '标题生成',
        'file': 'title/SKILL.md',
        'keywords': ['标题', 'title', '起名']
    },
    'outline': {
        'name': '大纲生成',
        'file': 'outline/SKILL.md',
        'keywords': ['大纲', 'outline', '提纲']
    },
    'draft': {
        'name': '初稿写作',
        'file': 'draft/SKILL.md',
        'keywords': ['写', '文章', 'draft', '创作']
    },
    'polish': {
        'name': '文章精修',
        'file': 'polish/SKILL.md',
        'keywords': ['精修', 'polish', '打磨', '润色']
    },
    'gzh': {
        'name': '公众号排版',
        'file': 'gzh/SKILL.md',
        'keywords': ['排版', 'gzh', '渲染']
    },
    'brush': {
        'name': '图片生成',
        'file': 'brush/SKILL.md',
        'keywords': ['图', '画', '配图']
    }
}


def detect_task_type(input_text):
    """检测任务类型"""
    for skill_type, info in SKILLS.items():
        for keyword in info['keywords']:
            if keyword in input_text:
                return skill_type
    return 'draft'  # 默认


def get_skill(skill_type):
    """获取技能信息"""
    return SKILLS.get(skill_type, SKILLS['draft'])


def run_title(topic):
    """生成标题"""
    print(f"""
{GREEN}📝 生成标题{RESET}

主题：{topic}

加载 title 技能...

请在对话中使用：
> 帮我起一个关于 "{topic}" 的标题
""")


def run_outline(topic):
    """生成大纲"""
    print(f"""
{GREEN}📋 生成大纲{RESET}

主题：{topic}

加载 outline 技能...

请在对话中使用：
> 帮我写一个关于 "{topic}" 的大纲
""")


def run_draft(topic):
    """写初稿"""
    print(f"""
{GREEN}✍️ 写初稿{RESET}

主题：{topic}

加载 draft 技能...

请在对话中使用：
> 帮我写一篇关于 "{topic}" 的文章
""")


def run_polish(content):
    """精修文章"""
    print(f"""
{GREEN}✨ 文章精修{RESET}

加载 polish 技能...

请在对话中使用：
> 帮我精修以下文章：
> {content[:100]}...
""")


def run_gzh(content):
    """公众号排版"""
    print(f"""
{GREEN}📱 公众号排版{RESET}

加载 gzh 技能...

请在对话中使用：
> 帮我排版以下文章：
> {content[:100]}...
""")


def run_full(topic):
    """完整流程"""
    print(f"""
{BLUE}🚀 启动完整创作流程{RESET}

主题：{topic}

流程：标题 → 大纲 → 初稿 → 精修 → 排版

{BLUE}═══════════════════════════════════════════════════{RESET}

Step 1: 生成标题
> 帮我起 5 个关于 "{topic}" 的文章标题

Step 2: 生成大纲
> 帮我根据选定的标题写一个详细大纲

Step 3: 写初稿
> 帮我根据大纲写一篇完整的文章

Step 4: 精修文章
> 帮我精修这篇文章，使其更流畅有说服力

Step 5: 公众号排版
> 帮我把这篇文章排版成公众号格式
""")


def interactive_mode():
    """交互模式"""
    banner()

    print(f"""
{BLUE}🎨 创作系统{RESET}

请告诉我你想做什么：
1. 起标题
2. 写大纲
3. 写文章
4. 精修
5. 排版
6. 完整流程（全部）

输入选项或直接描述你的需求：
""")

    choice = input("> ")

    if choice in ['1', '标题']:
        topic = input("文章主题：")
        run_title(topic)
    elif choice in ['2', '大纲']:
        topic = input("文章主题：")
        run_outline(topic)
    elif choice in ['3', '写', '文章']:
        topic = input("文章主题：")
        run_draft(topic)
    elif choice in ['4', '精修']:
        content = input("文章内容（或粘贴）：")
        run_polish(content)
    elif choice in ['5', '排版']:
        content = input("文章内容（或粘贴）：")
        run_gzh(content)
    elif choice in ['6', '全部', '完整']:
        topic = input("文章主题：")
        run_full(topic)
    else:
        # 智能检测
        skill_type = detect_task_type(choice)
        skill = get_skill(skill_type)
        print(f"\n{GREEN}检测到你可能需要：{skill['name']}{RESET}")
        print(f"请在对话中触发 skill：{skill_type}")


def main():
    parser = argparse.ArgumentParser(description='Create System - 创作系统路由')
    parser.add_argument('--title', metavar='TOPIC', help='生成标题')
    parser.add_argument('--outline', metavar='TOPIC', help='生成大纲')
    parser.add_argument('--draft', metavar='TOPIC', help='写初稿')
    parser.add_argument('--polish', metavar='CONTENT', help='精修文章')
    parser.add_argument('--gzh', metavar='CONTENT', help='公众号排版')
    parser.add_argument('--full', metavar='TOPIC', help='完整流程')
    parser.add_argument('--interactive', '-i', action='store_true', help='交互模式')

    args = parser.parse_args()

    if args.interactive or not any(vars(args).values()):
        interactive_mode()
    elif args.title:
        run_title(args.title)
    elif args.outline:
        run_outline(args.outline)
    elif args.draft:
        run_draft(args.draft)
    elif args.polish:
        run_polish(args.polish)
    elif args.gzh:
        run_gzh(args.gzh)
    elif args.full:
        run_full(args.full)


if __name__ == '__main__':
    main()
