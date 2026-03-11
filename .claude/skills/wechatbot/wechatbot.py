#!/usr/bin/env python3
"""
微信智能回复机器人 - 使用 EasyOCR + MiniMax API
监控微信聊天，检测 @MYCC 触发词，自动调用 AI 生成回复

环境变量:
  MINIMAX_API_KEY: MiniMax API Key

用法:
  python wechat-ai-bot-easy.py                  # 启动机器人
  python wechat-ai-bot-easy.py --trigger 小助手  # 自定义触发词
"""

import argparse
import json
import os
import sys
import time
import subprocess
from datetime import datetime
from pathlib import Path

# 设置 UTF-8 输出，支持 emoji
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 自动加载 .env 文件
def load_env_file():
    """从 .env 文件加载环境变量"""
    # 查找 .env 文件：当前目录 -> wechat-bot -> mycc
    possible_paths = [
        Path(".env"),
        Path(__file__).parent / "wechat-bot" / ".env",
        Path(__file__).parent / "mycc" / ".env",
    ]
    for env_path in possible_paths:
        if env_path.exists():
            print(f"[配置] 加载环境变量 from {env_path}")
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        if key.strip() not in os.environ:
                            os.environ[key.strip()] = value.strip()
            break
    else:
        print("[警告] 未找到 .env 文件")

load_env_file()

try:
    import pyautogui
    from mss import mss
    from PIL import Image
    import numpy as np
    import easyocr
    import requests
except ImportError as e:
    print(f"缺少依赖: {e}")
    print("请运行: pip install pytesseract requests")
    sys.exit(1)

# 配置
TRIGGER_WORD = os.getenv("WECHAT_TRIGGER", "@MYCC")
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
MINIMAX_MODEL = "M2-her"
MINIMAX_API_URL = "https://api.minimaxi.com/v1/text/chatcompletion_v2"
CHECK_INTERVAL = 3  # 检查间隔（秒）
MAX_HISTORY = 10
GLOBAL_COOLDOWN = 10  # 全局冷却时间（秒）
REPLY_COOLDOWN = 30   # 同一触发词冷却时间（秒）
ADMIN_NAME = os.getenv("WECHAT_ADMIN", "魔童")  # 管理员名称

pyautogui.FAILSAFE = False

# 全局客户端
# 已回复的问题集合（防止重复回复）
_replied_questions = set()
# 最后一次回复时间（全局冷却）
_last_reply_time = 0
_last_replied_trigger = None  # 最后一次回复的触发词
# 最近回复的触发消息（防止同一消息重复回复）
_last_trigger_msg = None
# 对话日志文件
LOG_FILE = Path(__file__).parent / "wechat-bot.log"


