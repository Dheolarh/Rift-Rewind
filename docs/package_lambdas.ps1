# PowerShell script to package the Rift Rewind backend for AWS Lambda
# Run this script from the 'backend' directory.

$ErrorActionPreference = "Stop"

# --- Configuration ---
$RequirementsFile = "requirements.txt"
$ServicesDir = "services"
$LambdasDir = "lambdas"
$ApiFile = "api.py"

# Output directory and staging area
$BuildDir = "build"
$StagingDir = "$BuildDir/lambda_staging"
$ZipFile = "$BuildDir/rift_rewind_lambda_package.zip"

# --- End Configuration ---

# 1. Clean up old build directory
if (Test-Path $BuildDir) {
    Write-Host "Cleaning up old build directory..."
    Remove-Item -Recurse -Force $BuildDir
}
New-Item -ItemType Directory -Force $BuildDir
New-Item -ItemType Directory -Force $StagingDir

# 2. Install dependencies to the staging folder
Write-Host "Installing Python dependencies from $RequirementsFile to $StagingDir..."
pip install --target $StagingDir -r $RequirementsFile
Write-Host "Dependencies installed."

# 3. Copy all shared application code to the staging folder
Write-Host "Copying 'services' directory..."
Copy-Item -Path $ServicesDir -Destination $StagingDir -Recurse -Force

Write-Host "Copying 'lambdas' directory (with all handlers)..."
Copy-Item -Path $LambdasDir -Destination $StagingDir -Recurse -Force

Write-Host "Copying 'api.py' file..."
Copy-Item -Path $ApiFile -Destination $StagingDir

# 4. Create the final Zip archive
Write-Host "Creating zip file at $ZipFile..."
Compress-Archive -Path "$StagingDir/*" -DestinationPath $ZipFile -Force

# 5. Clean up temporary staging directory
Write-Host "Cleaning up temporary staging directory..."
Remove-Item -Recurse -Force $StagingDir

Write-Host "--------------------------------------------------"
Write-Host "Lambda package created successfully: $ZipFile"
Write-Host ""
Write-Host "INSTRUCTIONS:"
Write-Host "1. Upload this single '$ZipFile' to BOTH of your Lambda functions."
Write-Host "2. Set the 'Handler' in AWS for each function:"
Write-Host "   - For your API Gateway function: orchestrator.lambda_handler"
Write-Host "   - For your async processor function: processor.lambda_handler"