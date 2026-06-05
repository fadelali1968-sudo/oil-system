# تثبيت اختصار نظام المشتريات النفطية
$chromePaths = @(
  'C:\Program Files\Google\Chrome\Application\chrome.exe',
  'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
  ($env:LOCALAPPDATA + '\Google\Chrome\Application\chrome.exe')
)
$chrome = $chromePaths | Where-Object { Test-Path $_ } | Select-Object -First 1

if (-not $chrome) {
  Write-Host 'خطأ: Google Chrome غير موجود على هذا الجهاز.' -ForegroundColor Red
  Write-Host 'يرجى تثبيت Chrome اولاً ثم اعادة تشغيل هذا الملف.' -ForegroundColor Yellow
  Read-Host 'اضغط Enter للخروج'
  exit 1
}

# نسخ الأيقونة إلى مكان ثابت
$iconDir = "$env:PUBLIC\OilSystem"
if (-not (Test-Path $iconDir)) { New-Item -ItemType Directory -Path $iconDir | Out-Null }
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Copy-Item -Path "$scriptDir\app.ico" -Destination "$iconDir\app.ico" -Force

# إنشاء الاختصار على سطح المكتب
$sh = New-Object -ComObject WScript.Shell
$desktop = [Environment]::GetFolderPath('Desktop')
$lnk = $sh.CreateShortcut($desktop + '\نظام المشتريات النفطية.lnk')
$lnk.TargetPath = $chrome
$lnk.Arguments = '--app="https://fadelali1968-sudo.github.io/oil-system/" --start-maximized'
$lnk.IconLocation = "$iconDir\app.ico,0"
$lnk.Save()

Write-Host ''
Write-Host '===========================================' -ForegroundColor Cyan
Write-Host '   تم تثبيت الاختصار بنجاح!' -ForegroundColor Green
Write-Host '   الاختصار موجود الآن على سطح المكتب.' -ForegroundColor Green
Write-Host '===========================================' -ForegroundColor Cyan
Write-Host ''
Read-Host 'اضغط Enter للخروج'