def log_conversation(question, reply, sender=None):
    """记录对话到日志文件"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] 发言: {sender or '未知'} | 问题: {question} | 回复: {reply}\n"
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"[日志错误] {e}")


def get_minimax_response(messages, api_key):
    """调用 MiniMax API 生成回复"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": MINIMAX_MODEL,
        "messages": messages,
        "temperature": 0.6,
        "max_completion_tokens": 150
    }

    try:
        response = requests.post(MINIMAX_API_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        result = response.json()

        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        else:
            return f"API 返回格式异常: {result}"

    except requests.exceptions.Timeout:
        return "请求超时，请稍后重试"
    except requests.exceptions.RequestException as e:
        return f"API 请求失败: {str(e)[:50]}"
    except (KeyError, json.JSONDecodeError) as e:
        return f"解析响应失败: {str(e)[:50]}"


def find_wechat_window():
    """查找微信窗口"""
    ps_script = """
Add-Type -AssemblyName UIAutomationClient
$automation = [Windows.Automation.AutomationElement]::RootElement
$windows = $automation.FindAll([Windows.Automation.TreeScope]::Children, [Windows.Automation.Condition]::TrueCondition)
foreach ($win in $windows) {
    if ($win.Current.ClassName -like "*Qt*" -or $win.Current.Name -eq "微信") {
        $rect = $win.Current.BoundingRectangle
        Write-Host "WINDOW|$($rect.Left)|$($rect.Top)|$($rect.Width)|$($rect.Height)|$($win.Current.Name)"
    }
}
"""
    result = subprocess.run(
        ["powershell", "-Command", ps_script],
        capture_output=True, text=True
    )

    for line in result.stdout.split('\n'):
        if line.startswith('WINDOW|'):
            parts = line.split('|')
            if len(parts) >= 6:
                try:
                    x = int(parts[1]) if parts[1] != 'Infinity' and parts[1].strip() else 0
                    y = int(parts[2]) if parts[2] != 'Infinity' and parts[2].strip() else 0
                    width = int(parts[3]) if parts[3] != 'Infinity' and parts[3].strip() else 800
                    height = int(parts[4]) if parts[4] != 'Infinity' and parts[4].strip() else 600
                    if width < 100 or height < 100:
                        continue
                    return {
                        'x': x, 'y': y,
                        'width': width, 'height': height,
                        'name': parts[5]
                    }
                except (ValueError, IndexError):
                    continue
    return None


def is_window_foreground(window_title="微信"):
    """检查指定窗口是否在前台"""
    ps_script = f"""
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32 {{
    [DllImport("user32.dll")]
    public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll", SetLastError = true)]
    public static extern int GetWindowText(IntPtr hWnd, System.Text.StringBuilder text, int count);
}}
"@
$fg = [Win32]::GetForegroundWindow()
$sb = New-Object System.Text.StringBuilder 256
[Win32]::GetWindowText($fg, $sb, 256) | Out-Null
$title = $sb.ToString()
if ($title -like "*{window_title}*") {{
    Write-Host "FOREGROUND"
}} else {{
    Write-Host "BACKGROUND|$title"
}}
"""
    result = subprocess.run(
        ["powershell", "-Command", ps_script],
        capture_output=True, text=True
    )
    return "FOREGROUND" in result.stdout


def get_chat_area(window):
    """计算聊天区域（覆盖整个聊天窗口）"""
    SIDEBAR_WIDTH = 320    # 左侧栏宽度
    TITLE_HEIGHT = 50       # 顶部标题栏高度
    INPUT_HEIGHT = 80       # 底部输入框区域

    # 聊天区域总宽度
    chat_width = window['width'] - SIDEBAR_WIDTH

    # 覆盖整个聊天区域（包括左右两边）
    return {
        'x': window['x'] + SIDEBAR_WIDTH,
        'y': window['y'] + TITLE_HEIGHT,
        'width': chat_width,  # 整个聊天区域
        'height': window['height'] - TITLE_HEIGHT - INPUT_HEIGHT
    }


# 调试模式：保存截图
DEBUG_SCREENSHOT = False
DEBUG_DIR = Path(__file__).parent / "debug_screenshots"


def capture_chat_area(window):
    """截取聊天区域"""
    area = get_chat_area(window)
    with mss() as sct:
        monitor = {
            "top": area['y'],
            "left": area['x'],
            "width": area['width'],
            "height": area['height']
        }
        screenshot = sct.grab(monitor)
    img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)

    # 调试：保存截图
    if DEBUG_SCREENSHOT:
        import random
        DEBUG_DIR.mkdir(exist_ok=True)
        debug_path = DEBUG_DIR / f"debug_{random.randint(1000,9999)}.png"
        img_pil = Image.fromarray(img)
        img_pil.save(debug_path)
        print(f"[DEBUG] 截图已保存: {debug_path}")

    return np.array(img)


