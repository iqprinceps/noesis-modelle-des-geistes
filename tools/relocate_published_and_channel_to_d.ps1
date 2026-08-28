$ErrorActionPreference = 'Stop'

$workspaceRoot = 'C:\Users\iQPrinceps\Documents\Codex\Youtube Modelle des Geistes'
$channelRoot = 'C:\Users\iQPrinceps\Documents\Codex\YouTubeChannel'
$noesisChannelRoot = 'C:\Users\iQPrinceps\Documents\Codex\NOESIS Channel'
$destinationRoot = 'D:\Noesis'

$moves = @(
    @{ Source = "$workspaceRoot\06_PRODUCTION\EP01_KOZYREV"; Destination = "$destinationRoot\Published\DE\EP01_KOZYREV" },
    @{ Source = "$workspaceRoot\06_PRODUCTION\EP02_GATEWAY_V7"; Destination = "$destinationRoot\Published\DE\EP02_GATEWAY_V7" },
    @{ Source = "$workspaceRoot\06_PRODUCTION\EP03_PEAR"; Destination = "$destinationRoot\Published\DE\EP03_PEAR" },
    @{ Source = "$workspaceRoot\06_PRODUCTION\JUNG_SERIES_V1"; Destination = "$destinationRoot\Published\DE\JUNG_SERIES_V1" },
    @{ Source = "$workspaceRoot\07_ENGLISH_PRODUCTION\EP01_KOZYREV"; Destination = "$destinationRoot\Published\EN\EP01_KOZYREV" },
    @{ Source = "$workspaceRoot\07_ENGLISH_PRODUCTION\EP02_GATEWAY"; Destination = "$destinationRoot\Published\EN\EP02_GATEWAY" },
    @{ Source = "$channelRoot\episodes"; Destination = "$destinationRoot\Channel Media\YouTubeChannel\episodes" },
    @{ Source = "$channelRoot\series"; Destination = "$destinationRoot\Channel Media\YouTubeChannel\series" },
    @{ Source = "$noesisChannelRoot\folgen"; Destination = "$destinationRoot\Channel Media\NOESIS Channel\folgen" },
    @{ Source = "$noesisChannelRoot\social"; Destination = "$destinationRoot\Channel Media\NOESIS Channel\social" },
    @{ Source = "$noesisChannelRoot\werkbank"; Destination = "$destinationRoot\Channel Media\NOESIS Channel\werkbank" }
)

function Assert-SafePath {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string[]]$AllowedRoots
    )

    $full = [IO.Path]::GetFullPath($Path).TrimEnd('\')
    foreach ($root in $AllowedRoots) {
        $safeRoot = [IO.Path]::GetFullPath($root).TrimEnd('\')
        if ($full.StartsWith($safeRoot + '\', [StringComparison]::OrdinalIgnoreCase)) {
            return $full
        }
    }
    throw "Unsafe filesystem target: $full"
}

function Get-FileMap {
    param([Parameter(Mandatory = $true)][string]$Root)

    $map = @{}
    foreach ($file in Get-ChildItem -LiteralPath $Root -File -Recurse -Force) {
        $relative = $file.FullName.Substring($Root.Length + 1)
        $map[$relative] = $file.Length
    }
    return $map
}

foreach ($move in $moves) {
    $source = Assert-SafePath -Path $move.Source -AllowedRoots @($workspaceRoot, (Split-Path -Parent $channelRoot))
    $destination = Assert-SafePath -Path $move.Destination -AllowedRoots @($destinationRoot)

    $sourceItem = Get-Item -LiteralPath $source -Force
    if ($sourceItem.LinkType -eq 'Junction') {
        Write-Output "ALREADY_LINKED`t$source`t$($sourceItem.Target)"
        continue
    }

    if (-not $sourceItem.PSIsContainer) {
        throw "Source is not a directory: $source"
    }

    New-Item -ItemType Directory -Path $destination -Force | Out-Null
    Write-Output "COPY_START`t$source`t$destination"

    & robocopy.exe $source $destination /E /COPY:DAT /DCOPY:DAT /R:2 /W:1 /XJ /NFL /NDL /NP /NJH /NJS
    $copyCode = $LASTEXITCODE
    if ($copyCode -ge 8) {
        throw "Robocopy failed with exit code $copyCode for $source"
    }

    $sourceMap = Get-FileMap -Root $source
    $destinationMap = Get-FileMap -Root $destination
    if ($sourceMap.Count -ne $destinationMap.Count) {
        throw "File count mismatch for ${source}: $($sourceMap.Count) vs $($destinationMap.Count)"
    }

    foreach ($relative in $sourceMap.Keys) {
        if (-not $destinationMap.ContainsKey($relative)) {
            throw "Destination file missing: $destination\$relative"
        }
        if ($destinationMap[$relative] -ne $sourceMap[$relative]) {
            throw "Destination size mismatch: $destination\$relative"
        }
    }

    $sourceBytes = ($sourceMap.Values | Measure-Object -Sum).Sum
    $destinationBytes = ($destinationMap.Values | Measure-Object -Sum).Sum
    if ($sourceBytes -ne $destinationBytes) {
        throw "Total byte mismatch for $source"
    }

    Write-Output "COPY_VERIFIED`t$($sourceMap.Count) files`t$([math]::Round($sourceBytes / 1GB, 3)) GB"

    $sourceParent = Split-Path -Parent $source
    $sourceLeaf = Split-Path -Leaf $source
    $temporaryLeaf = "$sourceLeaf.__relocating__"
    $temporaryPath = Join-Path $sourceParent $temporaryLeaf
    if (Test-Path -LiteralPath $temporaryPath) {
        throw "Temporary relocation path already exists: $temporaryPath"
    }

    try {
        Rename-Item -LiteralPath $source -NewName $temporaryLeaf
    }
    catch {
        Write-Output "RELOCATION_DEFERRED_SOURCE_LOCKED`t$source`t$($_.Exception.Message)"
        continue
    }
    try {
        New-Item -ItemType Junction -Path $source -Target $destination | Out-Null
        $junction = Get-Item -LiteralPath $source -Force
        if ($junction.LinkType -ne 'Junction') {
            throw "Junction verification failed: $source"
        }
    }
    catch {
        if (Test-Path -LiteralPath $source) {
            Remove-Item -LiteralPath $source -Force
        }
        Rename-Item -LiteralPath $temporaryPath -NewName $sourceLeaf
        throw
    }

    Remove-Item -LiteralPath $temporaryPath -Recurse -Force
    Write-Output "RELOCATED`t$source`t$destination"
}

Get-PSDrive C, D |
    Select-Object Name, @{ Name = 'FreeGB'; Expression = { [math]::Round($_.Free / 1GB, 2) } } |
    Format-Table -AutoSize
