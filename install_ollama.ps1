# PowerShell script to download and install Ollama
Write-Host "Downloading Ollama for Windows..."

# Create temp directory
$tempDir = "$env:TEMP\ollama_install"
if (!(Test-Path $tempDir)) {
    New-Item -ItemType Directory -Path $tempDir | Out-Null
}

# Download Ollama installer
$url = "https://github.com/ollama/ollama/releases/latest/download/OllamaSetup.exe"
$output = "$tempDir\OllamaSetup.exe"

Write-Host "Downloading from: $url"
Invoke-WebRequest -Uri $url -OutFile $output

Write-Host "Installing Ollama..."
Start-Process -FilePath $output -ArgumentList "/S" -Wait

# Clean up
Remove-Item $tempDir -Recurse -Force

Write-Host "Ollama installation completed!"
Write-Host "Please restart your terminal and run: python setup_ollama.py"