# 非聊天内容过滤关键词
NON_CHAT_KEYWORDS = [
    'powershell', 'command', 'cmd', 'terminal', 'taskkill', 'stop-process',
    'action', 'silently', 'continue', 'error', 'warning', 'exception',
    'claude', 'output', 'task_', 'process', 'window', 'rect',
    'gpu', 'cpu', 'import', 'def ', 'return ', 'class ',
    '.exe', '.py', '.js', '.ts', 'http', 'https', 'www.',
    '|', '>>', '<<', '--', '//', '&&', '||',
    # 终端乱码
    'ng', 'to manage', '129', '127', 'manage)', "'",
]

def is_likely_chat_message(text):
    """判断是否可能是聊天消息"""
    text_lower = text.lower()
    # 过滤包含系统/代码关键词的
    for kw in NON_CHAT_KEYWORDS:
        if kw in text_lower:
            return False
    # 过滤纯数字和符号
    if len(text.strip()) < 2:
        return False
    # 过滤连续大写字母（可能是代码）
    if len(text) > 10 and text.isupper() and not any(c in text for c in 'AEIOU'):
        return False
    return True


# 初始化 EasyOCR（全局，只初始化一次）
_ocr_reader = None

def get_ocr_reader():
    """获取或初始化 EasyOCR 阅读器"""
    global _ocr_reader
    if _ocr_reader is None:
        print("初始化 EasyOCR...")
        _ocr_reader = easyocr.Reader(['ch_sim', 'en'], gpu=False, verbose=False,
                                      model_storage_directory='./models',
                                      download_enabled=True,
                                      batch_size=1)
        print("EasyOCR 初始化完成")
    return _ocr_reader


def ocr_chat_area(window):
    """OCR 聊天区域"""
    img = capture_chat_area(window)

    # 使用 EasyOCR 识别
    try:
        reader = get_ocr_reader()
        result = reader.readtext(img)
        if not result:
            return []

        # 提取文字（EasyOCR返回格式：[(box, text, confidence), ...]）
        lines = []
        for item in result:
            if len(item) >= 2:
                text = item[1]  # 识别文本
                if isinstance(text, str):
                    lines.append(text.strip())

        # 调试：打印原始 OCR 结果
        print(f"[DEBUG OCR] 原始结果: {lines[:5]}")

    except Exception as e:
        print(f"[OCR错误] {e}")
        return []

    # 过滤
    messages = []
    for line in lines:
        if is_likely_chat_message(line):
            messages.append(line)

    return messages


def detect_trigger(messages, trigger):
    """检测是否包含触发词，返回最新的包含触发词的消息"""
    # 提取纯触发词（去掉 @ 符号）
    trigger_keyword = trigger.replace('@', '').lower()

    # 从后往前找，找最新的
    for msg in reversed(messages):
        msg_lower = msg.lower()
        # 匹配 @mycc, mycc, @MYCC, MYCC 等形式
        if trigger_keyword in msg_lower:
            return True, msg
    return False, None


def is_admin_command(message, sender_name):
    """检测是否是管理员下线命令"""
    if sender_name != ADMIN_NAME:
        return False
    keywords = ['下线', '停止', '结束', '退出', '关闭', '再见']
    return any(kw in message for kw in keywords)


def extract_sender(messages, trigger_msg):
    """从消息列表中提取触发消息的发言人"""
    trigger_keyword = trigger_msg.replace('@', '').lower()

    # 查找包含触发词的消息及其前面的消息
    for i, msg in enumerate(messages):
        if trigger_keyword in msg.lower():
            # 检查前面的消息是否是发言人（通常在触发消息的上方或同一条）
            if i > 0:
                prev_msg = messages[i - 1]
                # 前面一条消息可能是用户名（短，没有触发词）
                if len(prev_msg) < 20 and trigger_keyword not in prev_msg.lower():
                    # 去掉 @ 符号
                    sender = prev_msg.strip()
                    if sender.startswith('@'):
                        sender = sender[1:]
                    if sender and not any(kw in sender.lower() for kw in ['mycc', 'wx', 'wechat']):
                        return sender

            # 检查当前消息是否包含用户名（在触发词前面）
            # 格式：用户名 @mycc xxx
            for prefix in ['@' + trigger_keyword, trigger_keyword]:
                idx = msg.lower().find(prefix)
                if idx > 0:
                    sender = msg[:idx].strip()
                    if sender and len(sender) < 20:
                        return sender

    return None
    return None


