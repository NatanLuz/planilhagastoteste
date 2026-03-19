param(
    [string]$PythonCommand = "python",
    [string]$Version,
    [switch]$CreateTag,
    [switch]$PushTag,
    [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"
function Get-LatestSemverTag {
    $tag = git tag --list "v*" --sort=-version:refname | Select-Object -First 1
    if ([string]::IsNullOrWhiteSpace($tag)) {
        return $null
    }
    return $tag.Trim()
}

function Get-NextPatchVersion([string]$tag) {
    if ([string]::IsNullOrWhiteSpace($tag)) {
        return "v0.1.0"
    }

    if ($tag -notmatch "^v(\d+)\.(\d+)\.(\d+)$") {
        throw "Tag no formato invalido: $tag. Use semver (ex: v1.2.3)."
    }

    $major = [int]$Matches[1]
    $minor = [int]$Matches[2]
    $patch = [int]$Matches[3] + 1

    return "v$major.$minor.$patch"
}

function Ensure-Version([string]$inputVersion) {
    if (-not [string]::IsNullOrWhiteSpace($inputVersion)) {
        $v = $inputVersion.Trim()
        if (-not $v.StartsWith("v")) {
            $v = "v$v"
        }

        if ($v -notmatch "^v(\d+)\.(\d+)\.(\d+)$") {
            throw "Version '$v' invalida. Use semver (ex: v1.2.3)."
        }

        return $v
    }

    $latest = Get-LatestSemverTag
    return Get-NextPatchVersion $latest
}

function Ensure-CleanWorkingTree {
    $status = git status --porcelain
    if (-not [string]::IsNullOrWhiteSpace($status)) {
        throw "Working tree nao esta limpo. Commit/stash antes de gerar release."
    }
}

$resolvedVersion = Ensure-Version $Version
Write-Host "Versao de release: $resolvedVersion"

Ensure-CleanWorkingTree

if ($CreateTag) {
    $existing = git tag --list $resolvedVersion
    if (-not [string]::IsNullOrWhiteSpace($existing)) {
        throw "Tag $resolvedVersion ja existe."
    }

    git tag -a $resolvedVersion -m "Release $resolvedVersion"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    Write-Host "Tag criada: $resolvedVersion"

    if ($PushTag) {
        git push origin $resolvedVersion
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        Write-Host "Tag enviada para origin: $resolvedVersion"
    }
}

if (-not $SkipBuild) {
    & .\build_exe.ps1 -PythonCommand $PythonCommand -Version $resolvedVersion
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

$appName = "ControleFinanceiro"
$fileSafeVersion = $resolvedVersion.TrimStart("v")
$versionedExe = Join-Path "dist" "$appName-$fileSafeVersion.exe"
$zipPath = Join-Path "dist" "$appName-$fileSafeVersion-win64.zip"

$releaseDir = Join-Path "releases" $resolvedVersion
if (Test-Path $releaseDir) { Remove-Item $releaseDir -Recurse -Force }
New-Item -ItemType Directory -Path $releaseDir | Out-Null

if (Test-Path $versionedExe) { Copy-Item $versionedExe (Join-Path $releaseDir (Split-Path $versionedExe -Leaf)) -Force }
if (Test-Path $zipPath) { Copy-Item $zipPath (Join-Path $releaseDir (Split-Path $zipPath -Leaf)) -Force }

$checksumsPath = Join-Path $releaseDir "SHA256SUMS.txt"
$hashLines = @()
if (Test-Path (Join-Path $releaseDir (Split-Path $versionedExe -Leaf))) {
    $h = Get-FileHash (Join-Path $releaseDir (Split-Path $versionedExe -Leaf)) -Algorithm SHA256
    $hashLines += "$($h.Hash)  $($h.Path | Split-Path -Leaf)"
}
if (Test-Path (Join-Path $releaseDir (Split-Path $zipPath -Leaf))) {
    $h = Get-FileHash (Join-Path $releaseDir (Split-Path $zipPath -Leaf)) -Algorithm SHA256
    $hashLines += "$($h.Hash)  $($h.Path | Split-Path -Leaf)"
}
$hashLines | Set-Content $checksumsPath

$notesPath = Join-Path $releaseDir "RELEASE_NOTES.md"
@(
    "# Release $resolvedVersion",
    "",
    "## Artefatos",
    "- $appName-$fileSafeVersion.exe",
    "- $appName-$fileSafeVersion-win64.zip",
    "- SHA256SUMS.txt",
    "",
    "## Checklist",
    "- [ ] Testes executados (pytest)",
    "- [ ] Build do executavel gerado",
    "- [ ] Changelog/README atualizado"
) | Set-Content $notesPath

Write-Host "Release pronta em: $releaseDir"
Write-Host "Arquivos gerados:"
Get-ChildItem $releaseDir | Select-Object -ExpandProperty Name | ForEach-Object { Write-Host "- $_" }
