#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

"""
Test Review - 测试用例审查脚本

审查测试用例完整性，识别边界情况和遗漏。

使用方法：
    python test-review.py --file test.js          # 审查测试文件
    python test-review.py --file "*.test.js"      # 批量审查
    python test-review.py --dir tests/            # 审查目录
    python test-review.py --interactive           # 交互模式
"""
import os
import sys
import argparse
import re
from pathlib import Path

# 颜色
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RED = '\033[91m'
RESET = '\033[0m'


def banner():
    print(f"""
{BLUE}╔═══════════════════════════════════════════════════╗
║        🔍 Test Review - 测试用例审查              ║
║           检查测试用例完整性，识别遗漏             ║
╚═══════════════════════════════════════════════════╝{RESET}
    """)


# 常见测试框架特征
TEST_PATTERNS = {
    'describe': r'describe\s*\(',
    'it': r'it\s*\(',
    'test': r'test\s*\(',
    'expect': r'expect\s*\(',
    'assert': r'assert\s*\(',
    'should': r'should\s*\(',
    'describe_each': r'describe\.each\s*\(',
    'before_each': r'beforeEach\s*\(',
    'after_each': r'afterEach\s*\(',
    'before_all': r'beforeAll\s*\(',
    'after_all': r'afterAll\s*\(',
}

# 边界情况关键词
EDGE_CASE_KEYWORDS = [
    'null', 'undefined', 'empty', 'zero', 'negative',
    'max', 'min', 'boundary', 'edge', 'corner',
    'first', 'last', 'single', 'multiple', 'none',
]

# 异常情况关键词
ERROR_CASE_KEYWORDS = [
    'error', 'throw', 'reject', 'catch', 'fail',
    'exception', 'invalid', 'wrong', 'denied', 'timeout',
]


def analyze_test_file(file_path):
    """分析测试文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {'error': str(e)}

    # 统计测试用例数量
    test_count = 0
    describe_count = 0

    for pattern_name, pattern in TEST_PATTERNS.items():
        matches = re.findall(pattern, content)
        if pattern_name in ['describe', 'describe_each']:
            describe_count += len(matches)
        elif pattern_name in ['it', 'test']:
            test_count += len(matches)

    # 检查边界情况覆盖
    edge_cases_found = []
    for keyword in EDGE_CASE_KEYWORDS:
        if keyword in content.lower():
            edge_cases_found.append(keyword)

    # 检查异常情况覆盖
    error_cases_found = []
    for keyword in ERROR_CASE_KEYWORDS:
        if keyword in content.lower():
            error_cases_found.append(keyword)

    # 检查是否有异步测试
    has_async = 'async' in content or 'await' in content

    # 检查是否有 mocking
    has_mocking = 'mock' in content.lower() or 'spy' in content.lower()

    # 检查是否有 beforeEach/afterEach
    has_setup_teardown = 'beforeEach' in content or 'afterEach' in content

    # 提取测试用例名称
    test_names = re.findall(r'(?:it|test)\s*\([\'"`]([^\'"`]+)[\'"`]', content)

    return {
        'file': file_path,
        'test_count': test_count,
        'describe_count': describe_count,
        'edge_cases': edge_cases_found,
        'error_cases': error_cases_found,
        'has_async': has_async,
        'has_mocking': has_mocking,
        'has_setup_teardown': has_setup_teardown,
        'test_names': test_names[:10],  # 只取前10个
        'content_length': len(content)
    }


def calculate_coverage(analysis):
    """计算覆盖率评分"""
    score = {'normal': 0, 'edge': 0, 'error': 0, 'quality': 0}

    # 正常流程评分
    if analysis['test_count'] >= 5:
        score['normal'] = 100
    elif analysis['test_count'] >= 3:
        score['normal'] = 70
    elif analysis['test_count'] >= 1:
        score['normal'] = 40
    else:
        score['normal'] = 0

    # 边界情况评分
    edge_count = len(analysis['edge_cases'])
    if edge_count >= 4:
        score['edge'] = 100
    elif edge_count >= 2:
        score['edge'] = 60
    elif edge_count >= 1:
        score['edge'] = 30
    else:
        score['edge'] = 10

    # 异常情况评分
    error_count = len(analysis['error_cases'])
    if error_count >= 3:
        score['error'] = 100
    elif error_count >= 2:
        score['error'] = 60
    elif error_count >= 1:
        score['error'] = 30
    else:
        score['error'] = 10

    # 测试质量评分
    quality_score = 20
    if analysis['has_mocking']:
        quality_score += 20
    if analysis['has_setup_teardown']:
        quality_score += 20
    if analysis['has_async']:
        quality_score += 20
    if analysis['test_count'] > 0:
        quality_score += 20
    score['quality'] = quality_score

    return score


def generate_report(analysis):
    """生成审查报告"""
    score = calculate_coverage(analysis)

    if 'error' in analysis:
        return f"{RED}分析失败: {analysis['error']}{RESET}"

    report = f"""
{GREEN}╔═══════════════════════════════════════════════════╗
║                   🔍 测试审查报告                    ║
╚═══════════════════════════════════════════════════╝{RESET}