# 不安全关键词
UNSAFE_KEYWORDS = [
    '暴力', '色情', '赌博', '诈骗', '黑客', '病毒', '武器', '毒品',
    '炸弹', '枪支', '弹药', '恐怖', '袭击', '杀人', '自杀',
    '木马', '钓鱼', '钓鱼网站', '入侵', '破解', '外挂'
]


def is_safe_question(question):
    """检测问题是否安全"""
    question_lower = question.lower()
    return not any(kw in question_lower for kw in UNSAFE_KEYWORDS)


def get_safe_reply():
    """安全问题委婉拒绝"""
    replies = [
        "这个问题我不太方便回答，咱们聊点别的吧~",
        "这个我不太懂，换个话题聊聊？",
        "我不知道这个，咱们说点别的吧！",
        "这块儿我不太擅长，换个问题试试？"
    ]
    import random
    return random.choice(replies)


def extract_question(messages, trigger):
    """从消息中提取问题（提取最新的包含触发词的消息）"""
    trigger_keyword = trigger.replace('@', '').lower()  # 去掉 @ 符号

    # 从后往前找（微信消息是倒序的，最新的在下面）
    for msg in reversed(messages):
        msg_lower = msg.lower()
        # 检查是否包含触发词（去掉 @ 后匹配）
        if trigger_keyword in msg_lower:
            # 提取触发词后面的内容
            # 尝试多种格式：@mycc xxx, mycc xxx, @MYCC xxx
            for prefix in ['@' + trigger_keyword, trigger_keyword, '@' + trigger_keyword.upper(), '@' + trigger_keyword.capitalize()]:
                idx = msg_lower.find(prefix)
                if idx != -1:
                    question = msg[idx + len(prefix):].strip()
                    if question:
                        return question
            # 如果没找到后缀，直接移除触发词
            question = msg
            for variant in [trigger, trigger.lower(), trigger.upper(), trigger.capitalize()]:
                question = question.replace(variant, "")
            question = question.strip()
            if question:
                return question

    return "你好！"


def extract_question_from_trigger(trigger_msg, trigger):
    """从检测到的触发消息中提取问题（更准确）"""
    if not trigger_msg:
        return "你好！"

    trigger_keyword = trigger.replace('@', '').lower()
    msg_lower = trigger_msg.lower()

    # 提取触发词后面的内容
    for prefix in ['@' + trigger_keyword, trigger_keyword, '@' + trigger_keyword.upper(), '@' + trigger_keyword.capitalize()]:
        idx = msg_lower.find(prefix)
        if idx != -1:
            question = trigger_msg[idx + len(prefix):].strip()
            if question:
                return question

    # 如果没找到后缀，直接移除触发词
    question = trigger_msg
    for variant in [trigger, trigger.lower(), trigger.upper(), trigger.capitalize()]:
        question = question.replace(variant, "")
    question = question.strip()
    if question:
        return question

    return "你好！"


def web_search(query, need_link=False):
    """简单的网页搜索
    - need_link: 是否需要返回链接（音乐、视频类问题需要）
    """
    import urllib.parse
    try:
        # 使用 DuckDuckGo HTML 搜索
        url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)

        # 提取搜索结果标题和链接
        import re
        # 匹配链接和标题
        pattern = r'<a class="result__a" href="(https?://[^"]*)"[^>]*>([^<]+)</a>'
        matches = re.findall(pattern, response.text, re.IGNORECASE)

        if matches:
            results = []
            for href, title in matches[:5]:
                decoded_url = urllib.parse.unquote(href)
                if need_link:
                    # 音乐/视频需要链接
                    results.append(f"{title.strip()}\n{decoded_url}")
                else:
                    # 其他只返回标题
                    results.append(f"- {title.strip()}")
            return "\n".join(results)
        return None
    except Exception as e:
        print(f"[搜索错误] {e}")
        return None


