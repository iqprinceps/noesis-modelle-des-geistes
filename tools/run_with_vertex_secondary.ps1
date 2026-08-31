[CmdletBinding()]
param(
    [switch]$Check,
    [Parameter(Position = 0)]
    [string]$Executable,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ArgumentList
)

$ErrorActionPreference = 'Stop'

$credentialRoot = Join-Path $env:USERPROFILE 'Documents\Codex\_credentials\gcloud-noesis-secondary'
$adcFile = Join-Path $credentialRoot 'application_default_credentials.json'
$gcloud = Join-Path $env:LOCALAPPDATA 'Google\Cloud SDK\google-cloud-sdk\bin\gcloud.ps1'

if (-not (Test-Path -LiteralPath $adcFile)) {
    throw "Das lokale Vertex-Sekundaerprofil ist nicht autorisiert: $credentialRoot"
}
if (-not (Test-Path -LiteralPath $gcloud)) {
    throw "Google Cloud CLI wurde nicht gefunden: $gcloud"
}

$env:CLOUDSDK_CONFIG = $credentialRoot
$env:GOOGLE_CLOUD_PROJECT = 'project-3e0eb782-5078-446c-845'
$env:GOOGLE_CLOUD_LOCATION = 'global'
$env:VERTEX_LOCATION = 'global'

if ($Check) {
    $accessToken = & $gcloud auth application-default print-access-token 2>$null
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($accessToken)) {
        throw 'Das lokale Vertex-Sekundaerprofil liefert kein gueltiges ADC-Token.'
    }
    Write-Output 'Vertex-Sekundaerprofil: OK'
    Write-Output "Projekt: $env:GOOGLE_CLOUD_PROJECT"
    Write-Output "Region: $env:GOOGLE_CLOUD_LOCATION"
    exit 0
}

if ([string]::IsNullOrWhiteSpace($Executable)) {
    throw 'Executable fehlt. Beispiel: pwsh -File tools/run_with_vertex_secondary.ps1 python tools/generate_ep08_vertex.py'
}

& $Executable @ArgumentList
exit $LASTEXITCODE