{YELLOW}【文件】{RESET}
{analysis['file']}

{YELLOW}【测试统计】{RESET}
- 测试套件 (describe): {analysis['describe_count']}
- 测试用例 (it/test): {analysis['test_count']}
- 代码行数: {analysis['content_length']}

{GREEN}【覆盖率评分】{RESET}
- 正常流程：{score['normal']}%
- 边界情况：{score['edge']}%
- 异常情况：{score['error']}%
- 测试质量：{score['quality']}%

{YELLOW}【已覆盖的边界情况】{RESET}
"""

    if analysis['edge_cases']:
        for case in analysis['edge_cases']:
            report += f"- {case}\n"
    else:
        report += "⚠️ 未发现边界情况测试\n"

    report += f"""
{YELLOW}【已覆盖的异常情况】{RESET}
"""

    if analysis['error_cases']:
        for case in analysis['error_cases']:
            report += f"- {case}\n"
    else:
        report += "⚠️ 未发现异常情况测试\n"

    report += f"""
{YELLOW}【测试特性】{RESET}
"""

    if analysis['has_async']:
        report += f"- {GREEN}✓{RESET} 异步测试\n"
    else:
        report += f"- {YELLOW}○{RESET} 无异步测试\n"

    if analysis['has_mocking']:
        report += f"- {GREEN}✓{RESET} Mocking\n"
    else:
        report += f"- {YELLOW}○{RESET} 无 Mocking\n"

    if analysis['has_setup_teardown']:
        report += f"- {GREEN}✓{RESET} 前后置处理\n"
    else:
        report += f"- {YELLOW}○{RESET} 无前后置处理\n"

    # 问题和建议
    report += f"""
{YELLOW}【发现问题】{RESET}
"""

    issues = []

    if score['normal'] < 70:
        issues.append(f"测试用例数量偏少，建议增加至少 {5 - analysis['test_count']} 个测试")

    if score['edge'] < 50:
        issues.append("边界情况覆盖不足，建议添加空值、极值等测试")

    if score['error'] < 50:
        issues.append("异常情况覆盖不足，建议添加错误处理测试")

    if not analysis['has_mocking']:
        issues.append("建议使用 Mock 来隔离外部依赖")

    if not analysis['has_async'] and analysis['test_count'] > 3:
        issues.append("如有异步操作，建议添加异步测试")

    if issues:
        for i, issue in enumerate(issues, 1):
            report += f"{i}. {issue}\n"
    else:
        report += "✅ 测试覆盖良好\n"

    # 总体评价
    avg_score = (score['normal'] + score['edge'] + score['error'] + score['quality']) / 4

    if avg_score >= 80:
        evaluation = "优秀"
    elif avg_score >= 60:
        evaluation = "良好"
    elif avg_score >= 40:
        evaluation = "一般"
    else:
        evaluation = "需要改进"

    report += f"""
{GREEN}【总体评价】{RESET}
{evaluation} (综合评分: {avg_score:.0f}%)
"""

    return report


def main():
    parser = argparse.ArgumentParser(description='Test Review - 测试用例审查')
    parser.add_argument('--file', '-f', metavar='FILE', help='测试文件')
    parser.add_argument('--dir', '-d', metavar='DIR', help='测试目录')
    parser.add_argument('--pattern', '-p', metavar='PATTERN', default='*.test.js',
                        help='文件匹配模式')
    parser.add_argument('--interactive', '-i', action='store_true', help='交互模式')

    args = parser.parse_args()

    files_to_check = []

    if args.file:
        if '*' in args.file:
            # 使用 glob 模式
            import glob
            files_to_check = glob.glob(args.file)
        else:
            files_to_check = [args.file]
    elif args.dir:
        import glob
        pattern = os.path.join(args.dir, args.pattern)
        files_to_check = glob.glob(pattern)
    else:
        banner()
        print("请输入要审查的测试文件或目录：")
        path = sys.stdin.readline().strip()
        if os.path.isdir(path):
            args.dir = path
            import glob
            pattern = os.path.join(path, '*.test.js')
            files_to_check = glob.glob(pattern)
        else:
            files_to_check = [path]

    if not files_to_check:
        print(f"{RED}没有找到测试文件{RESET}")
        return

    # 分析每个文件
    for file_path in files_to_check:
        if os.path.isfile(file_path):
            print(generate_report(analyze_test_file(file_path)))


if __name__ == '__main__':
    main()
