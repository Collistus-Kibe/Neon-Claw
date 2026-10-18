# NemoClaw PowerShell Launcher
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
python "$ScriptDir\nemoclaw.py" @args
