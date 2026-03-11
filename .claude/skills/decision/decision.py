#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

"""
Decision - 决策记录脚本

自动记录技术选型、架构变更等决策。

使用方法：
    python decision.py --init           # 初始化决策记录
    python decision.py --add "标题"   # 添加决策
    python decision.py --list          # 列出最近决策
    python decision.py --check "关键词" # 检查是否有相关决策
"""
import os
import sys
import argparse
from datetime import datetime

# 颜色
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RED = '\033[91m'
RESET = '\033[0m'


def banner():
    print(f"""
{BLUE}╔═══════════════════════════════════════════════════╗
║        📝 Decision - 决策记录                    ║
║      记录"放弃了什么"，比"选了什么"更重要        ║
╚═══════════════════════════════════════════════════╝{RESET}
    """)


# 决策类型
DECISION_TYPES = {
    'fix': {'name': 'Bug 修复', 'desc': '发现 bug → 排查 → 定位根因 → 修复'},
    'arch': {'name': '架构变更', 'desc': '重构、模块拆分、技术栈迁移'},
    'api': {'name': 'API/接口', 'desc': '接口设计、协议变更、数据格式调整'},
    'config': {'name': '配置/运维', 'desc': '服务器配置、部署方式、环境变量'},
    'design': {'name': '产品设计', 'desc': 'UI/UX 决策、功能取舍、交互模式'},
    'auto': {'name': 'CC 自闭环', 'desc': 'CC 自主决策闭环'}
}


def generate_decision(title, decision_type, background, candidates, decision_reason, alternatives, files, conditions):
    """生成决策记录模板"""
    date = datetime.now().strftime('%Y-%m-%d')

    template = f"""## {title}（{date}）

<!-- type: {decision_type} -->
<!-- status: 生效中 -->

### 现象
{background}

### 候选方案
| 方案 | 做法 | 优点 | 缺点 |
|------|------|------|------|
"""

    for c in candidates:
        template += f"| {c['name']} | {c.get('做法', '-')} | {c.get('优点', '-')} | {c.get('缺点', '-')} |\n"

    template += f"""
### 决策
**选择**：{candidates[0]['name'] if candidates else '待填写'}
**理由**：{decision_reason}
**放弃的方案**：{alternatives}

### 改动
"""
    for f in files:
        template += f"- {f}\n"

    template += f"""
### 什么条件下该翻
"""
    for cond in conditions:
        template += f"- {cond}\n"

    return template


def interactive_add():
    """交互式添加决策"""
    banner()

    print(f"""
{GREEN}📝 添加新决策{RESET}

请按提示填写决策信息：
""")

    # 1. 标题
    title = input("决策标题：").strip()
    if not title:
        print(f"{RED}标题不能为空{RESET}")
        return

    # 2. 类型
    print(f"\n决策类型：")
    for key, info in DECISION_TYPES.items():
        print(f"  {key}: {info['name']} - {info['desc']}")

    decision_type = input("选择类型 [fix]: ").strip() or 'fix'
    if decision_type not in DECISION_TYPES:
        decision_type = 'fix'

    # 3. 背景
    print(f"\n{GREEN}### 现象{RESET}")
    print("（描述遇到了什么问题）")
    background = input("> ").strip()

    # 4. 候选方案
    print(f"\n{GREEN}### 候选方案{RESET}")
    print("（按回车添加方案，完成后直接回车）")
    candidates = []
    while True:
        name = input("方案名称（直接回车结束）: ").strip()
        if not name:
            break
        pros = input("优点: ").strip()
        cons = input("缺点: ").strip()
        candidates.append({'name': name, '优点': pros, '缺点': cons})

    # 5. 决策
    decision_reason = input("\n决策理由: ").strip()
    alternatives = input("放弃的方案（为什么放弃）: ").strip()

    # 6. 改动文件
    print(f"\n{GREEN}### 改动文件{RESET}")
    print("（直接回车结束）")
    files = []
    while True:
        f = input("文件路径: ").strip()
        if not f:
            break
        files.append(f)

    # 7. 翻转条件
    print(f"\n{GREEN}### 什么条件下该翻{RESET}")
    print("（直接回车结束）")
    conditions = []
    while True:
        c = input("条件: ").strip()
        if not c:
            break
        conditions.append(c)

    # 生成
    result = generate_decision(
        title, decision_type, background,
        candidates, decision_reason, alternatives,
        files, conditions
    )

    print(f"""
{BLUE}═══════════════════════════════════════════════════{RESET}

{GREEN}生成的决策记录：{RESET}

{result}

{BLUE}═══════════════════════════════════════════════════{RESET}

请将以上内容复制到项目的 04-决策记录.md 文件末尾。
""")

    return result


def show_recent_decisions():
    """显示最近的决策"""
    print(f"""
{BLUE}📋 最近的决策记录{RESET}

请在项目的 04-决策记录.md 文件中查看。
""")


def check_decision(keyword):
    """检查是否有相关决策"""
    print(f"""
{YELLOW}🔍 检查关键词: {keyword}{RESET}

请在项目的 04-决策记录.md 文件中搜索。
""")


def main():
    parser = argparse.ArgumentParser(description='Decision - 决策记录')
    parser.add_argument('--add', metavar='TITLE', help='添加新决策')
    parser.add_argument('--init', action='store_true', help='初始化决策记录模板')
    parser.add_argument('--list', action='store_true', help='列出最近决策')
    parser.add_argument('--check', metavar='KEYWORD', help='检查关键词')

    args = parser.parse_args()

    if args.add:
        interactive_add()
    elif args.init:
        print("""
## 决策记录模板

### 使用说明

1. 每次技术选型或架构变更后，运行此脚本
2. 按提示填写决策信息
3. 将生成的记录追加到 04-决策记录.md

### 决策类型

| 类型 | 场景 |
|------|------|
| fix | Bug 修复 |
| arch | 架构变更 |
| api | API 变更 |
| config | 配置变更 |
| design | 产品设计 |
| auto | CC 自闭环 |
""")
    elif args.list:
        show_recent_decisions()
    elif args.check:
        check_decision(args.check)
    else:
        banner()
        interactive_add()


if __name__ == '__main__':
    main()
