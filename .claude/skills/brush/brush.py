#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Brush - AI 图片生成脚本

根据描述生成优化的提示词，调用 CogView / SiliconFlow 生图。

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

try:
    import requests
except ImportError:
    requests = None

_requests_post = requests.post if requests else None

# 颜色
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RED = '\033[91m'
RESET = '\033[0m'


def banner():
    print(f"""
{BLUE}╔═══════════════════════════════════════════════════╗
║        Brush - AI 图片生成                        ║
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
    prompt_parts = [description]

    if style in STYLE_PROMPTS:
        prompt_parts.append(STYLE_PROMPTS[style])

    prompt_parts.append(QUALITY_PROMPTS)

    return ', '.join(prompt_parts)


def generate_prompt_variants(description, style='写实'):
    """生成多个提示词变体"""
    variants = []

    detailed = f"{description}, {STYLE_PROMPTS.get(style, '')}, {QUALITY_PROMPTS}, highly detailed"
    variants.append(('详细描述', detailed))

    simple = f"{description}, {STYLE_PROMPTS.get(style, '')}, clean and simple"
    variants.append(('简洁版', simple))

    artistic = f"{description}, {STYLE_PROMPTS.get(style, '')}, artistic, creative, unique"
    variants.append(('艺术版', artistic))

    return variants


def format_output(description, style, size, prompts):
    """格式化输出"""
    output = f"""
{GREEN}╔═══════════════════════════════════════════════════╗
║                   图片提示词生成                    ║
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
1. 将提示词复制到 AI 绘图工具
2. 根据需要调整提示词
3. 生成图片

"""

    return output


def _load_feishu_webhook():
    """从 tell-me/config.json 读取 webhook 地址"""
    config_path = Path(__file__).resolve().parents[1] / 'tell-me' / 'config.json'
    try:
        import json as _json
        data = _json.loads(config_path.read_text(encoding='utf-8'))
        return data.get('webhook')
    except Exception:
        return None


def send_image_to_feishu(title, image_url, color='blue'):
    """用富文本消息（post）发送图片链接到飞书，手机可直接点击查看"""
    if not _requests_post:
        print(f"{RED}缺少 requests 库{RESET}")
        return False

    webhook = _load_feishu_webhook()
    if not webhook:
        print(f"{RED}未找到飞书 webhook 配置{RESET}")
        return False

    payload = {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": f"🎨 {title}",
                    "content": [
                        [
                            {"tag": "text", "text": "点击查看图片："},
                            {"tag": "a", "text": "查看原图", "href": image_url},
                        ]
                    ]
                }
            }
        }
    }

    try:
        resp = _requests_post(webhook, json=payload, timeout=10)
        data = resp.json()
        if data.get('code') == 0 or data.get('StatusCode') == 0:
            print(f"{GREEN}已推送到飞书{RESET}")
            return True
        print(f"{RED}飞书推送失败：{data}{RESET}")
        return False
    except Exception as e:
        print(f"{RED}飞书推送异常：{e}{RESET}")
        return False


# ── 凭据解析 ──


def resolve_zhipu_credentials():
    """解析智谱 API Key"""
    key = os.environ.get('ZHIPU_API_KEY')
    if key:
        return key, 'env_zhipu'
    return None, 'none'


def resolve_siliconflow_credentials():
    """解析 SiliconFlow API Key"""
    key = os.environ.get('SILICONFLOW_API_KEY')
    if key:
        return key, 'env_siliconflow'
    return None, 'none'


# ── 图片生成 ──


def _extract_cogview_image_url(response):
    if response.status_code != 200:
        return None
    data = response.json() or {}
    images = data.get('data') or []
    if not images:
        return None
    return images[0].get('url')


def _extract_siliconflow_image_url(response):
    if response.status_code != 200:
        return None
    data = response.json() or {}
    images = data.get('images') or []
    if not images:
        return None
    return images[0].get('url')


def try_generate_image(prompt):
    """尝试生成图片：CogView 优先 → SiliconFlow 兜底"""
    if not _requests_post:
        return None

    failures = []
    sources = []

    # 1. CogView-3-Flash
    zhipu_key, zhipu_source = resolve_zhipu_credentials()
    if zhipu_key:
        sources.append(zhipu_source)
        try:
            response = _requests_post(
                'https://open.bigmodel.cn/api/paas/v4/images/generations',
                headers={
                    'Authorization': f'Bearer {zhipu_key}',
                    'Content-Type': 'application/json',
                },
                json={
                    'model': 'cogview-3-flash',
                    'prompt': prompt,
                },
                timeout=90,
            )
            url = _extract_cogview_image_url(response)
            if url:
                return url
            error_msg = _safe_error_text(response)
            failures.append(('CogView', response.status_code, error_msg))
        except Exception as e:
            failures.append(('CogView', 0, str(e)))

    # 2. SiliconFlow FLUX
    sf_key, sf_source = resolve_siliconflow_credentials()
    if sf_key:
        sources.append(sf_source)
        try:
            response = _requests_post(
                'https://api.siliconflow.cn/v1/images/generations',
                headers={
                    'Authorization': f'Bearer {sf_key}',
                    'Content-Type': 'application/json',
                },
                json={
                    'model': 'black-forest-labs/FLUX.1-schnell',
                    'prompt': prompt,
                    'image_size': '1024x1024',
                },
                timeout=90,
            )
            url = _extract_siliconflow_image_url(response)
            if url:
                return url
            error_msg = _safe_error_text(response)
            failures.append(('SiliconFlow', response.status_code, error_msg))
        except Exception as e:
            failures.append(('SiliconFlow', 0, str(e)))

    # 全部失败
    if failures or not sources:
        msg = get_generation_error_message(sources, failures)
        print(f"{RED}{msg}{RESET}")

    return None


def _safe_error_text(response):
    try:
        data = response.json()
        err = data.get('error', {})
        if isinstance(err, dict):
            return err.get('message', response.text[:200])
        return str(err) or response.text[:200]
    except Exception:
        return response.text[:200]


def get_generation_error_message(sources, failures):
    """生成明确的错误提示信息"""
    if not sources and not failures:
        return (
            "未配置任何图片生成 API Key。请设置环境变量：\n"
            "  - ZHIPU_API_KEY（智谱 CogView，免费）\n"
            "  - SILICONFLOW_API_KEY（SiliconFlow FLUX）"
        )

    lines = ["图片生成失败："]
    for name, status, msg in failures:
        lines.append(f"  - {name}: HTTP {status} - {msg}")
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Brush - AI 图片生成')
    parser.add_argument('description', nargs='?', help='图片描述')
    parser.add_argument('--desc', '-d', metavar='DESC', help='图片描述')
    parser.add_argument('--style', '-s', metavar='STYLE',
                        default='写实', choices=list(STYLE_PROMPTS.keys()),
                        help='风格：写实/插画/漫画/极简/抽象/水彩/油画')
    parser.add_argument('--size', '-z', metavar='SIZE', default='16:9',
                        help='尺寸：16:9, 4:3, 1:1, 9:16')
    parser.add_argument('--image-url', metavar='URL', help='已有图片 URL（无需 API 生成）')
    parser.add_argument('--send-feishu', action='store_true', help='生成成功后自动推送到飞书')
    parser.add_argument('--title', metavar='TITLE', default='AI 生成图片', help='飞书卡片标题')
    parser.add_argument('--color', metavar='COLOR', default='blue', help='飞书卡片颜色（blue/green/orange/red）')
    parser.add_argument('--interactive', '-i', action='store_true', help='交互模式')

    args = parser.parse_args()

    # 直接使用已有图片 URL
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
    print(format_output(description, args.style, args.size, [('主提示词', main_prompt)] + variants))

    # 尝试生成图片
    image_url = try_generate_image(main_prompt)
    if image_url:
        print(f"{GREEN}【生成图片链接】{RESET}\n{image_url}\n")

        if args.send_feishu:
            send_image_to_feishu(args.title, image_url, args.color)


if __name__ == '__main__':
    main()
