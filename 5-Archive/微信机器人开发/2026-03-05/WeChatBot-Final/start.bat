@echo off
chcp 65001 >nul
echo ====================================
echo   微信 AI 聊天机器人
echo ====================================
echo.

cd /d "%~dp0"

echo [1/3] 检查依赖...
python -c "import openai, dotenv, pyautogui, psutil, win32gui" 2>nul
if errorlevel 1 (
    echo 缺少依赖，正在安装...
    pip install -r requirements.txt
)

echo.
echo [2/3] 启动机器人...
echo.
echo 提示：
echo - 确保微信已登录
echo - 确保微信窗口可见
echo - 按 Ctrl+C 可停止机器人
echo.

python wechat_ai_bot.py

pause
