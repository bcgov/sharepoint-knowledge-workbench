# Validation Checklist

- Package is deployed in the intended App Catalog without package errors.
- App is installed on the intended test site.
- Exactly one matching list custom action exists by name or component ID.
- Command appears only on the intended list/library and in intended selection states.
- URL parameters reject blank, signed, decimal, zero, negative, and overflow values.
- React dialog/panel traps focus, labels controls, reports errors, and supports dismissal.
- Upload writes to the intended folder and assigns metadata using live internal names.
- Lookup and multi-lookup payloads use the correct `Id` shapes.
- Duplicate filenames use deterministic suffixes without overwriting existing files.
- Metadata failure compensates only the newly uploaded file.
- Success is visible before the panel closes or the list refreshes.
- `-Remove` hides the command without deleting the package, app, files, or list data.
