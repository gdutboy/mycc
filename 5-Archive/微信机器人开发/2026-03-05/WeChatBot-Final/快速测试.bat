@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 正在测试微信 AI 机器人...
python wechat_ai_bot.py --test
pause
