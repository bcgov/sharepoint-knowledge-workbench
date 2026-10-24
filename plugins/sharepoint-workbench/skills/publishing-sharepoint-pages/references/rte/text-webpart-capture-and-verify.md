# Capture tenant markup and verify the edit round trip

Public documentation does not list the stored markup for several newer toolbar features
(custom font size, custom color, line spacing, paragraph spacing variants, new quote styles,
list styles). The editor is the source of truth: let it write the markup, then read it back.
PnP's own docs recommend the same "reverse engineer" approach.

PowerShell snippets below use PnP.PowerShell cmdlets; they were not executed by the skill
author — run against a test site first.

## 1. Build a vocabulary page by hand (once per tenant, repeat after Text web part updates)
Create a page `RTE-Vocabulary.aspx`. In **one** Text web part, add one labeled line per feature,
formatted only with the toolbar, e.g.:
- "H1", "H2", "H3" in each heading style; "Normal with spacing", "Normal without spacing"
- each quote style; monospaced
- font size 8, 12, 18, 28, 48, 72, 250 (typed); each theme color, a standard color, a custom hex color
- each highlight color; bold/italic/underline/strike/sup/sub
- align left/center/right/justify; indent ×1, ×2; line spacing 1.0/1.5/2.0; spacing before/after
- bullet disc/circle/square; numbered 1/A/a/I/i; numbered list starting at 5
- a link; one table per style (plain…column header, simple and themed) and per alignment
- one inline image, left/center/right
Publish.

## 2. Read the stored HTML
```powershell
Connect-PnPOnline -Url https://contoso.sharepoint.com/sites/test -Interactive -ClientId <app-id>
$page = Get-PnPPage -Identity "RTE-Vocabulary"
$page.EditorType            # expect CK5
$i = 0
foreach ($c in Get-PnPPageComponent -Page "RTE-Vocabulary") {
  if ($c.PSObject.Properties.Name -contains "Text") {   # text parts expose .Text
    $c.Text | Set-Content -Encoding utf8 ("capture-{0:D2}.html" -f $i++)
  }
}
```

## 3. Harvest into the allow-list
```bash
python scripts/sp_text_webpart_html.py harvest capture-*.html --vocab assets/rte-vocabulary.json --write
```
This adds every tag, class, style property and data-* attribute seen in the captures to the
`tenant` section of the vocabulary (marked as tenant-confirmed). Then update
[text-webpart-markup-vocabulary](text-webpart-markup-vocabulary.md), replacing **Capture** rows with the observed markup.

## 4. Lint generated HTML
```bash
python scripts/sp_text_webpart_html.py check generated.html --vocab assets/rte-vocabulary.json
```
Exit code 1 lists each element/class/style/attribute not in the allow-list.

## 5. Edit round-trip test (mandatory before bulk publishing)
```powershell
$sent = Get-Content generated.html -Raw
Add-PnPPage -Name "RoundTrip" -LayoutType Article
Add-PnPPageTextPart -Page "RoundTrip" -Text $sent
Set-PnPPage -Identity "RoundTrip" -Publish
# --> In the browser: open RoundTrip, Edit, type one character in the text part, Republish.
$after = (Get-PnPPageComponent -Page "RoundTrip" | Where-Object { $_.PSObject.Properties.Name -contains "Text" })[0].Text
$after | Set-Content -Encoding utf8 after.html
```
Diff `generated.html` vs `after.html` (e.g. `git diff --no-index --word-diff`). Expected
differences: the one typed character, whitespace, attribute order. Anything else (lost
classes, removed styles, rewritten tables) means that construct is not editor-native — fix the
mapping, or accept the editor's form and use *that* as the template.

Checking only the published view proves nothing; the stripping happens when the editor loads.

## Reading the stored HTML back
Page text parts are readable with PnP: `Connect-PnPOnline -Url <SiteUrl> -ClientId <ClientId> -Tenant <TenantId> -Interactive` (values from `config-spo-*.psd1` `Connection`), then `Get-PnPPage -Identity <Page>.aspx` and read `.Text` of each `PageText` control in `Sections[].Controls`. Announce the sign-in prompt to the user first. A capture page of one Text part per experiment (view, then edit and save, then read back) is the fastest evidence; the `RTE-Capture` run is logged in `text-web-part-html-sanitization.md`.
