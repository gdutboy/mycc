# WeChat Read Messages (Windows)
param([switch]$BBox)

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

# Find WeChat
$hwnd = [Win32]::FindWindow("WeChatMainWndForPC", $null)
if ($hwnd -eq [IntPtr]::Zero) {
    Write-Host "ERROR: WeChat not found!" -ForegroundColor Red
    exit 1
}

# Get window info
$rect = New-Object Win32+RECT
[Win32]::GetWindowRect($hwnd, [ref]$rect) | Out-Null
[Win32]::SetForegroundWindow($hwnd) | Out-Null
Start-Sleep -m 100

# Chat region (exclude sidebar and input area)
$SIDEBAR = 310
$TITLE_H = 50
$INPUT_H = 110

$chatX = $rect.L + $SIDEBAR
$chatY = $rect.T + $TITLE_H
$chatW = $rect.R - $rect.L - $SIDEBAR
$chatH = $rect.B - $rect.T - $TITLE_H - $INPUT_H

# Move mouse to chat center
$centerX = $chatX + $chatW / 2
$centerY = $chatY + $chatH / 2

Add-Type -AssemblyName System.Windows.Forms
[Windows.Forms.Cursor]::Position = New-Object Drawing.Point([int]$centerX, [int]$centerY)
Start-Sleep -m 50

# Call OCR
$skillDir = Join-Path $PSScriptRoot "..\..\desktop"
$ocrScript = Join-Path $skillDir "ocr-win.py"

if (Test-Path $ocrScript) {
    $size = "${chatW}x${chatH}"
    if ($BBox) {
        python $ocrScript --cursor --bbox --size $size --lang "chi_sim+eng" 2>$null
    } else {
        python $ocrScript --cursor --size $size --lang "chi_sim+eng" 2>$null
    }
} else {
    Write-Host "OCR script not found: $ocrScript" -ForegroundColor Red
    Write-Host "Please install Tesseract OCR first." -ForegroundColor Yellow
}
