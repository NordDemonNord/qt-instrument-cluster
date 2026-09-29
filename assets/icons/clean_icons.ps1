# clean_icons.ps1
# Removes background rects and corner-frame groups from SVG icons.
# Run from assets/icons folder:
#     powershell -ExecutionPolicy Bypass -File clean_icons.ps1
# Originals are saved as *.svg.bak

$files = Get-ChildItem -Filter *.svg
if ($files.Count -eq 0) {
    Write-Host "No SVG files found. Run from assets/icons folder."
    exit
}

$totalRemoved = 0
Write-Host "Cleaning icons..."

foreach ($file in $files) {
    $text = Get-Content $file.FullName -Raw -Encoding UTF8

    $svgW = 0.0; $svgH = 0.0
    if ($text -match 'viewBox="[\d.\s]*?\s([\d.]+)\s+([\d.]+)"') {
        $svgW = [double]$matches[1]; $svgH = [double]$matches[2]
    } elseif ($text -match '<svg[^>]*\bwidth="([\d.]+)"' ) {
        $svgW = [double]$matches[1]
        if ($text -match '<svg[^>]*\bheight="([\d.]+)"') { $svgH = [double]$matches[1] }
    }

    $removed = 0
    $newText = $text

    # 1. Remove decorative corner-frame group <g stroke="#999">...</g>
    $framePattern = '(?s)<g\s+stroke="#999"[^>]*>.*?</g>'
    $frameMatches = [regex]::Matches($newText, $framePattern)
    if ($frameMatches.Count -gt 0) {
        $newText = [regex]::Replace($newText, $framePattern, '')
        $removed += $frameMatches.Count
    }

    # 2. Remove full-area background rects
    $rectMatches = [regex]::Matches($newText, '<rect\b[^>]*/>')
    for ($i = $rectMatches.Count - 1; $i -ge 0; $i--) {
        $tag = $rectMatches[$i].Value

        $rw = 0.0; $rh = 0.0
        if ($tag -match 'width="([\d.]+)"')  { $rw = [double]$matches[1] }
        if ($tag -match 'height="([\d.]+)"') { $rh = [double]$matches[1] }

        $covers = ($svgW -gt 0 -and $svgH -gt 0 -and $rw -ge (0.9*$svgW) -and $rh -ge (0.9*$svgH))

        $fillVal = ""
        if ($tag -match 'fill="([^"]*)"') { $fillVal = $matches[1].Trim().ToLower() }
        $noVisibleFill = ($fillVal -eq "" -or $fillVal -eq "#000" -or $fillVal -eq "#000000" -or $fillVal -eq "black")

        if ($covers -and $noVisibleFill) {
            $start = $rectMatches[$i].Index
            $len = $rectMatches[$i].Length
            $newText = $newText.Substring(0, $start) + $newText.Substring($start + $len)
            $removed++
        }
    }

    if ($removed -gt 0) {
        $bak = $file.FullName + ".bak"
        if (-not (Test-Path $bak)) {
            Copy-Item $file.FullName $bak
        }
        Set-Content -Path $file.FullName -Value $newText -Encoding UTF8 -NoNewline
        Write-Host ("  {0}: removed {1}" -f $file.Name, $removed)
        $totalRemoved += $removed
    }
}

Write-Host ""
Write-Host ("Done. Total removed: {0}" -f $totalRemoved)
Write-Host "Originals saved as *.svg.bak"
