#!/usr/bin/env python3
"""
AI 引擎 - 智谱 GLM-4-Flash
支持 OpenAI 兼容 API
"""

import os
import logging
from typing import Optional
from openai import OpenAI

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class AIEngine:
    """AI 引擎 - 调用智谱 GLM-4-Flash"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # 从环境变量读取配置
        self.api_key = os.getenv("ZHIPUAI_API_KEY", "06a208b9b6be4bb6bc42b097dc00f6b5.IOzAf6mEqeSWMa1o")
        self.base_url = os.getenv("ZHIPUAI_BASE_URL", "https://open.bigmodel.cn/api/paas/v4/")
        self.model = os.getenv("ZHIPUAI_MODEL", "glm-4-flash")
        self.memory_size = int(os.getenv("MEMORY_SIZE", "10"))

        # 初始化 OpenAI 客户端
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

        # 对话记忆
        self.conversation_history = {}

        self.logger.info(f"AI 引擎已初始化 | 模型: {self.model} | 记忆: {self.memory_size} 轮")

    def _get_history_key(self, user_id: str) -> str:
        """获取对话历史的键"""
        return user_id

    def _trim_history(self, history: list) -> list:
        """裁剪历史记录到指定长度"""
        if len(history) > self.memory_size:
            return history[-self.memory_size:]
        return history

    def generate_reply(self, user_id: str, message: str, system_prompt: Optional[str] = None) -> str:
        """生成 AI 回复"""

        # 获取或初始化对话历史
        key = self._get_history_key(user_id)
        if key not in self.conversation_history:
            self.conversation_history[key] = []

        history = self.conversation_history[key]

        # 构建消息列表
        messages = []

        # 系统提示
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            messages.append({
                "role": "system",
                "content": "你是一个友好、幽默的AI助手。请用简洁自然的中文回复用户消息。"
            })

        # 添加历史对话
        for msg in history:
            messages.append(msg)

        # 添加当前用户消息
        messages.append({"role": "user", "content": message})

        try:
            self.logger.info(f"调用 AI | 用户: {user_id} | 消息: {message[:50]}...")

            # 调用 API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500,
            )

            # 提取回复
            reply = response.choices[0].message.content.strip()
            self.logger.info(f"AI 回复 | 用户: {user_id} | 回复: {reply[:50]}...")

            # 更新历史
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": reply})
            self.conversation_history[key] = self._trim_history(history)

            return reply

        except Exception as e:
            self.logger.error(f"AI 调用失败: {e}")
            return f"⚠️ AI 服务暂时不可用，请稍后再试。\n错误信息：{str(e)}"

    def clear_history(self, user_id: str):
        """清除指定用户的对话历史"""
        key = self._get_history_key(user_id)
        if key in self.conversation_history:
            del self.conversation_history[key]
            self.logger.info(f"已清除用户 {user_id} 的对话历史")

    def get_history(self, user_id: str) -> list:
        """获取指定用户的对话历史"""
        key = self._get_history_key(user_id)
        return self.conversation_history.get(key, [])


if __name__ == "__main__":
    # 测试
    ai = AIEngine()
    reply = ai.generate_reply("test_user", "你好")
    print(f"AI 回复: {reply}")
