$RepoDir = $PSScriptRoot

# Define all possible PowerShell profile paths
$ProfilePaths = @(
    "$HOME\Documents\PowerShell\Microsoft.PowerShell_profile.ps1",          # PowerShell 7+
    "$HOME\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1"    # PowerShell 5.1
)

$StartMark = "# --- BEGIN GWT CONFIG ---"
$EndMark = "# --- END GWT CONFIG ---"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "       GWT Uninstall Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ProfilesToClean = @()

foreach ($ProfilePath in $ProfilePaths) {
    if (Test-Path $ProfilePath) {
        $Content = Get-Content $ProfilePath -Raw -ErrorAction SilentlyContinue
        
        # Check if gwt config exists
        if ($Content -match $StartMark -or $Content -match "gwt\.ps1") {
            $ProfilesToClean += $ProfilePath
        }
    }
}

if ($ProfilesToClean.Count -eq 0) {
    Write-Host "⚠️  No gwt configuration found in any PowerShell profile." -ForegroundColor Yellow
    Write-Host ""
    exit 0
}

# Show what will be removed
Write-Host "📋 The following configuration will be removed:" -ForegroundColor Yellow
Write-Host ""

foreach ($ProfilePath in $ProfilesToClean) {
    Write-Host "📄 File: $ProfilePath" -ForegroundColor Cyan
    Write-Host "   Content to be removed:" -ForegroundColor Gray
    Write-Host "   ─────────────────────────────────────" -ForegroundColor DarkGray
    
    $Lines = Get-Content $ProfilePath -ErrorAction SilentlyContinue
    $InBlock = $false
    
    foreach ($Line in $Lines) {
        if ($Line -eq $StartMark) { $InBlock = $true }
        
        if ($InBlock) {
            Write-Host "   │ $Line" -ForegroundColor Red
        } elseif ($Line -match "gwt\.ps1") {
            Write-Host "   │ $Line" -ForegroundColor Red
        }
        
        if ($Line -eq $EndMark) { $InBlock = $false }
    }
    
    Write-Host "   ─────────────────────────────────────" -ForegroundColor DarkGray
    Write-Host ""
}

# Ask for confirmation
Write-Host "⚠️  This action will:" -ForegroundColor Yellow
Write-Host "   1. Create a backup of each profile file (.bak)" -ForegroundColor Gray
Write-Host "   2. Remove the gwt configuration blocks shown above" -ForegroundColor Gray
Write-Host ""

$Confirm = Read-Host "❓ Are you sure you want to continue? (y/N)"

if ($Confirm -ne "y" -and $Confirm -ne "Y") {
    Write-Host ""
    Write-Host "❌ Uninstall cancelled." -ForegroundColor Red
    exit 0
}

Write-Host ""

# Perform the uninstall
$UpdatedCount = 0

foreach ($ProfilePath in $ProfilesToClean) {
    Write-Host "🔧 Removing gwt from $ProfilePath ..." -ForegroundColor Cyan
    
    # Backup
    $BackupPath = "$ProfilePath.bak"
    Copy-Item -Path $ProfilePath -Destination $BackupPath -Force
    Write-Host "   📦 Backup created: $BackupPath" -ForegroundColor Gray

    $Lines = Get-Content $ProfilePath -ErrorAction SilentlyContinue
    $NewLines = @()
    $Skip = $false

    if ($Lines) {
        foreach ($Line in $Lines) {
            if ($Line -eq $StartMark) { $Skip = $true }

            $IsLegacy = $Line -match "gwt\.ps1"

            if (-not $Skip -and -not $IsLegacy) {
                $NewLines += $Line
            }

            if ($Line -eq $EndMark) { $Skip = $false }
        }
    }

    # Remove trailing empty lines
    while ($NewLines.Count -gt 0 -and [string]::IsNullOrWhiteSpace($NewLines[-1])) {
        $NewLines = $NewLines[0..($NewLines.Count - 2)]
    }

    $NewLines | Set-Content -Path $ProfilePath -Encoding UTF8
    Write-Host "   ✅ Removed" -ForegroundColor Green
    $UpdatedCount++
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ Uninstall complete!" -ForegroundColor Green
Write-Host "   Removed from $UpdatedCount profile(s)." -ForegroundColor Gray
Write-Host "   Restart PowerShell to apply changes." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Green
