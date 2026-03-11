# Windows Control Script (Mouse & Keyboard)
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class Win32 {
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern bool GetCursorPos(out POINT lpPoint);
    [DllImport("user32.dll")] public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint cButtons, uint dwExtraInfo);
    public const uint MOUSEEVENTF_LEFTDOWN = 0x0002;
    public const uint MOUSEEVENTF_LEFTUP = 0x0004;
    public const uint MOUSEEVENTF_RIGHTDOWN = 0x0008;
    public const uint MOUSEEVENTF_RIGHTUP = 0x0010;
    [StructLayout(LayoutKind.Sequential)] public struct POINT { public int X; public int Y; }
}
"@
Add-Type -AssemblyName System.Windows.Forms

function Get-MousePos {
    $pt = New-Object Win32+POINT
    [Win32]::GetCursorPos([ref]$pt) | Out-Null
    return "$($pt.X),$($pt.Y)"
}

function Send-Click($x, $y) {
    [Win32]::SetCursorPos($x, $y) | Out-Null
    Start-Sleep -m 10
    [Win32]::mouse_event([Win32]::MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    [Win32]::mouse_event([Win32]::MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
}

if ($args.Count -eq 0) {
    Write-Host "Commands: mouse:get, mouse:move:x:y, mouse:click:x:y, type:text, key:name"
    exit 0
}

$cmd = $args[0]
switch -regex ($cmd) {
    "^mouse:get$" { Get-MousePos }
    "^mouse:move:(\d+):(\d+)$" { [Win32]::SetCursorPos($Matches[1], $Matches[2]) }
    "^mouse:click:(\d+):(\d+)$" { Send-Click $Matches[1] $Matches[2] }
    "^type:(.+)$" { [Windows.Forms.SendKeys]::SendWait($Matches[1]) }
    "^key:(.+)$" { $k=@{Enter="{ENTER}";Tab="{TAB}";Esc="{ESC}";Space=" "}[$Matches[1]]; if($k) {[Windows.Forms.SendKeys]::SendWait($k)} }
}
