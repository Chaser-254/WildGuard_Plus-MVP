# WildGuard MVP - Miniconda Installation & Environment Setup Script
# Run this script to download Miniconda, install it, and create the conda environment

param(
    [string]$GPU = "none"  # Options: "none" (CPU), "cu118" (CUDA 11.8), "cu121" (CUDA 12.1)
)

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "  WildGuard MVP - Conda Environment Setup" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan

# Step 1: Download Miniconda
Write-Host "`n[1/4] Downloading Miniconda3..." -ForegroundColor Yellow
$minicondaUrl = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
$minicondaPath = "$env:USERPROFILE\Downloads\Miniconda3-latest-Windows-x86_64.exe"

if (-not (Test-Path $minicondaPath)) {
    Write-Host "Downloading from $minicondaUrl..." -ForegroundColor Gray
    try {
        Invoke-WebRequest -Uri $minicondaUrl -OutFile $minicondaPath -ErrorAction Stop
        Write-Host "✓ Download complete" -ForegroundColor Green
    }
    catch {
        Write-Host "✗ Download failed: $_" -ForegroundColor Red
        exit 1
    }
}
else {
    Write-Host "✓ Miniconda installer already exists at $minicondaPath" -ForegroundColor Green
}

# Step 2: Run Miniconda Installer
Write-Host "`n[2/4] Installing Miniconda..." -ForegroundColor Yellow
Write-Host "Please follow the installer prompts. Recommended settings:" -ForegroundColor Gray
Write-Host "  - Install for: Just Me (current user)" -ForegroundColor Gray
Write-Host "  - Installation path: Use default (usually C:\Users\YourName\miniconda3)" -ForegroundColor Gray
Write-Host "  - Add Miniconda to PATH: YES" -ForegroundColor Gray
Write-Host "  - Register Miniconda as default Python: NO (optional)" -ForegroundColor Gray

Start-Process -FilePath $minicondaPath -Wait
Write-Host "✓ Installer completed" -ForegroundColor Green

# Step 3: Reinitialize conda (add to current shell)
Write-Host "`n[3/4] Initializing conda for PowerShell..." -ForegroundColor Yellow
$condaPath = "$env:USERPROFILE\miniconda3\Scripts\conda.exe"
if (Test-Path $condaPath) {
    & $condaPath init powershell
    Write-Host "✓ Conda initialized" -ForegroundColor Green
    Write-Host "Please restart PowerShell or run: &$PROFILE" -ForegroundColor Yellow
}
else {
    Write-Host "✗ Conda not found at expected location. Reopen PowerShell and run:" -ForegroundColor Red
    Write-Host "  conda create -n wildguard python=3.11 -y" -ForegroundColor Cyan
    exit 0
}

# Step 4: Create conda environment
Write-Host "`n[4/4] Creating conda environment 'wildguard' (Python 3.11)..." -ForegroundColor Yellow
& $condaPath create -n wildguard python=3.11 -y

Write-Host "`n===============================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "  1. Restart PowerShell (close and reopen)" -ForegroundColor Cyan
Write-Host "  2. Run: conda activate wildguard" -ForegroundColor Cyan

if ($GPU -eq "none") {
    Write-Host "  3. Run (CPU-only PyTorch):" -ForegroundColor Cyan
    Write-Host "     conda install -c pytorch pytorch torchvision torchaudio cpuonly -y" -ForegroundColor Cyan
}
elseif ($GPU -eq "cu118") {
    Write-Host "  3. Run (GPU with CUDA 11.8):" -ForegroundColor Cyan
    Write-Host "     conda install -c pytorch -c nvidia pytorch torchvision torchaudio pytorch-cuda=11.8 -y" -ForegroundColor Cyan
}
elseif ($GPU -eq "cu121") {
    Write-Host "  3. Run (GPU with CUDA 12.1):" -ForegroundColor Cyan
    Write-Host "     conda install -c pytorch -c nvidia pytorch torchvision torchaudio pytorch-cuda=12.1 -y" -ForegroundColor Cyan
}

Write-Host "  4. Run: pip install -r requirements.txt" -ForegroundColor Cyan
Write-Host "`nFor GPU support:" -ForegroundColor Yellow
Write-Host "  If you have an NVIDIA GPU:" -ForegroundColor Gray
Write-Host "    - Check CUDA version: nvidia-smi" -ForegroundColor Gray
Write-Host "    - Use cu118 or cu121 channel based on your CUDA version" -ForegroundColor Gray
