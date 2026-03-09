#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
wechat-autochat.py — 微信自动聊天（监听+自动回复）
用法: python wechat-autochat.py
Ctrl+C 中断
"""
import sys
import os
import time
import asyncio
import hashlib
import subprocess
import tempfile
import re

LOGFILE = os.path.join(tempfile.gettempdir(), "wechat-autochat.log")

def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    with open(LOGFILE, 'a', encoding='utf-8-sig') as f:
        f.write(line + '\n')
    try:
        sys.stdout.buffer.write((line + '\n').encode('utf-8'))
        sys.stdout.buffer.flush()
    except Exception:
        pass

import pyautogui
import pygetwindow as gw
from PIL import ImageEnhance

try:
    import winocr
except ImportError:
    print("[error] winocr 未安装: pip install winocr")
    sys.exit(1)

SIDEBAR = int(os.environ.get("WECHAT_SIDEBAR", 320))
TITLE_H = int(os.environ.get("WECHAT_TITLE_H", 60))
INPUT_H = int(os.environ.get("WECHAT_INPUT_H", 160))
POLL = 5
COOLDOWN = 10  # 发送后冷却秒数，防止死循环

CLAUDE_CMD = os.path.expandvars(r"%APPDATA%\npm\claude.cmd")

# 终端干扰文字过滤（OCR 可能读到 Claude Code 终端内容）
NOISE_PATTERNS = [
    r'autochat', r'2>&1', r'Claude\s*Code', r'Bash\(', r'Running',
    r'stopped', r'Noodling', r'Pontificat', r'output', r'\.py[l\]]',
    r'nage\)', r'esc\s+to', r'interrupt', r'ctrl\+',
]
NOISE_RE = re.compile('|'.join(NOISE_PATTERNS), re.IGNORECASE)


def find_wechat_window():
    for w in gw.getAllWindows():
        if w.title == "微信" and w.width > 400:
            return w
    return None


def is_noise(text):
    """判断是否是终端干扰文字"""
    if NOISE_RE.search(text):
        return True
    # 纯数字或太短的噪声
    if len(text) <= 1 and not any('\u4e00' <= c <= '\u9fff' for c in text):
        return True
    return False


async def read_chat():
    """读取聊天内容，返回带角色标记的对话列表。
    每条格式: '对方: xxx' 或 '我: xxx'
    """
    win = find_wechat_window()
    if not win:
        return None

    try:
        win.activate()
    except Exception:
        pass
    time.sleep(0.3)

    x = win.left + SIDEBAR
    y = win.top + TITLE_H
    w = win.width - SIDEBAR
    h = win.height - TITLE_H - INPUT_H

    if w <= 0 or h <= 0:
        return None

    img = pyautogui.screenshot(region=(x, y, w, h))
    img = ImageEnhance.Contrast(img).enhance(2.0)

    result = await winocr.recognize_pil(img, 'zh-Hans-CN')
    mid_x = w / 2
    lines = []
    for line in result.lines:
        text = line.text.replace(' ', '')
        if not text or is_noise(text):
            continue
        # 用 word 的位置判断左（对方）还是右（自己）
        words = list(line.words)
        if not words:
            continue
        first_r = words[0].bounding_rect
        last_r = words[-1].bounding_rect
        line_center = (first_r.x + last_r.x + last_r.width) / 2
        role = '对方' if line_center < mid_x * 0.85 else '我'
        # 过滤时间戳和系统消息（撤回等）
        if re.match(r'^\d{1,2}[：:]\d{2}$', text):
            continue
        if '撤回' in text or '重新编辑' in text:
            continue
        lines.append(f'{role}: {text}')
    return lines


def copy_to_clipboard(text):
    tmp = os.path.join(tempfile.gettempdir(), "wechat_clip.txt")
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(text)
    subprocess.run(
        ['powershell', '-command',
         f'Get-Content -Path "{tmp}" -Encoding UTF8 -Raw | Set-Clipboard'],
        capture_output=True
    )


def send_message(message):
    win = find_wechat_window()
    if not win:
        return False
    try:
        win.activate()
    except Exception:
        pass
    time.sleep(0.3)

    copy_to_clipboard(message)
    time.sleep(0.1)

    input_x = win.left + SIDEBAR + (win.width - SIDEBAR) // 2
    input_y = win.top + win.height - 50
    pyautogui.click(input_x, input_y)
    time.sleep(0.2)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.2)
    pyautogui.press('enter')
    return True


def generate_reply(chat_lines, sent_history=None):
    """用 Claude 生成回复"""
    chat_text = '\n'.join(chat_lines)
    sent_info = ""
    if sent_history:
        sent_info = f"\n你之前说过的话（不要重复）：\n" + '\n'.join(f"- {s}" for s in sent_history[-5:]) + "\n"
    prompt = f"""你正在微信里和朋友聊天。下面是聊天记录，"对方"是朋友说的，"我"是你说的。
