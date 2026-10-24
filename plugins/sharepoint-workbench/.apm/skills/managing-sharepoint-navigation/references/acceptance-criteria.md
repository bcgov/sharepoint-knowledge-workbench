# Acceptance criteria: sp-navigation-sync

- [ ] Export is read-only and prints a tree or writes snapshot JSON; it never writes to the site.
- [ ] Sync without `-Execute` makes no connection and changes nothing.
- [ ] `-Execute` without `-ConfirmToken PROVISION-SPO-NAV` fails before any connection.
- [ ] A non-DEV site is refused unless `-AllowNonDev` is passed.
- [ ] Validation reports every workbook error (gap, duplicate path, encoding, bad URL, missing leaf URL) and writes no plan.
- [ ] Re-running export, plan and diff after a successful sync yields only `unchanged` ops (idempotent).
- [ ] Nodes absent from the workbook are removed only with `-Prune`.
- [ ] A stale target (missing or retitled since the diff) aborts in preflight before any change.
- [ ] A backup of the live tree is saved before the first write; the first failure stops the run.
- [ ] Native "Edit navigation" still works on the provisioned nodes.
