# Mainstall Build Script
# This script builds the Mainstall executable using PyInstaller

Write-Host "=== Mainstall Build Script ===" -ForegroundColor Green
Write-Host ""

# Check if PyInstaller is installed
try {
    $null = Get-Command pyinstaller -ErrorAction Stop
    Write-Host "✓ PyInstaller found" -ForegroundColor Green
} catch {
    Write-Host "✗ PyInstaller not found. Installing..." -ForegroundColor Yellow
    pip install pyinstaller
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Failed to install PyInstaller" -ForegroundColor Red
        exit 1
    }
}

# Check if mainstall.py exists
if (-not (Test-Path "mainstall.py")) {
    Write-Host "✗ mainstall.py not found!" -ForegroundColor Red
    exit 1
}

# Check if spec file exists
if (-not (Test-Path "mainstall.spec")) {
    Write-Host "✗ mainstall.spec not found!" -ForegroundColor Red
    exit 1
}

# Check if icon exists
if (-not (Test-Path "assets\mainstall.ico")) {
    Write-Host "⚠ Warning: mainstall.ico not found in assets folder" -ForegroundColor Yellow
    Write-Host "  The executable will use a default icon" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Building Mainstall executable..." -ForegroundColor Cyan

# Clean previous builds
if (Test-Path "build") {
    Write-Host "Cleaning previous build..." -ForegroundColor Yellow
    Remove-Item "build" -Recurse -Force
}

if (Test-Path "dist") {
    Write-Host "Cleaning previous dist..." -ForegroundColor Yellow
    Remove-Item "dist" -Recurse -Force
}

# Build the executable
Write-Host "Running PyInstaller..." -ForegroundColor Cyan
pyinstaller mainstall.spec

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✓ Build completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Executable location: dist\Mainstall.exe" -ForegroundColor Cyan
    Write-Host "Size: $((Get-Item 'dist\Mainstall.exe').Length / 1MB) MB" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "You can now run the application using:" -ForegroundColor White
    Write-Host "  .\dist\Mainstall.exe" -ForegroundColor Yellow
    Write-Host "  or" -ForegroundColor White
    Write-Host "  .\run_mainstall.bat" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "✗ Build failed!" -ForegroundColor Red
    Write-Host "Check the error messages above for details." -ForegroundColor Red
    exit 1
} 
Write-Host "Build process completed." -ForegroundColor Green 