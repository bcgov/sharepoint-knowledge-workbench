# Site Navigation & Chrome Architecture Summary — {{SITE_NAME}}

> **Source Site**: `{{SITE_URL}}`
> **Analysis Date**: {{DATE}}
> **Subwebs Scanned**: {{TOTAL_WEBS}}
> **Global Navigation Nodes**: {{TOP_NAV_COUNT}}
> **Quick Launch Nodes**: {{QUICK_LAUNCH_COUNT}}

---

## 1. Executive Summary

This report evaluates classic site navigation structures, breadcrumbs, locale settings, and master page chrome configurations extracted across all site collection webs.

---

## 2. Navigation Architecture Breakdown

| Navigation Component | Total Nodes | Target Modern SharePoint Equivalent | Modernization Strategy |
|---|---|---|---|
| **Top Navigation Bar** | {{TOP_NAV_COUNT}} | Modern Global / Hub Navigation | Native Hub / Global Nav Bar |
| **Quick Launch Navigation** | {{QUICK_LAUNCH_COUNT}} | Modern Left Navigation | Modern Left Navigation Bar |
| **Master Page Chrome** | Standard | Modern Communication Site | Modern Site Header & Footer |

---

## 3. Top Navigation Structure Matrix

| # | Node Title | Target URL | Sub-Nodes | Modern Navigation Mapping |
|---|---|---|---|---|
{{NAV_ROWS}}

---

## 4. Follow-up Review Guidance

- Standard links: re-create in modern hub / global navigation.
- Sub-site links: map to corresponding modern site collection URLs post-migration.