请根据对方最新的消息，回复一条自然的消息。

要求：
- 直接输出回复内容，不加引号、不解释、不加"我:"前缀
- 简短自然，像朋友间聊天（一两句话）
- 针对对方最新说的内容来回应
- 文字可能有 OCR 错别字，理解意思即可
- 你不是AI，不要提及AI、助手、Claude、命令、截图等概念
{sent_info}
聊天记录：
{chat_text}

回复："""

    try:
        env = os.environ.copy()
        for key in list(env.keys()):
            if 'CLAUDE' in key.upper():
                del env[key]
        result = subprocess.run(
            [CLAUDE_CMD, '-p', prompt, '--model', 'haiku'],
            capture_output=True, text=True, timeout=30,
            encoding='utf-8', env=env,
            cwd=tempfile.gettempdir()  # 用临时目录避免加载项目 CLAUDE.md
        )
        reply = result.stdout.strip()
        if reply:
            reply = reply.strip('"').strip("'").strip('\u201c').strip('\u201d')
            return reply
    except Exception as e:
        log(f"[autochat] Claude 调用失败: {e}")
    return None


def md5(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def char_overlap_ratio(a, b):
    """计算两个字符串的字符重叠率（用于模糊匹配 OCR 错字）"""
    if not a or not b:
        return 0
    set_a = set(a)
    set_b = set(b)
    overlap = set_a & set_b
    return len(overlap) / min(len(set_a), len(set_b))


def is_my_message(line, sent_history):
    """判断某行是否是自己发送的消息（OCR 模糊匹配）"""
    clean_line = line.replace(' ', '')
    if len(clean_line) < 3:
        return False
    for sent in sent_history:
        clean_sent = sent.replace(' ', '')
        # 方法1：子串匹配
        if clean_line in clean_sent or clean_sent in clean_line:
            return True
        # 方法2：字符重叠率 > 60%（应对 OCR 错字）
        # 只在长度相近时比较（避免短行误匹配长句）
        len_ratio = len(clean_line) / len(clean_sent) if clean_sent else 0
        if 0.3 < len_ratio < 3.0 and char_overlap_ratio(clean_line, clean_sent) > 0.6:
            return True
    return False


def extract_other_messages(lines):
    """提取对方的消息（以'对方:'开头的行）"""
    return [line for line in lines if line.startswith('对方:')]


async def main():
    log("[autochat] 启动微信自动聊天")
    log(f"[autochat] 轮询: {POLL}s / 冷却: {COOLDOWN}s")
    log("[autochat] Ctrl+C 退出")

    last_hash = ""
    warmup = True
    last_send_time = 0
    sent_history = []  # 记录自己发过的消息
    last_other_hash = ""  # 对方消息的 hash，避免对方没说新话就重复回

    while True:
        try:
            lines = await read_chat()
            if not lines:
                time.sleep(POLL)
                continue

            content = '\n'.join(lines)
            current_hash = md5(content)

            if current_hash != last_hash:
                log(f"内容变化: {' | '.join(lines[-3:])}")  # 只打最后3行

                if warmup:
                    log("[autochat] 预热完成")
                    warmup = False
                    last_hash = current_hash
                    time.sleep(POLL)
                    continue

                # 冷却检查：防止自己发的消息触发新一轮
                elapsed = time.time() - last_send_time
                if elapsed < COOLDOWN:
                    log(f"[autochat] 冷却中({int(COOLDOWN - elapsed)}s)，跳过")
                    last_hash = current_hash
                    time.sleep(POLL)
                    continue

                # 只看对方说了什么
                other_lines = extract_other_messages(lines)
                other_hash = md5('\n'.join(other_lines)) if other_lines else ""

                if not other_lines or other_hash == last_other_hash:
                    log(f"[autochat] 对方无新消息，跳过")
                    last_hash = current_hash
                    time.sleep(POLL)
                    continue

                log(f"[autochat] 对方消息: {' | '.join(other_lines[-3:])}")
                log("[autochat] 生成回复...")
                reply = generate_reply(lines, sent_history)
                if reply:
                    log(f"[autochat] 回复: {reply}")
                    if send_message(reply):
                        log("[autochat] 发送成功")
                        last_send_time = time.time()
                        sent_history.append(reply)
                        # 只保留最近 20 条
                        if len(sent_history) > 20:
                            sent_history = sent_history[-20:]
                        last_other_hash = other_hash
                    else:
                        log("[autochat] 发送失败")
                else:
                    log("[autochat] 未能生成回复")

                last_hash = current_hash

            time.sleep(POLL)

        except KeyboardInterrupt:
            log("[autochat] 已停止")
            break
        except Exception as e:
            log(f"[autochat] 错误: {e}")
            time.sleep(POLL)


if __name__ == "__main__":
    asyncio.run(main())
