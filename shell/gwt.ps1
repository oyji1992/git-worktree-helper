# Wrapper for gwt.py (PowerShell)

# Determine repo + Python entry script
$script:GWT_SCRIPT_DIR = $PSScriptRoot
$script:GWT_REPO_DIR = Split-Path -Parent $script:GWT_SCRIPT_DIR
$script:GWT_PY_SCRIPT = Join-Path $script:GWT_REPO_DIR "src\gwt.py"

function gwt {
    param(
        [Parameter(ValueFromRemainingArguments=$true)]
        [string[]]$Args
    )

    # Use pre-defined script path
    $pyScript = $script:GWT_PY_SCRIPT

    if (-not (Test-Path $pyScript)) {
        Write-Error "❌ Cannot find gwt.py at: $pyScript"
        return
    }

    # Temp file for CD communication
    $tmpCdFile = [System.IO.Path]::GetTempFileName()
    
    # Set Env Var
    $env:GWT_CD_FILE = $tmpCdFile

    try {
        # Run Python
        # We need to pass arguments correctly.
        python $pyScript $Args
    }
    finally {
        # Check for CD request
        if (Test-Path $tmpCdFile) {
            $targetDir = Get-Content -Path $tmpCdFile -ErrorAction SilentlyContinue
            if (-not [string]::IsNullOrWhiteSpace($targetDir)) {
                # Trim whitespace
                $targetDir = $targetDir.Trim()
                if (Test-Path $targetDir) {
                    Set-Location -Path $targetDir
                }
            }
            Remove-Item -Path $tmpCdFile -ErrorAction SilentlyContinue
        }
        
        # Clean Env Var
        Remove-Item Env:\GWT_CD_FILE -ErrorAction SilentlyContinue
    }
}

# Register Auto-completion
if (Get-Command Register-ArgumentCompleter -ErrorAction SilentlyContinue) {
    Register-ArgumentCompleter -Native -CommandName gwt -ScriptBlock {
        param($wordToComplete, $commandAst, $cursorPosition)

        # Use pre-defined script path from outer scope
        $pyScript = $script:GWT_PY_SCRIPT
        if (-not $pyScript -or -not (Test-Path $pyScript)) {
            return
        }

        # Parse input
        $inputStr = $commandAst.ToString()
        $tokens = $inputStr.Split(" ", [System.StringSplitOptions]::RemoveEmptyEntries)
        $cmd = "gwt"
        $prev = ""
        
        # Determine if cursor is after the last token (completing new arg) or within a token
        # cursorPosition > inputStr.TrimEnd().Length means user typed space after last token
        $trimmedLen = $inputStr.TrimEnd().Length
        $isCompletingNewArg = $cursorPosition -gt $trimmedLen
        
        # Logic:
        # - If only "gwt" or "gwt sta<tab>" (completing subcommand), cmd = "gwt"
        # - If "gwt rv <tab>" (completing args for rv), cmd = "rv"
        # - If "gwt rv -t <tab>" (completing value for -t), cmd = "rv", prev = "-t"
        if ($tokens.Count -gt 1) {
            if ($tokens.Count -eq 2 -and -not $isCompletingNewArg) {
                # Completing subcommand: gwt stat<Cursor>
                $cmd = "gwt"
            } else {
                # Completing args: gwt rv <Cursor> or gwt rv -t <Cursor>
                $cmd = $tokens[1]
                if ($tokens.Count -gt 2) {
                    $prev = $tokens[$tokens.Count - 1]
                    if (-not $isCompletingNewArg) {
                        # Cursor is within last token, prev is the one before
                        $prev = $tokens[$tokens.Count - 2]
                    }
                }
            }
        }

        # Run Python
        # We catch output and return as strings
        try {
            $results = python $pyScript __complete --cmd=$cmd --cur=$wordToComplete --prev=$prev
            foreach ($res in $results) {
                # Split value:description
                $parts = $res -split ":", 2
                $val = $parts[0]
                $desc = if ($parts.Count -gt 1) { $parts[1] } else { $val }
                
                [System.Management.Automation.CompletionResult]::new($val, $val, 'ParameterValue', $desc)
            }
        } catch {
            # Silent fail on completion error
        }
    }
}
