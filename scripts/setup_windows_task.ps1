# Windows タスクスケジューラに監視タスクを登録するスクリプト
# 管理者権限 PowerShell で実行: .\scripts\setup_windows_task.ps1

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$PythonExe = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$MainScript = Join-Path $ProjectRoot "main.py"
$TaskName = "SE-Recruit-Monitor"

if (-not (Test-Path $PythonExe)) {
    Write-Host "仮想環境が見つかりません。先に以下を実行してください:" -ForegroundColor Yellow
    Write-Host "  cd $ProjectRoot"
    Write-Host "  python -m venv .venv"
    Write-Host "  .venv\Scripts\pip install -r requirements.txt"
    exit 1
}

if (-not (Test-Path (Join-Path $ProjectRoot ".env"))) {
    Write-Host ".env ファイルが見つかりません。.env.example をコピーして設定してください。" -ForegroundColor Yellow
    exit 1
}

$Action = New-ScheduledTaskAction `
    -Execute $PythonExe `
    -Argument "`"$MainScript`" --once" `
    -WorkingDirectory $ProjectRoot

$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration ([TimeSpan]::MaxValue)

$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 10)

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description "6社SE職の二次応募/追加募集を監視しメール通知" `
    -Force

Write-Host "タスク '$TaskName' を登録しました（1時間ごとに実行）。" -ForegroundColor Green
Write-Host "確認: Get-ScheduledTask -TaskName '$TaskName'"
Write-Host "手動実行: Start-ScheduledTask -TaskName '$TaskName'"
Write-Host "削除: Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false"