def get_ai_response(question, conversation_history=None):
    """调用 MiniMax API 生成智能回复"""
    if not MINIMAX_API_KEY:
        return "错误: 未设置 MINIMAX_API_KEY 环境变量"

    messages = []

    # 检测是否需要联网搜索（扩展到生活资讯类问题）
    # 本地问题不搜索：问候、闲聊、个人问题
    local_only_patterns = ['你好', '早上好', '晚好', '在吗', '干嘛', '忙吗', '睡了吗', '吃了吗',
                           '怎么样', '好不好', '累不累', '开心吗', '今天过得', '最近如何',
                           '夸', '笑话', '讲故事', '玩', '聊天']
    is_local_only = any(p in question for p in local_only_patterns)

    # 生活资讯类问题需要联网
    need_search = not is_local_only and any(kw in question for kw in [
        # 时间日期
        '时间', '日期', '今天', '明天', '昨天', '现在', '几点', '多少号', '星期几', '农历',
        # 天气
        '天气', '气温', '温度', '下雨', '晴天', '阴天', '台风', '预警',
        # 新闻资讯
        '新闻', '最新', '消息', '热点', '热搜', '头条',
        # 财经
        '股票', '基金', '行情', '汇率', '美元', '人民币', '欧元', '日元', '港币', '油价', '黄金',
        # 生活
        '天气', '交通', '堵车', '限行', '感冒', '发烧', '咳嗽', '疫情', '核酸', '病毒',
        # 知识
        '什么是', '怎么', '如何', '为什么', '哪个', '什么', '多少', '多少钱', '哪里',
        # 搜索
        '查一下', '帮我查', '搜索', '问一下', '知道吗', '介绍一下', '解释',
        # 娱乐
        '电影', '电视剧', '综艺', '比赛', '球赛', '比分', '音乐', '听歌', '歌曲', '歌',
        '视频', 'youtube', 'bilibili', '抖音', 'MV', '演唱会',
    ])

    search_context = ""
    if need_search:
        # 判断是否需要链接（音乐/视频类）
        need_link = any(kw in question for kw in ['音乐', '听歌', '歌曲', '歌', '视频', 'mv', '电影', '电视剧', '综艺'])
        print(f"[搜索] 检测到需要联网查询: {question} (需要链接: {need_link})")
        search_result = web_search(question, need_link=need_link)
        if search_result:
            search_context = f"\n\n【联网搜索结果】\n{search_result}\n【以上是搜索结果，请根据真实信息回答】"
            print(f"[搜索] 获得 {len(search_result)} 字符结果")

    # 系统提示词：真人聊天风格，不要模板化回复
    system_prompt = """你是 CC，一个聪明幽默的 AI 助手，像真人朋友一样聊天。

关键规则：
1. 不要说"我是AI助手"、"我是一个AI"这种自我介绍
2. 不要用模板回复（如"好的"、"收到"、"请问有什么可以帮您"）
3. 直接回答问题，就像朋友之间聊天
4. 可以用口语化的表达，甚至带点幽默
5. 如果问题太模糊（如"介绍一下"），直接反问或推测意图回答
6. 回复要简短有力，一般20-60字，不超过80字
7. 如果不知道，直接说"不太清楚"或"没理解"，不要瞎编"""

    if search_context:
        system_prompt += search_context

    messages.append({
        "role": "system",
        "content": system_prompt
    })

    # 只保留最近2轮对话（避免混乱）
    if conversation_history and len(conversation_history) > 4:
        conversation_history = conversation_history[-4:]
    if conversation_history:
        messages.extend(conversation_history)

    messages.append({"role": "user", "content": question})

    # 调用 MiniMax API
    reply = get_minimax_response(messages, MINIMAX_API_KEY)

    # 截断过长回复
    if len(reply) > 100:
        reply = reply[:97] + "..."

    return reply


