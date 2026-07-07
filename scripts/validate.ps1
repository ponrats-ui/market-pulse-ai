Set-StrictMode -Version Latest
$root = Split-Path -Parent $PSScriptRoot
Set-Location "$root\frontend"
npm run build
Set-Location "$root"
git status --short
