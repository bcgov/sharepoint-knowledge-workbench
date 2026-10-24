# Tailwind CSS Integration Guide for SharePoint Framework (SPFx 1.20+)

## Overview

Modern SharePoint Framework projects (SPFx 1.20+) use **Rushstack Heft** and Webpack 5 as their primary build orchestrator instead of legacy Gulp tasks. Integrating Tailwind CSS alongside Microsoft Fluent UI 8/9 requires a clean approach that avoids Webpack ejecting, prevents style leaking across web parts, and respects SharePoint theme tokens.

---

## Architectural Approaches

### Pattern A: Tailwind CLI Pre-Processing (Recommended for Production & CI/CD)

The most resilient, decoupled approach across SPFx 1.20–1.22 is running the Tailwind CLI compiler to generate a dedicated, minified CSS artifact before the Heft build bundles it.

```text
┌────────────────────────┐      Tailwind CLI       ┌────────────────────────┐      Heft / Webpack      ┌────────────────────────┐
│ src/.../tailwind.css   │ ───────────────────────► │ tailwind.output.css    │ ───────────────────────► │ Web Part .sppkg Bundle │
│ (@tailwind directives) │  (Scans TSX for classes) │ (Minified compiled CSS)│  (Standard CSS Import)   │ (Ready for deployment) │
└────────────────────────┘                          └────────────────────────┘                          └────────────────────────┘
```

#### 1. Install Toolchain Dependencies

```bash
npm install -D tailwindcss@3 postcss autoprefixer
```

#### 2. Root Configuration: `tailwind.config.js`

Ensure class scoping is isolated to your web parts to avoid styling conflicts with SharePoint Modern Chrome:

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{ts,tsx,html}'
  ],
  corePlugins: {
    preflight: false, // Disabling preflight prevents Tailwind reset styles from breaking SharePoint page layout
  },
  theme: {
    extend: {
      colors: {
        spPrimary: 'var(--primaryColor, #0078d4)',
        spBodyText: 'var(--bodyText, #323130)',
        spBodyBg: 'var(--bodyBackground, #ffffff)',
      }
    },
  },
  plugins: [],
}
```

> [!IMPORTANT]
> **Preflight setting:** Set `corePlugins: { preflight: false }`. Tailwind's default Preflight includes CSS global resets (e.g. `margin: 0` on `h1-h6` and buttons) which can distort native SharePoint site headers and quick-launch navigation.

#### 3. Source Styles: `src/webparts/<webPartName>/style/tailwind.css`

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

#### 4. NPM Build Scripts in `package.json`

Add pre-build and watch commands:

```json
{
  "scripts": {
    "build:tailwind": "tailwindcss -i ./src/webparts/<webPartName>/style/tailwind.css -o ./src/webparts/<webPartName>/style/tailwind.output.css --minify",
    "watch:tailwind": "tailwindcss -i ./src/webparts/<webPartName>/style/tailwind.css -o ./src/webparts/<webPartName>/style/tailwind.output.css --watch",
    "build": "npm run build:tailwind && heft test --clean --production && heft package-solution --production",
    "start": "heft start --clean"
  }
}
```

#### 5. Import in the Web Part Class

In `<WebPartName>WebPart.ts`:

```typescript
import './style/tailwind.output.css';
import './style/style.std.css';
```

---

## Coexistence with Microsoft Fluent UI

When building rich enterprise SPFx components:
1. **Layout & Grid**: Use Tailwind for container flexboxes, grid systems, spacing, shadows, and badges.
2. **Interactive UI Controls**: Use `@fluentui/react` for Complex Inputs, DetailsList, Dropdowns, DatePickers, and CommandBars.
3. **Theme Harmonization**: Pass `this._currentTheme` into Fluent UI components and use CSS variables / `getPivotStyles(theme)` for seamless background adaptation across light/dark section colors.