$ErrorActionPreference = 'Stop'
$windowsLocal = Join-Path ([Environment]::GetFolderPath('UserProfile')) 'AppData/Local'
# The Codex Windows package can redirect LocalAppData when installing Hermes.
$codexLocal = Join-Path $windowsLocal 'Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local'
$hermesRoot = @($codexLocal, $env:LOCALAPPDATA, $windowsLocal) | ForEach-Object {
    Join-Path $_ 'hermes'
} | Where-Object {
    (Test-Path -LiteralPath (Join-Path $_ 'netguard-runtime/Scripts/hermes.exe') -PathType Leaf) -and
    (Test-Path -LiteralPath (Join-Path $_ 'netguard-profile/.env') -PathType Leaf)
} | Select-Object -First 1
if (-not $hermesRoot) { throw 'No se encontro la instalacion de Hermes ni su perfil NETGUARD.' }
$profileDir = Join-Path $hermesRoot 'netguard-profile'
$hermesExe = Join-Path $hermesRoot 'netguard-runtime/Scripts/hermes.exe'
$ollamaExe = @($windowsLocal, $env:LOCALAPPDATA, $codexLocal) | ForEach-Object {
    Join-Path $_ 'Programs/Ollama/ollama.exe'
} | Where-Object { Test-Path -LiteralPath $_ -PathType Leaf } | Select-Object -First 1
if (-not $ollamaExe) { throw 'No se encontro Ollama en este usuario de Windows.' }
$pythonExe = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $pythonExe)) { $pythonExe = 'D:/escritorio/Syslog/NETGUARD-NOC/.venv/Scripts/python.exe' }
foreach ($file in @($hermesExe, $ollamaExe, $pythonExe, (Join-Path $profileDir '.env'))) {
    if (-not (Test-Path -LiteralPath $file -PathType Leaf)) { throw "Falta un componente local: $file" }
}
$keyLine = Get-Content -LiteralPath (Join-Path $profileDir '.env') | Where-Object { $_ -match '^API_SERVER_KEY=[a-f0-9]{64}$' } | Select-Object -First 1
if (-not $keyLine) { throw 'No se encontro la clave del perfil dedicado de Hermes.' }
$env:NETGUARD_HERMES_KEY = $keyLine.Substring('API_SERVER_KEY='.Length)
$env:NETGUARD_HERMES_MODEL = 'netguard'
$env:HERMES_HOME = $profileDir
$env:OLLAMA_HOST = '127.0.0.1:11434'

if (-not (Get-NetTCPConnection -LocalPort 11434 -State Listen -ErrorAction SilentlyContinue)) {
    Start-Process -FilePath $ollamaExe -ArgumentList 'serve' -WindowStyle Hidden
}
if (-not (Get-NetTCPConnection -LocalPort 8642 -State Listen -ErrorAction SilentlyContinue)) {
    Start-Process -FilePath $hermesExe -ArgumentList 'gateway' -WorkingDirectory $profileDir -WindowStyle Hidden
}
if (Get-NetTCPConnection -LocalPort 8002 -State Listen -ErrorAction SilentlyContinue) {
    Write-Host 'NETGUARD ya esta abierto. Abre esta direccion en tu navegador:'
    Write-Host 'http://127.0.0.1:8002/amenazas'
    Write-Host 'Si Hermes aparece desactivado, cierra la instancia anterior y vuelve a usar este archivo.'
    exit 0
}
Set-Location -LiteralPath $PSScriptRoot
Write-Host 'Abre esta direccion y elige Consultar con Hermes:'
Write-Host 'http://127.0.0.1:8002/amenazas'
& $pythonExe -m uvicorn app.main:app --host 127.0.0.1 --port 8002
exit $LASTEXITCODE
