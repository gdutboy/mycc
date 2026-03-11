# WeChat Send Message (Windows)
param([Parameter(Mandatory=$true)][string]$Message)

Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class Win32 {
    [DllImport("user32.dll")] public static extern IntPtr FindWindow(string cls, string name);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L,T,R,B; }
}
"@

Add-Type -AssemblyName System.Windows.Forms

# Find WeChat window
$hwnd = [Win32]::FindWindow("WeChatMainWndForPC", $null)
if ($hwnd -eq [IntPtr]::Zero) {
    Write-Host "ERROR: WeChat window not found!" -ForegroundColor Red
    Write-Host "Please open WeChat PC version first." -ForegroundColor Yellow
    exit 1
}

# Get window position
$rect = New-Object Win32+RECT
[Win32]::GetWindowRect($hwnd, [ref]$rect) | Out-Null
[Win32]::SetForegroundWindow($hwnd) | Out-Null
Start-Sleep -m 200

# Calculate input box position (bottom area)
$w = $rect.R - $rect.L
$h = $rect.B - $rect.T
$inputX = $rect.L + 200  # Offset from left
$inputY = $rect.T + $h - 60  # From bottom

# Click input box
[Windows.Forms.Cursor]::Position = New-Object Drawing.Point($inputX, $inputY)
[Windows.Forms.SendKeys]::SendWait("{ }")
Start-Sleep -m 100

# Select all and clear
[Windows.Forms.SendKeys]::SendWait("^a")
Start-Sleep -m 50
[Windows.Forms.SendKeys]::SendWait("{BS}")
Start-Sleep -m 50

# Type message
$escaped = $Message -replace '\+', '{+}' -replace '%', '{%}' -replace '~', '{~}' -replace '\(', '{(}' -replace '\)', '{)}'
[Windows.Forms.SendKeys]::SendWait($escaped)
Start-Sleep -m 200

# Send
[Windows.Forms.SendKeys]::SendWait("{ENTER}")
Start-Sleep -m 300

Write-Host "Sent: $Message" -ForegroundColor Green
