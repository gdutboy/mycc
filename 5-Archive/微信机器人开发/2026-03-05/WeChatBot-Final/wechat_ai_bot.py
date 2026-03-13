#!/usr/bin/env python3
"""
微信 AI 聊天机器人
基于 gdutboy/WeChat-MCP-Server + 智谱 GLM-4-Flash

功能：
- 发送消息并获取 AI 回复
- 支持对话记忆
- 支持 MCP 协议
"""

import asyncio
import io
import logging
import os
import sys
import time
from pathlib import Path
from typing import Optional

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 设置 UTF-8 输出（仅在未设置时）
if not hasattr(sys.stdout, 'encoding') or sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass  # 如果已经设置过，忽略错误

from ai_engine import AIEngine
from src.wechat_controller import WeChatController

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class WeChatAIBot:
    """微信 AI 聊天机器人"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # 初始化组件
        self.ai = AIEngine()
        self.wechat = WeChatController()

        # 配置
        self.default_contact = os.getenv("DEFAULT_CONTACT", "魔童")
        self.auto_reply_interval = int(os.getenv("AUTO_REPLY_INTERVAL", "5"))

        self.logger.info("=" * 50)
        self.logger.info("微信 AI 聊天机器人已启动")
        self.logger.info("=" * 50)
        self.logger.info(f"默认联系人: {self.default_contact}")
        self.logger.info(f"AI 模型: {self.ai.model}")
        self.logger.info(f"记忆轮数: {self.ai.memory_size}")
        self.logger.info("=" * 50)

    async def send_and_reply(self, contact: str, message: str) -> bool:
        """
        发送消息给联系人并获取 AI 回复

        Args:
            contact: 联系人名称
            message: 要发送的消息

        Returns:
            是否成功
        """
        try:
            # 1. 先用 AI 生成回复
            self.logger.info(f"处理消息 | 联系人: {contact} | 消息: {message[:50]}...")
            reply = self.ai.generate_reply(contact, message)

            if not reply or reply.startswith("⚠️"):
                self.logger.warning("AI 生成回复失败，跳过发送")
                return False

            # 2. 发送 AI 回复到微信
            self.logger.info(f"发送回复 | 联系人: {contact} | 回复: {reply[:50]}...")
            result = await self.wechat.send_text_message(contact, reply)

            if result.get("ok"):
                self.logger.info(f"✅ 消息已发送")
                return True
            else:
                stage = result.get("stage", "unknown")
                reason = result.get("reason", "Unknown error")
                self.logger.error(f"❌ 消息发送失败 | 阶段: {stage} | 原因: {reason}")
                return False

        except Exception as e:
            self.logger.error(f"处理失败: {e}")
            return False

    async def send_message(self, contact: str, message: str) -> bool:
        """
        直接发送消息（不生成 AI 回复）

        Args:
            contact: 联系人名称
            message: 要发送的消息

        Returns:
            是否成功
        """
        try:
            self.logger.info(f"发送消息 | 联系人: {contact} | 消息: {message[:50]}...")
            result = await self.wechat.send_text_message(contact, message)

            if result.get("ok"):
                self.logger.info(f"✅ 消息已发送")
                return True
            else:
                stage = result.get("stage", "unknown")
                reason = result.get("reason", "Unknown error")
                self.logger.error(f"❌ 消息发送失败 | 阶段: {stage} | 原因: {reason}")
                return False

        except Exception as e:
            self.logger.error(f"发送失败: {e}")
            return False

    async def chat_loop(self):
        """交互式聊天循环"""
        self.logger.info("\n进入交互模式（输入 'quit' 退出）")
        self.logger.info(f"默认联系人: {self.default_contact}")
        self.logger.info("命令格式: <联系人名> <消息>  或  直接输入消息（使用默认联系人）")
        self.logger.info("-" * 50)

        while True:
            try:
                user_input = input("\n> ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['quit', 'exit', 'q']:
                    self.logger.info("退出聊天")
                    break

                # 解析输入
                parts = user_input.split(maxsplit=1)

                if len(parts) == 2:
                    # 指定了联系人
                    contact, message = parts
                    await self.send_and_reply(contact, message)
                else:
                    # 使用默认联系人
                    await self.send_and_reply(self.default_contact, user_input)

            except KeyboardInterrupt:
                self.logger.info("\n退出聊天")
                break
            except Exception as e:
                self.logger.error(f"处理输入失败: {e}")

    async def test_mode(self):
        """测试模式 - 发送测试消息"""
        self.logger.info("\n=== 测试模式 ===")

        test_message = "你好，这是一条测试消息"
        self.logger.info(f"发送测试消息给 {self.default_contact}: {test_message}")

        success = await self.send_and_reply(self.default_contact, test_message)

        if success:
            self.logger.info("✅ 测试成功！")
        else:
            self.logger.error("❌ 测试失败！")

        return success


async def main_async():
    """异步主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="微信 AI 聊天机器人")
    parser.add_argument("--test", "-t", action="store_true", help="测试模式")
    parser.add_argument("--contact", "-c", help="联系人名称")
    parser.add_argument("--message", "-m", help="要发送的消息")
    args = parser.parse_args()

    bot = WeChatAIBot()

    if args.test:
        # 测试模式
        await bot.test_mode()
    elif args.contact and args.message:
        # 单次发送
        await bot.send_and_reply(args.contact, args.message)
    elif args.message:
        # 使用默认联系人
        await bot.send_and_reply(bot.default_contact, args.message)
    else:
        # 交互模式
        await bot.chat_loop()


def main():
    """主函数"""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