def send_message_to_wechat(window, message):
    """发送消息到微信"""
    SIDEBAR_WIDTH = 310
    INPUT_MARGIN = 60
    input_x = window['x'] + SIDEBAR_WIDTH + (window['width'] - SIDEBAR_WIDTH) // 2
    input_y = window['y'] + window['height'] - INPUT_MARGIN

    pyautogui.click(input_x, input_y)
    time.sleep(0.3)
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.1)

    escaped_message = message.replace('"', '`"').replace('`', '``')
    ps_clip = f'Set-Clipboard -Value "{escaped_message}"'
    subprocess.run(["powershell", "-Command", ps_clip], capture_output=True)
    time.sleep(0.3)

    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.3)
    pyautogui.press('enter')
    time.sleep(0.3)


def activate_wechat_window(window):
    """激活微信窗口（不闪烁）"""
    if sys.platform == 'win32':
        import ctypes
        user32 = ctypes.windll.user32

        # 查找窗口并激活
        hwnd = user32.FindWindowW(None, window['name'])
        if hwnd:
            user32.SetForegroundWindow(hwnd)


def main():
    parser = argparse.ArgumentParser(description="微信智能回复机器人 (EasyOCR + MiniMax)")
    parser.add_argument("--trigger", default=TRIGGER_WORD, help="触发词")
    parser.add_argument("--interval", type=int, default=CHECK_INTERVAL, help="检查间隔（秒）")
    parser.add_argument("--once", action="store_true", help="单次运行")
    parser.add_argument("--test", action="store_true", help="测试模式")

    args = parser.parse_args()

    print("=" * 60)
    print("微信智能回复机器人 (EasyOCR + MiniMax)")
    print("=" * 60)
    print(f"触发词: {args.trigger}")
    print(f"检查间隔: {args.interval}秒")
    print(f"OCR: EasyOCR (本地)")
    print(f"AI: MiniMax {MINIMAX_MODEL}")
    print(f"MiniMax API: {'已配置' if MINIMAX_API_KEY else '未配置'}")
    print("=" * 60)

    # 查找微信窗口
    print("\n正在查找微信窗口...")
    window = find_wechat_window()
    if not window:
        print("错误: 未找到微信窗口")
        sys.exit(1)
    print(f"找到窗口: {window['name']}")
    print(f"窗口坐标: x={window['x']}, y={window['y']}, w={window['width']}, h={window['height']}")
    chat_area = get_chat_area(window)
    print(f"聊天区域: x={chat_area['x']}, y={chat_area['y']}, w={chat_area['width']}, h={chat_area['height']}")

    # 启动时截取聊天区域截图，供确认 OCR 区域
    print("\n正在截取聊天区域截图...")
    # 先截取整个窗口
    with mss() as sct:
        screenshot = sct.grab({
            "left": window["x"],
            "top": window["y"],
            "width": window["width"],
            "height": window["height"]
        })
        full_img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)

    # 在聊天区域画红色矩形框
    from PIL import ImageDraw
    draw = ImageDraw.Draw(full_img)
    draw.rectangle(
        [(chat_area["x"] - window["x"], chat_area["y"] - window["y"]),
         (chat_area["x"] - window["x"] + chat_area["width"], chat_area["y"] - window["y"] + chat_area["height"])],
        outline="red",
        width=3
    )

    screenshot_path = Path(__file__).parent / "chat_area_screenshot.png"
    full_img.save(screenshot_path)
    print(f"截图已保存: {screenshot_path}")
    print("请确认截图中的红色框选区域是否正确覆盖了聊天内容")

    activate_wechat_window(window)

    seen_messages = set()
    conversation_history = []
    global _replied_questions, _last_reply_time, _last_trigger_msg

    print(f"\n开始监控... (按 Ctrl+C 退出)\n")

    try:
        while True:
            timestamp = datetime.now().strftime("%H:%M:%S")
            current_time = time.time()

            # 检查微信窗口是否在前台
            if not is_window_foreground("微信"):
                time.sleep(args.interval)
                continue

            messages = ocr_chat_area(window)

            # 记录聊天日志
            log_path = Path(__file__).parent / "chat_log.txt"
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] OCR: {messages}\n")

            if not messages:
                time.sleep(args.interval)
                continue

            # 检测触发词
            triggered, trigger_msg = detect_trigger(messages, args.trigger)

            if triggered:
                # 记录触发日志
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(f"[{timestamp}] 触发词检测到: {trigger_msg}\n")

                print(f"[DEBUG] OCR messages: {messages}")
                print(f"[DEBUG] Trigger detected in: {trigger_msg}")

                # 提取问题
                question = extract_question_from_trigger(trigger_msg, args.trigger)

                # 提取发言人
                sender_name = extract_sender(messages, trigger_msg)
                print(f"[DEBUG] 发言人: {sender_name}")

                # 检查是否是管理员下线命令
                if is_admin_command(question, sender_name):
                    print(f"\n[{timestamp}] 收到管理员 {ADMIN_NAME} 下线命令，正在退出...")
                    break

                # 检查是否需要跳过（避免重复回复同一触发词）
                # 如果同一个触发词在 REPLY_COOLDOWN 秒内再次出现，跳过
                if _last_replied_trigger and trigger_msg == _last_replied_trigger:
                    if current_time - _last_reply_time < REPLY_COOLDOWN:
                        time.sleep(args.interval)
                        continue

                # 记录触发消息
                _last_trigger_msg = trigger_msg

                # 调用 API 回复
                print(f"[{timestamp}] 正在调用 API 回复...")

                print(f"\n[{timestamp}] 检测到触发词!")
                print(f"问题: {question}")

                if args.test:
                    print("[测试模式] 跳过回复")
                else:
                    # 检查安全问题
                    if not is_safe_question(question):
                        print("[安全检查] 问题包含敏感内容，委婉拒绝")
                        reply = get_safe_reply()
                    else:
                        print("正在生成回复...")
                        reply = get_ai_response(question, conversation_history)
                    print(f"回复: {reply}")

                    print("发送消息...")
                    send_message_to_wechat(window, reply)
                    print("发送成功!")

                    # 记录对话到日志（包括触发问题和回复内容）
                    log_path = Path(__file__).parent / "chat_log.txt"
                    with open(log_path, "a", encoding="utf-8") as f:
                        f.write(f"[{timestamp}] 问题: {question}\n")
                        f.write(f"[{timestamp}] 回复: {reply}\n")
                        f.write(f"[{timestamp}] 发言人: {sender_name}\n")
                        f.write("-" * 50 + "\n")

                    # 记录已回复的问题
                    _replied_questions.add(question)
                    # 更新最后回复时间
                    _last_reply_time = current_time
                    # 记录最后一次回复的触发词
                    _last_replied_trigger = trigger_msg

                    # 更新对话历史
                    conversation_history.append({"role": "user", "content": question})
                    conversation_history.append({"role": "assistant", "content": reply})

                    if len(conversation_history) > MAX_HISTORY * 2:
                        conversation_history = conversation_history[-MAX_HISTORY * 2:]

                if args.once:
                    break
                time.sleep(args.interval * 2)
            else:
                if len(messages) > 0:
                    print(f"[{timestamp}] 监控中... ({len(messages)} 条消息)", flush=True)

            time.sleep(args.interval)

    except KeyboardInterrupt:
        print("\n\n已停止监控")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
