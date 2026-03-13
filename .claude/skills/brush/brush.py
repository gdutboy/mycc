#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

"""
Brush - AI 图片生成脚本

根据描述生成优化的提示词，指导 AI 绘图。

使用方法：
    python brush.py "图片描述"              # 命令行
    python brush.py --desc "描述" --style 插画  # 指定风格
    python brush.py --interactive           # 交互模式
"""
import os
import sys
import argparse
import subprocess
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
║        🎨 Brush - AI 图片生成                     ║
║           根据描述生成优化的提示词                 ║
╚═══════════════════════════════════════════════════╝{RESET}
    """)


# 风格提示词模板
STYLE_PROMPTS = {
    '写实': 'photorealistic, high detail, 8k, professional photography, natural lighting',
    '插画': 'illustration, flat design, vector art, clean lines, vibrant colors',
    '漫画': 'comic style, manga, anime, bold outlines, expressive characters',
    '极简': 'minimalist, simple, clean, line art, monochrome',
    '抽象': 'abstract art, artistic, colorful, geometric shapes, modern',
    '水彩': 'watercolor painting, soft colors, artistic, delicate',
    '油画': 'oil painting, classical, rich colors, textured, masterpiece'
}

# 质量提示词
QUALITY_PROMPTS = 'high quality, best quality, detailed, masterpiece'


def optimize_prompt(description, style='写实', size='16:9', aspect_ratio=None):
    """优化提示词"""
    # 基础提示词
    prompt_parts = [description]

    # 添加风格
    if style in STYLE_PROMPTS:
        prompt_parts.append(STYLE_PROMPTS[style])

    # 添加质量
    prompt_parts.append(QUALITY_PROMPTS)

    # 添加尺寸
    if aspect_ratio:
        prompt = ', '.join(prompt_parts)
    else:
        prompt = ', '.join(prompt_parts)

    # 英文提示词（大多数 AI 绘图支持英文效果更好）
    return prompt


def generate_prompt_variants(description, style='写实'):
    """生成多个提示词变体"""
    variants = []

    # 变体1: 详细描述
    detailed = f"{description}, {STYLE_PROMPTS.get(style, '')}, {QUALITY_PROMPTS}, highly detailed"
    variants.append(('详细描述', detailed))

    # 变体2: 简洁版
    simple = f"{description}, {STYLE_PROMPTS.get(style, '')}, clean and simple"
    variants.append(('简洁版', simple))

    # 变体3: 艺术版
    artistic = f"{description}, {STYLE_PROMPTS.get(style, '')}, artistic, creative, unique"
    variants.append(('艺术版', artistic))

    return variants


def format_output(description, style, size, prompts):
    """格式化输出"""
    output = f"""
{GREEN}╔═══════════════════════════════════════════════════╗
║                   🎨 图片提示词生成                   ║
╚═══════════════════════════════════════════════════╝{RESET}

{YELLOW}【图片描述】{RESET}
{description}

{YELLOW}【选择风格】{RESET}
{style}

{YELLOW}【输出尺寸】{RESET}
{size}

{GREEN}【优化的提示词】{RESET}
{prompts[0][1]}

{YELLOW}【提示词变体】{RESET}
"""

    for name, prompt in prompts[1:]:
        output += f"\n### {name}\n{prompt}\n"

    output += f"""
{GREEN}【使用说明】{RESET}
1. 将提示词复制到 AI 绘图工具（如 Midjourney、DALL-E、Stable Diffusion）
2. 根据需要调整提示词
3. 生成图片

{YELLOW}【推荐工具】{RESET}
• Midjourney: /imagine prompt: <提示词>
• DALL-E: 直接在 ChatGPT Plus 中使用
• Stable Diffusion: 本地部署或在线平台
• Leonardo.ai: 免费额度，提示词优化

"""

    return output


def send_image_to_feishu(title, image_url, color='blue'):
    """调用 tell-me/send.js 发送图片 URL 到飞书"""
    script_path = Path(__file__).resolve().parents[1] / 'tell-me' / 'send.js'

    if not script_path.exists():
        print(f"{RED}未找到 send.js：{script_path}{RESET}")
        return False

    cmd = [
        'node',
        str(script_path),
        '--image-url',
        title,
        image_url,
        color,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"{GREEN}✅ 已推送到飞书{RESET}")
        return True

    print(f"{RED}❌ 飞书推送失败：{(result.stderr or result.stdout).strip()}{RESET}")
    return False


def try_generate_image(prompt, api_key=None):
    """尝试调用 API 生成图片（如果配置了）"""
    # 这里可以集成各种 AI 绘图 API
    # 目前返回提示词，由用户手动生成

    # 尝试调用 DALL-E API（如果安装了 openai）
    if api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)

            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1792x1024",
                quality="standard",
                n=1,
            )

            return response.data[0].url
        except ImportError:
            return None
        except Exception as e:
            return None

    return None


def main():
    parser = argparse.ArgumentParser(description='Brush - AI 图片生成')
    parser.add_argument('description', nargs='?', help='图片描述')
    parser.add_argument('--desc', '-d', metavar='DESC', help='图片描述')
    parser.add_argument('--style', '-s', metavar='STYLE',
                        default='写实', choices=list(STYLE_PROMPTS.keys()),
                        help='风格：写实/插画/漫画/极简/抽象/水彩/油画')
    parser.add_argument('--size', '-z', metavar='SIZE', default='16:9',
                        help='尺寸：16:9, 4:3, 1:1, 9:16')
    parser.add_argument('--api-key', '-k', metavar='KEY', help='OpenAI API Key（可选）')
    parser.add_argument('--image-url', metavar='URL', help='已有图片 URL（无需 API 生成）')
    parser.add_argument('--send-feishu', action='store_true', help='生成成功后自动推送到飞书')
    parser.add_argument('--title', metavar='TITLE', default='AI 生成图片', help='飞书卡片标题')
    parser.add_argument('--color', metavar='COLOR', default='blue', help='飞书卡片颜色（blue/green/orange/red）')
    parser.add_argument('--interactive', '-i', action='store_true', help='交互模式')

    args = parser.parse_args()

    # 直接使用已有图片 URL（无需 API key）
    if args.image_url:
        print(f"{GREEN}【图片链接】{RESET}\n{args.image_url}\n")
        if args.send_feishu:
            send_image_to_feishu(args.title, args.image_url, args.color)
        return

    # 读取描述
    if args.description:
        description = args.description
    elif args.desc:
        description = args.desc
    else:
        banner()
        print("请描述要生成的图片内容：")
        description = sys.stdin.read().strip()

    if not description:
        print(f"{RED}图片描述不能为空{RESET}")
        return

    # 优化提示词
    main_prompt = optimize_prompt(description, args.style, args.size)

    # 生成变体
    variants = generate_prompt_variants(description, args.style)

    # 输出提示词
    print(format_output(description, args.style, args.size, [( '主提示词', main_prompt)] + variants))

    # 尝试生成图片
    image_url = try_generate_image(main_prompt, args.api_key)
    if image_url:
        print(f"{GREEN}【生成图片链接】{RESET}\n{image_url}\n")

        if args.send_feishu:
            send_image_to_feishu(args.title, image_url, args.color)
    else:
        if args.send_feishu:
            print(f"{YELLOW}未生成图片：请传入可用 --api-key 后再开启 --send-feishu{RESET}")


if __name__ == '__main__':
    main()
