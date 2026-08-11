# Acceptance Criteria

- Builds a plan for copying an existing `.aspx` Site Page from one SPO site to
  another.
- Performs no SharePoint tenant I/O by default.
- Rejects non-`.aspx` page names.
- States that raw `.aspx` upload should be avoided for modern SPO pages.
- Keeps helper code in the plugin-level `scripts/` directory and exposes it to
  the skill through a file-level symlink.
