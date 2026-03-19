param(
    [string]$PythonCommand = "python",
    [string]$Version = "dev",
    [string]$AppName = "ControleFinanceiro"
)

$ErrorActionPreference = "Stop"

Write-Host "[1/3] Instalando dependencias de build..."
& $PythonCommand -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $PythonCommand -m pip install -r requirements-dev.txt
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "[2/3] Limpando artefatos antigos..."
if (Test-Path "build") { Remove-Item "build" -Recurse -Force }
if (Test-Path "dist") { Remove-Item "dist" -Recurse -Force }

Write-Host "[3/3] Gerando executavel..."
& $PythonCommand -m PyInstaller --noconfirm --clean --windowed --name $AppName --collect-all customtkinter --collect-all matplotlib app.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$exePath = Join-Path "dist" "$AppName\$AppName.exe"
if (-not (Test-Path $exePath)) {
    throw "Executavel nao encontrado em $exePath"
}

$versionNormalized = $Version.Trim()
if ([string]::IsNullOrWhiteSpace($versionNormalized)) {
    $versionNormalized = "dev"
}

$versionFileSafe = $versionNormalized.TrimStart("v")
$versionedExe = Join-Path "dist" "$AppName-$versionFileSafe.exe"
Copy-Item $exePath $versionedExe -Force

$zipPath = Join-Path "dist" "$AppName-$versionFileSafe-win64.zip"
if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
Compress-Archive -Path (Join-Path "dist" "$AppName\*") -DestinationPath $zipPath

Write-Host "Concluido."
Write-Host "Executavel principal: $exePath"
Write-Host "Executavel versionado: $versionedExe"
Write-Host "Pacote zip: $zipPath"
