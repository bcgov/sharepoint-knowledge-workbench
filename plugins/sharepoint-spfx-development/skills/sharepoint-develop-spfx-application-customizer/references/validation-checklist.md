# Validation Checklist

- Package is deployed in the intended App Catalog without package errors.
- App is installed on the intended test site.
- Exactly one matching custom action exists by name or component id, at the intended scope.
- The UI renders once per page, including after in-app navigation, and is removed on disposal.
- The extension does not throw when the placeholder is missing.
- Menu or content text and URLs from the site are rendered as text; unsafe URL schemes are rejected.
- Keyboard operation, focus order, focus ring, `aria-expanded` and Escape behaviour work.
- Layout works at narrow widths and does not cover page content or the suite bar.
- No console errors; a failed data fetch degrades to the last good content.
- `-Remove` hides the UI without deleting the package, app, or any content.
