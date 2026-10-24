# Mode: Export Navigation

Download the live menu tree from SharePoint Online into JSON or console output.

## Command

```powershell
pwsh -File scripts/export-spo-navigation.ps1 -ConfigPath <config.psd1> -Format Json -OutputPath <path.json>
```

Omit `-Format` and `-OutputPath` to print the formatted navigation tree directly to the terminal.

## Parameters

- `-ConfigPath <string>`: Path to layer 1 connection configuration file (`config.psd1`).
- `-NavigationType <string>`: Either `TopNavigationBar` (default) or `QuickLaunch`.
- `-Format <string>`: `Json` or `Tree` (default `Tree`).
- `-OutputPath <string>`: Target JSON output path when `-Format Json`.
