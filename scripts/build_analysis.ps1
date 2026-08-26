param(
  [string]$Source = (Join-Path $PSScriptRoot '..\analysis\IROS_2026_Reasoning_Papers_Analysis.md'),
  [string]$Output = (Join-Path $PSScriptRoot '..\output\iros2026_reasoning_papers_analysis.html')
)

$ErrorActionPreference = 'Stop'

$sourcePath = (Resolve-Path -LiteralPath $Source).Path
$templatePath = Join-Path $PSScriptRoot 'analysis_template.html'
$outputPath = [System.IO.Path]::GetFullPath($Output)
$outputDir = Split-Path -Parent $outputPath
$tempDir = Join-Path ([System.IO.Path]::GetTempPath()) ('iros-analysis-' + [guid]::NewGuid().ToString('N'))

New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null

try {
  $utf8 = [System.Text.UTF8Encoding]::new($false)
  $markdown = [System.IO.File]::ReadAllText($sourcePath, $utf8)

  # Marked interprets underscores and list markers inside display math. Wrap
  # each LaTeX block in raw HTML before Markdown conversion so KaTeX receives
  # the original expression byte-for-byte.
  $protectedMarkdown = [regex]::Replace(
    $markdown,
    '(?ms)^\\\[\s*.*?\s*\\\]\r?$',
    { param($match) "`n<div class=`"math-block`">`n$($match.Value)`n</div>`n" }
  )

  $protectedPath = Join-Path $tempDir 'analysis.md'
  $fragmentPath = Join-Path $tempDir 'fragment.html'
  [System.IO.File]::WriteAllText($protectedPath, $protectedMarkdown, $utf8)

  & npx --yes marked@16.4.2 $protectedPath -o $fragmentPath
  if ($LASTEXITCODE -ne 0) { throw 'Markdown conversion failed.' }

  $fragment = [System.IO.File]::ReadAllText($fragmentPath, $utf8)
  $readingNote = '<div class="reading-note"><strong>분석 범위</strong> · IROS 2026 전체 프로그램 1,933편에서 reasoning 관련 검색 결과 64편을 분류한 문서입니다. 제목·세션·저자 키워드에 근거한 보수적 해석이며, 개별 논문의 초록·본문 리뷰와는 구분됩니다.</div>'
  $firstHeadingEnd = $fragment.IndexOf('</h1>')
  if ($firstHeadingEnd -ge 0) {
    $insertAt = $firstHeadingEnd + 5
    $fragment = $fragment.Insert($insertAt, "`n$readingNote")
  }
  $template = [System.IO.File]::ReadAllText($templatePath, $utf8)
  if (-not $template.Contains('<!--CONTENT-->')) { throw 'Template content marker is missing.' }

  $html = $template.Replace('<!--CONTENT-->', $fragment)
  [System.IO.File]::WriteAllText($outputPath, $html, $utf8)
  Write-Output "Built $outputPath"
}
finally {
  if (Test-Path -LiteralPath $tempDir) {
    Remove-Item -LiteralPath $tempDir -Recurse -Force
  }
}
