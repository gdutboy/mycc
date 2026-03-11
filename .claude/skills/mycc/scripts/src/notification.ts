/**
 * CC Notification System - 轻量方案
 * 使用 PowerShell WinForms 弹窗实现 Permission 确认
 */

import notifier from 'node-notifier';
import { spawn, execSync } from 'child_process';
import { platform } from 'process';
import path from 'path';
import fs from 'fs';
import os from 'os';

// ============== 配置 ==============
const PROTOCOL = 'claude';

interface NotificationOptions {
  sessionId: string;
  title: string;
  message: string;
  type: 'permission' | 'stop' | 'general';
  onProceed?: (approved: boolean) => void;
}

const permissionCallbacks = new Map<string, (approved: boolean) => void>();

// ============== 焦点检测 ==============

function getCurrentTerminalTitle(): string {
  if (platform !== 'win32') return '';

  try {
    const scriptPath = path.join(os.tmpdir(), 'cc-get-title.ps1');
    const script = `
Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;
public class Win32 {
  [DllImport("user32.dll")]
  public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll", CharSet = CharSet.Unicode)]
  public static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count);
}
"@
$hwnd = [Win32]::GetForegroundWindow()
$sb = New-Object System.Text.StringBuilder(256)
[Win32]::GetWindowText($hwnd, $sb, 256) | Out-Null
Write-Output $sb.ToString()
`;
    fs.writeFileSync(scriptPath, script, 'utf8');
    const result = execSync(`powershell -NoProfile -ExecutionPolicy Bypass -File "${scriptPath}"`, {
      encoding: 'utf8',
      timeout: 3000,
    });
    fs.unlinkSync(scriptPath);
    return result.trim();
  } catch {
    return '';
  }
}

export function isTerminalInForeground(): boolean {
  const title = getCurrentTerminalTitle();
  if (!title) return true;

  const terminalKeywords = ['powershell', 'windows terminal', 'cmd.exe', 'claude code', 'node.js', '终端'];
  const lowerTitle = title.toLowerCase();
  return terminalKeywords.some(kw => lowerTitle.includes(kw));
}

// ============== Protocol Handler ==============

function registerProtocolHandler(): void {
  if (platform !== 'win32') return;

  try {
    const regPath = 'HKCU\\Software\\Classes\\claude';
    execSync(`reg query "${regPath}" /ve`, { stdio: 'ignore' });
  } catch {
    try {
      const exePath = process.execPath;
      const scriptPath = path.join(os.tmpdir(), 'cc-register-protocol.ps1');
      const script = `
$regPath = "HKCU:\\Software\\Classes\\claude"
New-Item -Path $regPath -Force | Out-Null
Set-ItemProperty -Path $regPath -Name "(Default)" -Value "URL:Claude Protocol"
Set-ItemProperty -Path $regPath -Name "URL Protocol" -Value ""
$commandPath = "$regPath\\shell\\open\\command"
New-Item -Path $commandPath -Force | Out-Null
Set-ItemProperty -Path $commandPath -Name "(Default)" -Value '"${exePath}" "%1"'
`;
      fs.writeFileSync(scriptPath, script, 'utf8');
      execSync(`powershell -NoProfile -ExecutionPolicy Bypass -File "${scriptPath}"`, {
        encoding: 'utf8',
        timeout: 5000,
      });
      fs.unlinkSync(scriptPath);
    } catch (e) {
      // 忽略错误
    }
  }
}

export function parseProtocolUrl(url: string): { action: string; sessionId?: string; approved?: boolean } | null {
  try {
    const parsed = new URL(url);
    if (parsed.protocol !== 'claude:') return null;
    return {
      action: parsed.hostname,
      sessionId: parsed.searchParams.get('session') || undefined,
      approved: parsed.searchParams.get('action') === 'proceed',
    };
  } catch {
    return null;
  }
}

// ============== Permission 弹窗 ==============

/**
 * 创建 PowerShell WinForms 弹窗（带 Proceed/Deny 按钮）
 */
