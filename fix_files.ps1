# fix_files.ps1
Write-Host "🔧 REPARANDO ESTRUCTURA DE ARCHIVOS..." -ForegroundColor Yellow

# 1. Renombrar carpeta adapters
if (Test-Path "core\adadpters") {
    Write-Host "📁 Renombrando adadpters -> adapters..." -ForegroundColor Cyan
    Rename-Item -Path "core\adadpters" -NewName "adapters"
}

# 2. Renombrar todos los _init_.py a __init__.py
Get-ChildItem -Recurse -Filter "_init_.py" | ForEach-Object {
    Write-Host "📄 Renombrando $($_.FullName)..." -ForegroundColor Cyan
    Rename-Item -Path $_.FullName -NewName "__init__.py"
}

# 3. Eliminar __pycache__
Get-ChildItem -Recurse -Directory -Filter "__pycache__" | ForEach-Object {
    Write-Host "🗑️ Eliminando $($_.FullName)..." -ForegroundColor Red
    Remove-Item -Recurse -Force -Path $_.FullName
}

# 4. Verificar estructura
Write-Host ""
Write-Host "✅ ESTRUCTURA REPARADA!" -ForegroundColor Green
Write-Host ""
Write-Host "📁 Carpetas encontradas:" -ForegroundColor Yellow
Get-ChildItem -Recurse -Directory | Select-Object FullName

Write-Host ""
Write-Host "🚀 Ahora ejecuta: python app.py" -ForegroundColor Green