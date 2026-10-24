# Shared static design-system assets for SharePoint Online

## Contents

- [Recommendation](#recommendation)
- [CDN privacy and URL considerations](#cdn-privacy-and-url-considerations)
- [Organization Assets Library](#organization-assets-library-is-a-different-feature)
- [Migration workflow contract](#migration-workflow-contract)
- [Microsoft sources](#microsoft-sources)

## Recommendation

For static HTML pages that share the same design-system CSS and font files,
publish approved shared assets once to an approved location on the target
SharePoint site, then reuse their verified URLs in later pages.
Do not upload another copy for every page. Keep the asset source, release or
version, destination URLs, and content hashes in the migration evidence so a
later run can verify that it is reusing the intended files.

Microsoft documents the SharePoint Online CDN as a way to serve static assets
from origins that may be a site, document library, or folder. A dedicated
library or folder can limit which files are included. CDN setup and origin
configuration are tenant-level administration decisions, not part of an
ordinary page migration. Do not enable or reconfigure a tenant CDN as an
implicit part of this workflow.

If an approved CDN origin is already configured, use its documented asset
URLs and verify the CSS and font files are included, retrievable, and
permitted for the intended audience. Otherwise, use an approved SharePoint
library/folder on the target site and verify real user access, content type,
and browser loading from the published HTML. A SharePoint URL is not proof
that anonymous or authenticated browser requests, CSS imports, or font
requests will work.

## CDN privacy and URL considerations

- Microsoft distinguishes public and private CDN origins. Content in a
  public origin is anonymously accessible; never put sensitive or
  organization-restricted content there. Treat publication to a public
  origin as a security and governance decision.
- Microsoft's guidance recommends limiting origins. Prefer an already
  approved shared origin rather than creating a new origin for each page.
- Do not hardcode a constructed CDN URL. Microsoft warns CDN URLs can change
  and recommends using the supported page-context mechanism for SharePoint
  pages. For standalone HTML files, use only the URL form approved and
  validated for the actual target.
- The current Microsoft 365 CDN documentation lists `.css`, `.ttf`, `.woff`,
  and `.woff2` among the default public-origin file types. Verify the target
  tenant's effective CDN policy and actual requests; do not infer support
  from the file extension alone.
- Confirm font redistribution/use rights and the font's actual format before
  publication. Do not convert or rename font files to work around a CDN or
  browser restriction.
- When CSS refers to fonts or images using relative URLs, preserve the
  expected directory layout or rewrite and validate those references against
  the actual shared asset URLs.

## Organization Assets Library is a different feature

Microsoft's Organization Assets Library feature is intended to make
organization images available in SharePoint's image picker and Office
templates available in Office. The documented asset types are images and
Office templates; it is not a general-purpose web-font or CSS hosting
recommendation. Although its setup can enable a CDN, that does not by itself
make a library a suitable or approved web asset origin. Do not designate a
library as an Organization Assets Library to host this workflow's CSS or
fonts.

## Migration workflow contract

1. Before styling the first page, inspect the target site for an approved
   shared asset location and any existing Modernernment Design System assets.
   Verify each needed file by exact URL and content hash; do not use a
   filename-only match.
2. If the exact approved asset release is already present and accessible,
   reuse its recorded URLs and do not upload duplicates.
3. If an asset is missing, prepare a single asset package from the approved
   design-system source. Use `sharepoint-publish-markdown-files` to create and
   execute the document-library file publication plan; it is the existing
   file-and-asset publisher and its plan builder includes files recursively.
   Dry-run first and inspect every target mapping. Its executor can overwrite
   existing files, so independently check exact target paths and do not
   overwrite shared assets implicitly. The HTML-only publisher does not upload
   companion assets.
4. If the shared library or folder is missing, use
   `sharepoint-create-document-library` for the library and its
   `spo-create-folder.ps1` for folders (`-Execute -ConfirmToken
   CREATE-SPO-FOLDER`; it checks the library exists and creates parents
   first). Upload with `spo-upload-file.ps1` (`-Execute -ConfirmToken
   PUBLISH-SPO-MARKDOWN`). The site-level location is
   `SiteAssets/standard-design-system` with `fonts/` and `icons/` subfolders;
   the required set is every file under the `standard-design-system` skill's
   `assets/` (CSS, all fonts, `fonts/LICENSE`, `icons/bc-logo.png`). Verify
   each object before publication. Do not create a library or change CDN
   settings without the required authorization.
5. After an approved upload, verify file identity, hash, URL, permissions,
   MIME/content type, and browser retrieval (including font loading/CORS as
   applicable). Only then record the reusable URLs and use them from page
   HTML.
6. For later pages targeting the same environment, verify and reuse those
   URLs. Upload only missing approved assets; use a new versioned path for
   changed releases rather than silently replacing files on which existing
   pages depend.
7. Stop before page publication if access, font loading, licensing, CDN
   policy, or asset identity is unresolved. Never claim design-system
   conformance from local CSS alone.

The installed `sharepoint-publish-markdown-files` skill explicitly owns raw
file and asset upload to document libraries. Its plan builder enumerates
source files recursively and its PnP executor uploads them with `Add-PnPFile`.
Use its dry-run and `PUBLISH-SPO-MARKDOWN` write gate for shared assets; do not
use `sharepoint-publish-html-page` for CSS or fonts.

## Microsoft sources

- [Use Microsoft 365 CDN with SharePoint Online](https://learn.microsoft.com/en-us/microsoft-365/enterprise/use-microsoft-365-cdn-with-spo?view=o365-worldwide):
  static asset origins, supported file types, public-origin behavior,
  configuration, and URL cautions.
- [Content delivery networks](https://learn.microsoft.com/en-us/microsoft-365/enterprise/content-delivery-networks?view=o365-worldwide):
  overview of Microsoft 365 CDN and the anonymous-access implications of
  public origins.
- [Create an organization assets library](https://learn.microsoft.com/en-us/sharepoint/organization-assets-library):
  supported Organization Assets Library scenarios, asset types, permissions,
  and its CDN relationship.