function showPermissionDialog(
  sessionId: string,
  title: string,
  message: string,
  onResult: (approved: boolean) => void
): void {
  const resultFile = path.join(os.tmpdir(), `cc-permission-${Date.now()}.txt`);

  // 注册回调
  const callbackKey = sessionId;
  permissionCallbacks.set(callbackKey, onResult);

  // PowerShell 脚本：创建 WinForms 窗口
  const script = `
Add-Type -AssemblyName System.Windows.Forms

$form = New-Object System.Windows.Forms.Form
$form.Text = "${title}"
$form.Width = 450
$form.Height = 200
$form.StartPosition = "CenterScreen"
$form.TopMost = $true
$form.FormBorderStyle = "FixedDialog"
$form.MaximizeBox = $false

$label = New-Object System.Windows.Forms.Label
$label.Text = "${message}"
$label.AutoSize = $false
$label.Width = 400
$label.Height = 60
$label.Location = New-Object System.Drawing.Point(20, 20)
$label.TextAlign = "MiddleCenter"
$form.Controls.Add($label)

$sessionLabel = New-Object System.Windows.Forms.Label
$sessionLabel.Text = "Session: ${sessionId}"
$sessionLabel.ForeColor = "Gray"
$sessionLabel.AutoSize = $true
$sessionLabel.Location = New-Object System.Drawing.Point(20, 90)
$form.Controls.Add($sessionLabel)

$proceedBtn = New-Object System.Windows.Forms.Button
$proceedBtn.Text = "Proceed"
$proceedBtn.Width = 100
$proceedBtn.Height = 35
$proceedBtn.Location = New-Object System.Drawing.Point(180, 110)
$proceedBtn.DialogResult = "OK"
$form.Controls.Add($proceedBtn)

$denyBtn = New-Object System.Windows.Forms.Button
$denyBtn.Text = "Deny"
$denyBtn.Width = 100
$denyBtn.Height = 35
$denyBtn.Location = New-Object System.Drawing.Point(290, 110)
$denyBtn.DialogResult = "Cancel"
$form.Controls.Add($denyBtn)

$result = $form.ShowDialog()
if ($result -eq "OK") {
  Write-Output "PROCEED"
} else {
  Write-Output "DENY"
}
`;

  const scriptPath = path.join(os.tmpdir(), `cc-dialog-${Date.now()}.ps1`);
  fs.writeFileSync(scriptPath, script, 'utf8');

  // 启动 PowerShell 进程（不同步阻塞，等待用户点击）
  const ps = spawn('powershell', [
    '-NoProfile',
    '-ExecutionPolicy', 'Bypass',
    '-File', scriptPath
  ], {
    stdio: ['pipe', 'pipe', 'pipe']
  });

  let output = '';
  ps.stdout.on('data', (data) => {
    output += data.toString();
  });

  ps.on('close', (code) => {
    // 清理脚本文件
    try { fs.unlinkSync(scriptPath); } catch {}

    const result = output.trim();
    const approved = result === 'PROCEED';

    console.log(`[Notification] 用户选择: ${approved ? 'Proceed' : 'Deny'}`);

    // 触发回调
    const callback = permissionCallbacks.get(callbackKey);
    if (callback) {
      callback(approved);
      permissionCallbacks.delete(callbackKey);
    }
  });

  ps.on('error', (err) => {
    console.error('[Notification] 弹窗进程错误:', err);
    try { fs.unlinkSync(scriptPath); } catch {}
  });
}

// ============== 通知发送 ==============

export function sendNotification(options: NotificationOptions): void {
  const { sessionId, title, message, type, onProceed } = options;

  if (platform !== 'win32') {
    console.log(`[Notification] [${sessionId}] ${title}: ${message}`);
    return;
  }

  // 焦点检测：在前台则跳过
  if (isTerminalInForeground()) {
    console.log(`[Notification] [${sessionId}] 终端在前台，跳过通知`);
    return;
  }

  if (type === 'permission' && onProceed) {
    // 使用 WinForms 弹窗
    showPermissionDialog(sessionId, title, message, onProceed);
  } else {
    // 普通通知
    notifier.notify({
      title: `[${sessionId}] ${title}`,
      message,
      sound: true,
    });
    console.log(`[Notification] [${sessionId}] 通知已发送: ${title}`);
  }
}

// ============== 智能延迟 ==============

interface PendingNotification {
  options: NotificationOptions;
  retryCount: number;
  maxRetries: number;
}

const pendingQueue: PendingNotification[] = [];
let checkInterval: NodeJS.Timeout | null = null;

export function sendNotificationSmart(options: NotificationOptions): void {
  const { sessionId, title } = options;

  if (!isTerminalInForeground()) {
    sendNotification(options);
    return;
  }

  console.log(`[Notification] [${sessionId}] 终端在后台，加入延迟队列`);
  pendingQueue.push({
    options,
    retryCount: 0,
    maxRetries: 10,
  });

  if (!checkInterval) {
    checkInterval = setInterval(checkPendingNotifications, 2000);
  }
}

function checkPendingNotifications(): void {
  const toRemove: number[] = [];

  for (let i = 0; i < pendingQueue.length; i++) {
    const pending = pendingQueue[i];
    const { sessionId, title } = pending.options;

    if (!isTerminalInForeground()) {
      sendNotification(pending.options);
      toRemove.push(i);
    } else {
      pending.retryCount++;
      if (pending.retryCount >= pending.maxRetries) {
        console.log(`[Notification] [${sessionId}] 通知超时放弃: ${title}`);
        toRemove.push(i);
      }
    }
  }

  for (let i = toRemove.length - 1; i >= 0; i--) {
    pendingQueue.splice(toRemove[i], 1);
  }

  if (pendingQueue.length === 0 && checkInterval) {
    clearInterval(checkInterval);
    checkInterval = null;
  }
}

// ============== 初始化 ==============

export function initNotificationSystem(): void {
  if (platform === 'win32') {
    registerProtocolHandler();
    console.log('[Notification] 系统初始化完成');
  }
}

// ============== 测试 ==============

if (import.meta.url === `file://${process.argv[1]}`) {
  const sessionId = process.argv[2] || 'test-session';
  const type = process.argv[3] || 'general';

  console.log('测试通知系统...');
  initNotificationSystem();

  if (type === 'permission') {
    sendNotification({
      sessionId,
      title: 'Permission Required',
      message: 'CC 需要执行命令，是否允许？',
      type: 'permission',
      onProceed: (approved) => {
        console.log(`=== 用户选择了: ${approved ? '允许' : '拒绝'}`);
        process.exit(0);
      },
    });
    console.log('等待用户点击...');
    setTimeout(() => {
      console.log('超时');
      process.exit(1);
    }, 120000);
  } else {
    sendNotification({
      sessionId,
      title: 'CC Stopped',
      message: 'Claude Code 已停止',
      type: 'stop',
    });
    setTimeout(() => process.exit(0), 2000);
  }
}
