$RepoDir = $PSScriptRoot
$ScriptPath = Join-Path $RepoDir "shell\gwt.ps1"

# Define all possible PowerShell profile paths
$ProfilePaths = @(
    "$HOME\Documents\PowerShell\Microsoft.PowerShell_profile.ps1",          # PowerShell 7+
    "$HOME\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1"    # PowerShell 5.1
)

$StartMark = "# --- BEGIN GWT CONFIG ---"
$EndMark = "# --- END GWT CONFIG ---"

$UpdatedCount = 0

foreach ($ProfilePath in $ProfilePaths) {
    # Check if this PowerShell version is installed by checking if the directory exists
    $ProfileDir = Split-Path -Parent $ProfilePath

    if (Test-Path $ProfileDir) {
        Write-Host "🔧 Configuring gwt to $ProfilePath ..." -ForegroundColor Cyan

        if (-not (Test-Path $ProfilePath)) {
            New-Item -Type File -Path $ProfilePath -Force | Out-Null
        }

        $Lines = Get-Content $ProfilePath -ErrorAction SilentlyContinue
        $NewLines = @()
        $Skip = $false

        if ($Lines) {
            foreach ($Line in $Lines) {
                # Check for block markers
                if ($Line -eq $StartMark) { $Skip = $true }

                # Check for legacy line (simple match) ensuring we don't duplicate removal
                $IsLegacy = $Line -match "gwt.ps1" -and (-not $Skip)

                if (-not $Skip -and -not $IsLegacy) {
                    $NewLines += $Line
                }

                if ($Line -eq $EndMark) { $Skip = $false }
            }
        }

        # Append new block
        $NewLines += ""
        $NewLines += $StartMark
        $NewLines += ". '$ScriptPath'"
        $NewLines += $EndMark

        $NewLines | Set-Content -Path $ProfilePath -Encoding UTF8

        Write-Host "   ✅ Updated" -ForegroundColor Green
        $UpdatedCount++
    }
}

if ($UpdatedCount -eq 0) {
    Write-Host "⚠️  No PowerShell profiles found." -ForegroundColor Yellow
} else {
    Write-Host "`n✅ Configuration complete! Updated $UpdatedCount profile(s)." -ForegroundColor Green
    Write-Host "   Restart your PowerShell or run: . `$PROFILE" -ForegroundColor Cyan
}