param(
    [Parameter(Mandatory = $true)] [string] $Image,
    [Parameter(Mandatory = $true)] [string] $RestoreImage,
    [Parameter(Mandatory = $true)] [string] $ExpectedCurrentSha256,
    [Parameter(Mandatory = $true)] [switch] $AuthorizeFlash,
    [int] $AdapterKHz = 950
)

$ErrorActionPreference = "Stop"
if (-not $AuthorizeFlash) { throw "Refusing to flash without -AuthorizeFlash." }

$openOcd = "C:\ProgramData\chocolatey\bin\openocd.exe"
if (-not (Test-Path -LiteralPath $openOcd)) {
    $openOcd = (Get-Command openocd -ErrorAction Stop).Source
}
$imagePath = (Resolve-Path -LiteralPath $Image).Path
$restorePath = (Resolve-Path -LiteralPath $RestoreImage).Path
$expected = $ExpectedCurrentSha256.Trim().ToUpperInvariant()
$privateRoot = Join-Path $PSScriptRoot "..\firmware\private"
New-Item -ItemType Directory -Path $privateRoot -Force | Out-Null
$preflash = Join-Path $privateRoot ("preflash_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".bin")

function Invoke-OpenOcd([string] $commands) {
    & $openOcd -f interface/stlink.cfg -f target/stm32h7x.cfg `
        -c "adapter speed $AdapterKHz" -c $commands
    if ($LASTEXITCODE -ne 0) { throw "OpenOCD failed with exit code $LASTEXITCODE." }
}

Write-Host "Reading a private pre-flash recovery image..."
Invoke-OpenOcd "init; reset halt; dump_image {$preflash} 0x08000000 0x200000; reset run; shutdown"
$actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $preflash).Hash.ToUpperInvariant()
if ($actual -ne $expected) {
    throw "Current flash hash $actual does not match authorized hash $expected. No flash was performed."
}

Write-Host "Current image verified: $actual"
Write-Host "New image:             $((Get-FileHash -Algorithm SHA256 -LiteralPath $imagePath).Hash)"
Write-Host "Recovery image:        $((Get-FileHash -Algorithm SHA256 -LiteralPath $restorePath).Hash)"
try {
    Invoke-OpenOcd "init; reset halt; program {$imagePath} 0x08000000 verify reset; shutdown"
    Write-Host "Flash and verify completed. Recovery copy remains at $preflash"
}
catch {
    Write-Warning "New firmware flash failed. Attempting immediate vendor recovery."
    Invoke-OpenOcd "init; reset halt; program {$restorePath} 0x08000000 verify reset; shutdown"
    throw
}
