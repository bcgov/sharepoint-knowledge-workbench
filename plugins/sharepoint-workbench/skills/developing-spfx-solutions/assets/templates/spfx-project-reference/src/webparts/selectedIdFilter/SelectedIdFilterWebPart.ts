/**
 * SelectedIdFilterWebPart (SPFx Web Part)
 * =====================================
 *
 * Purpose:
 *     POC SPFx web part that reads a `SelectedID` URL query parameter and
 *     renders the matching item from the `Books` list, expanding the
 *     `BookAuthor` lookup. This is the SPFx-based replacement for SP2016's
 *     native `?SelectedID=` URL-driven page filtering, which has no
 *     equivalent in modern SharePoint Online (confirmed: native "Connect
 *     to source" web part connections only respond to in-page clicks,
 *     never URL query params).
 *
 * Layer: Frontend / SPFx Web Part
 *
 * Key Input Dependencies:
 *     - SharePoint `Books` list (fields: `Title`, `BookAuthor` lookup ->
 *       `Authors` list `Title`) on the trial tenancy site.
 *     - `SelectedID` URL query string parameter (e.g.
 *       `?SelectedID=1234`), read via `window.location.search`. Must be a
 *       positive integer — validated before use (see `_renderBook`).
 *     - `this.context.spHttpClient` (SPFx-provided REST client) and
 *       `this.context.pageContext.web.absoluteUrl`.
 *
 * Usage Examples:
 *     Add this web part to a page, then navigate to:
 *     `<page>.aspx?SelectedID=<Books item ID>`
 *
 * Key Functions:
 *     - render() - reads `SelectedID` from the URL; shows "No SelectedID
 *       provided." if absent, otherwise delegates to `_renderBook`.
 *     - _renderBook(rawSelectedId) - validates the ID is numeric, queries
 *       the `Books` list item by ID (expanding `BookAuthor`), and renders
 *       Title/ID/Author or a not-found/error message. Escapes all
 *       REST-sourced and URL-sourced values before inserting into the DOM
 *       (XSS mitigation) and guards against stale/out-of-order responses
 *       from overlapping `render()` calls.
 *     - _escapeHtml(value) - HTML-entity-encodes a string for safe
 *       interpolation into `innerHTML`.
 *
 * Security notes:
 *     - All list-sourced field values (e.g. `Title`) and the `SelectedID`
 *       URL parameter itself are user-editable/attacker-controlled data
 *       and are escaped before rendering — do not remove `_escapeHtml`
 *       calls when editing this file.
 *
 * See also: the proof-of-concept log (design
 * notes, including the Claude code-review findings this revision
 * addresses) and
 * plugins/sharepoint-spfx-development/references/MODERN-PAGE-DYNAMIC-FILTERING-GAP.md
 * (full gap analysis this POC is validating).
 */

import { Version } from '@microsoft/sp-core-library';
import { BaseClientSideWebPart } from '@microsoft/sp-webpart-base';
import { SPHttpClient, SPHttpClientResponse } from '@microsoft/sp-http';
import {
  IDynamicDataCallables,
  IDynamicDataPropertyDefinition
} from '@microsoft/sp-dynamic-data';

import styles from './SelectedIdFilterWebPart.module.scss';

export interface ISelectedIdFilterWebPartProps {
}

const BOOKS_LIST_NAME       = 'Books';
const AUTHORS_LIST_NAME     = 'Authors';
const EVENT_LIST_NAME        = 'Author_Events';
const REVIEW_LIST_NAME        = 'Author_Reviews';

export interface IAuthorItem {
  Id: number;
  Title: string;
}

export interface IEventItem {
  Id: number;
  Title: string;
  EventDate: string;
  Location: string;
}

export interface IReviewItem {
  Id: number;
  Title: string;
  Review: string;
}

export default class SelectedIdFilterWebPart
  extends BaseClientSideWebPart<ISelectedIdFilterWebPartProps>
  implements IDynamicDataCallables {

  private _renderToken = 0;

  // Dynamic Data state exposed to other web parts on the page
  private _selectedBookId: number | undefined;
  private _selectedBookTitle: string | undefined;
  private _selectedAuthorId: number | undefined;
  private _selectedAuthorTitle: string | undefined;

  public onInit(): Promise<void> {
    this.context.dynamicDataSourceManager.initializeSource(this);
    return super.onInit();
  }

  public getPropertyDefinitions(): ReadonlyArray<IDynamicDataPropertyDefinition> {
    return [
      { id: 'authorId', title: 'Author ID' },
      { id: 'authorTitle', title: 'Author Title / Name' },
      { id: 'bookId', title: 'Book ID' },
      { id: 'bookTitle', title: 'Book Title' }
    ];
  }

  public getPropertyValue(propertyId: string): number | string | undefined {
    switch (propertyId) {
      case 'authorId': return this._selectedAuthorId;
      case 'authorTitle': return this._selectedAuthorTitle;
      case 'bookId': return this._selectedBookId;
      case 'bookTitle': return this._selectedBookTitle;
      default: return undefined;
    }
  }

  public render(): void {
    this.domElement.innerHTML = `<div class="${ styles.selectedIdFilter }">Loading briefing dossier...</div>`;

    const params = new URLSearchParams(window.location.search);
    const rawSelectedId = this._getParamCaseInsensitive(params, 'SelectedID');

    if (!rawSelectedId) {
      this._updateDynamicProperties(undefined, undefined, undefined, undefined);
      this.domElement.innerHTML = `
        <div class="${ styles.selectedIdFilter }">
          <div class="${ styles.banner }">
            <h1>Master-Detail Dossier Briefing</h1>
          </div>
          <p class="${ styles.emptyNotice }">No SelectedID provided in the URL query string (e.g. <code>?SelectedID=3</code>).</p>
        </div>
      `;
      return;
    }

    const token = ++this._renderToken;
    this._renderDashboard(rawSelectedId, token).catch((error: unknown) => {
      if (token !== this._renderToken) {
        return;
      }
      this._updateDynamicProperties(undefined, undefined, undefined, undefined);
      const message = error instanceof Error ? error.message : String(error);
      this.domElement.innerHTML = `<div class="${ styles.selectedIdFilter }">Error loading briefing: ${this._escapeHtml(message)}</div>`;
    });
  }

  private _updateDynamicProperties(
    bookId: number | undefined,
    bookTitle: string | undefined,
    authorId: number | undefined,
    authorTitle: string | undefined
  ): void {
    const changed =
      this._selectedBookId !== bookId ||
      this._selectedBookTitle !== bookTitle ||
      this._selectedAuthorId !== authorId ||
      this._selectedAuthorTitle !== authorTitle;

    this._selectedBookId = bookId;
    this._selectedBookTitle = bookTitle;
    this._selectedAuthorId = authorId;
    this._selectedAuthorTitle = authorTitle;

    if (changed) {
      this.context.dynamicDataSourceManager.notifyPropertyChanged('authorId');
      this.context.dynamicDataSourceManager.notifyPropertyChanged('authorTitle');
      this.context.dynamicDataSourceManager.notifyPropertyChanged('bookId');
      this.context.dynamicDataSourceManager.notifyPropertyChanged('bookTitle');
    }
  }

  private _getParamCaseInsensitive(params: URLSearchParams, name: string): string | null {
    const target = name.toLowerCase();
    let result: string | null = null;
    params.forEach((value, key) => {
      if (result === null && key.toLowerCase() === target) {
        result = value;
      }
    });
    return result;
  }

  private _escapeHtml(value: string): string {
    return value
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  /**
   * Fetch and render the full 5-Section Dossier Briefing Dashboard.
   */
  private async _renderDashboard(rawSelectedId: string, token: number): Promise<void> {
    const id = parseInt(rawSelectedId, 10);
    if (isNaN(id) || id <= 0) {
      if (token === this._renderToken) {
        this._updateDynamicProperties(undefined, undefined, undefined, undefined);
        this.domElement.innerHTML = `<div class="${ styles.selectedIdFilter }">Invalid SelectedID: ${this._escapeHtml(rawSelectedId)}</div>`;
      }
      return;
    }

    const siteUrl = this.context.pageContext.web.absoluteUrl;

    // 1. Fetch Book item
    const bookUrl =
      `${siteUrl}/_api/web/lists/getbytitle('${BOOKS_LIST_NAME}')/items(${id})?$select=Id,Title,BookAuthorId,BookAuthor/Title&$expand=BookAuthor`;

    const response: SPHttpClientResponse = await this.context.spHttpClient.get(
      bookUrl,
      SPHttpClient.configurations.v1,
      { headers: { Accept: 'application/json;odata=nometadata' } }
    );

    if (token !== this._renderToken) {
      return;
    }

    if (!response.ok) {
      this._updateDynamicProperties(undefined, undefined, undefined, undefined);
      if (response.status === 404) {
        this.domElement.innerHTML = `<div class="${ styles.selectedIdFilter }">No record found for SelectedID ${id}.</div>`;
        return;
      }
      this.domElement.innerHTML = `<div class="${ styles.selectedIdFilter }">Error loading record (${response.status})</div>`;
      return;
    }

    const book = await response.json();
    if (!book || book.Id === undefined) {
      this._updateDynamicProperties(undefined, undefined, undefined, undefined);
      this.domElement.innerHTML = `<div class="${ styles.selectedIdFilter }">Unexpected response for SelectedID ${id}.</div>`;
      return;
    }

    const bookId = typeof book.Id === 'number' ? book.Id : parseInt(book.Id, 10);
    const bookTitle = book.Title || '';
    const authorId = book.BookAuthorId !== undefined && book.BookAuthorId !== null
      ? (typeof book.BookAuthorId === 'number' ? book.BookAuthorId : parseInt(book.BookAuthorId, 10))
      : undefined;
    const authorTitle = book.BookAuthor && book.BookAuthor.Title ? book.BookAuthor.Title : '';

    this._updateDynamicProperties(bookId, bookTitle, authorId, authorTitle);

    // 2. Fetch Author Image, Events, and Reviews in parallel
    let events: IEventItem[] = [];
    let reviews: IReviewItem[] = [];
    let authorImageUrl: string | null = null;

    if (authorId !== undefined) {
      const authorUrl = `${siteUrl}/_api/web/lists/getbytitle('${AUTHORS_LIST_NAME}')/items(${authorId})?$select=Id,Title,Picture`;
      const apprUrl = `${siteUrl}/_api/web/lists/getbytitle('${EVENT_LIST_NAME}')/items?$filter=RelatedAuthorId eq ${authorId}&$select=Id,Title,EventDate,Location&$orderby=EventDate asc`;
      const reviewUrl = `${siteUrl}/_api/web/lists/getbytitle('${REVIEW_LIST_NAME}')/items?$filter=RelatedAuthorId eq ${authorId}&$select=Id,Title,Review`;

      const authorKey = authorTitle.toLowerCase().split(' ').pop() || '';

      try {
        const [authorRes, apprRes, narrRes] = await Promise.all([
          this.context.spHttpClient.get(authorUrl, SPHttpClient.configurations.v1, { headers: { Accept: 'application/json;odata=nometadata' } }),
          this.context.spHttpClient.get(apprUrl, SPHttpClient.configurations.v1, { headers: { Accept: 'application/json;odata=nometadata' } }),
          this.context.spHttpClient.get(reviewUrl, SPHttpClient.configurations.v1, { headers: { Accept: 'application/json;odata=nometadata' } })
        ]);

        if (authorRes.ok) {
          const authorObj = await authorRes.json();
          if (authorObj && authorObj.Picture) {
            authorImageUrl = typeof authorObj.Picture === 'string' ? authorObj.Picture : (authorObj.Picture.Url || null);
          }
        }
        if (apprRes.ok) {
          const data = await apprRes.json();
          events = data && data.value ? data.value : [];
        }
        if (narrRes.ok) {
          const data = await narrRes.json();
          reviews = data && data.value ? data.value : [];
        }

        // If no explicit Picture field on Author, search the Images library by name
        if (!authorImageUrl) {
          try {
            const imgQueryUrl = `${siteUrl}/_api/web/lists/getbytitle('Images')/items?$select=FileRef,FileLeafRef`;
            const imgRes = await this.context.spHttpClient.get(imgQueryUrl, SPHttpClient.configurations.v1, { headers: { Accept: 'application/json;odata=nometadata' } });
            if (imgRes.ok) {
              const imgData = await imgRes.json();
              const files = imgData && imgData.value ? imgData.value : [];
              const match = files.find((f: { FileLeafRef: string; FileRef: string }) => {
                const name = (f.FileLeafRef || '').toLowerCase();
                return authorKey && (name.indexOf(authorKey) !== -1 || (authorKey === 'austen' && name.indexOf('austin') !== -1));
              });
              if (match && match.FileRef) {
                authorImageUrl = match.FileRef;
              }
            }
          } catch {
            // fallback
          }
        }
      } catch {
        // non-blocking
      }
    }


    if (token !== this._renderToken) {
      return;
    }

    // Split events into Upcoming vs Previous
    const now = new Date();
    const upcomingEvents: IEventItem[] = [];
    const previousEvents: IEventItem[] = [];

    events.forEach(appr => {
      const d = appr.EventDate ? new Date(appr.EventDate) : null;
      if (d && d >= now) {
        upcomingEvents.push(appr);
      } else {
        previousEvents.push(appr);
      }
    });

    const safeTitle = this._escapeHtml(bookTitle);
    const safeAuthorTitle = this._escapeHtml(authorTitle);
    const currentUrl = encodeURIComponent(window.location.href);

    const editAuthorUrl = authorId ? `${siteUrl}/Lists/${AUTHORS_LIST_NAME}/EditForm.aspx?ID=${authorId}&Source=${currentUrl}` : '#';
    const newReviewUrl = `${siteUrl}/Lists/${REVIEW_LIST_NAME}/NewForm.aspx?Source=${currentUrl}`;
    const newEventUrl = `${siteUrl}/Lists/${EVENT_LIST_NAME}/NewForm.aspx?Source=${currentUrl}`;

    // Photo Box markup
    const photoBoxContent = authorImageUrl
      ? `<img src="${authorImageUrl}" alt="${safeAuthorTitle}" style="width: 100%; height: 100%; object-fit: cover;" />`
      : `
        <svg width="64" height="64" viewBox="0 0 24 24" fill="#a19f9d">
          <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
        </svg>
        <span class="${ styles.noPhotoText }">No Photo</span>
      `;


    // Render Section: Upcoming Events Table
    let upcomingHtml = '';
    if (upcomingEvents.length > 0) {
      const rows = upcomingEvents.map(a => `
        <tr>
          <td style="width: 50px;"><a class="${styles.actionButton} ${styles.secondaryButton}" href="${siteUrl}/Lists/${EVENT_LIST_NAME}/EditForm.aspx?ID=${a.Id}&Source=${currentUrl}">Edit</a></td>
          <td><b>${this._escapeHtml(a.Title || '')}</b></td>
          <td>${a.EventDate ? new Date(a.EventDate).toLocaleDateString() : 'N/A'}</td>
          <td>${this._escapeHtml(a.Location || '')}</td>
        </tr>
      `).join('');
      upcomingHtml = `
        <table class="${styles.dataTable}">
          <thead>
            <tr>
              <th style="width: 50px;">Edit</th>
              <th>Event Title</th>
              <th>Date</th>
              <th>Location</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      `;
    } else {
      upcomingHtml = `<p class="${styles.emptyNotice}">There are no upcoming events to show for this subject.</p>`;
    }

    // Render Section: Previous Events Table
    let previousHtml = '';
    if (previousEvents.length > 0) {
      const rows = previousEvents.map(a => `
        <tr>
          <td style="width: 50px;"><a class="${styles.actionButton} ${styles.secondaryButton}" href="${siteUrl}/Lists/${EVENT_LIST_NAME}/EditForm.aspx?ID=${a.Id}&Source=${currentUrl}">Edit</a></td>
          <td><b>${this._escapeHtml(a.Title || '')}</b></td>
          <td>${a.EventDate ? new Date(a.EventDate).toLocaleDateString() : 'N/A'}</td>
          <td>${this._escapeHtml(a.Location || '')}</td>
        </tr>
      `).join('');
      previousHtml = `
        <table class="${styles.dataTable}">
          <thead>
            <tr>
              <th style="width: 50px;">Edit</th>
              <th>Event Title</th>
              <th>Date</th>
              <th>Location</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      `;
    } else {
      previousHtml = `<p class="${styles.emptyNotice}">There are no previous events to show for this subject.</p>`;
    }

    // Render Section: Background Information / Reviews
    let reviewsHtml = '';
    if (reviews.length > 0) {
      const rows = reviews.map(n => `
        <tr>
          <td style="width: 50px;"><a class="${styles.actionButton} ${styles.secondaryButton}" href="${siteUrl}/Lists/${REVIEW_LIST_NAME}/EditForm.aspx?ID=${n.Id}&Source=${currentUrl}">Edit</a></td>
          <td>${this._escapeHtml(n.Review || n.Title || '')}</td>
        </tr>
      `).join('');
      reviewsHtml = `
        <table class="${styles.dataTable}">
          <thead>
            <tr>
              <th style="width: 50px;">Edit</th>
              <th>Review</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      `;
    } else {
      reviewsHtml = `<p class="${styles.emptyNotice}">There are no items to show in this view of the "Author_Reviews" list.</p>`;
    }

    this.domElement.innerHTML = `
      <div class="${ styles.selectedIdFilter }">
        <div class="${ styles.banner }">
          <h1>Master-Detail Dossier Dashboard</h1>
        </div>

        <!-- Section 1: Identification Details & Photo -->
        <div class="${ styles.section }">
          <div class="${ styles.sectionHeader }">
            <h3>Identification Details & Picture</h3>
            ${authorId ? `<a class="${styles.actionButton} ${styles.secondaryButton}" href="${editAuthorUrl}">Edit Author</a>` : ''}
          </div>
          <div class="${ styles.idCardContainer }">
            <!-- Author Photo / Avatar Box -->
            <div class="${ styles.photoBox }">
              ${photoBoxContent}
            </div>

            <!-- Identity Details Grid -->
            <div class="${ styles.detailGrid }">
              <div class="${ styles.detailItem }">
                <span class="${ styles.label }">Subject Name</span>
                <span class="${ styles.value }">${safeAuthorTitle || 'None'}</span>
              </div>
              <div class="${ styles.detailItem }">
                <span class="${ styles.label }">Author ID</span>
                <span class="${ styles.value }">${authorId !== undefined ? authorId : 'N/A'}</span>
              </div>
              <div class="${ styles.detailItem }">
                <span class="${ styles.label }">Book Title</span>
                <span class="${ styles.value }">${safeTitle} (ID: ${bookId})</span>
              </div>
              <div class="${ styles.detailItem }">
                <span class="${ styles.label }">Category / Role</span>
                <span class="${ styles.value }">Author / Primary Subject</span>
              </div>
              <div class="${ styles.detailItem }">
                <span class="${ styles.label }">CS Number</span>
                <span class="${ styles.value }">CS-${authorId ? (1000 + authorId) : 'N/A'}</span>
              </div>
              <div class="${ styles.detailItem }">
                <span class="${ styles.label }">FPS Number</span>
                <span class="${ styles.value }">FPS-${authorId ? (80000 + authorId) : 'N/A'}</span>
              </div>
            </div>
          </div>
        </div>


        <!-- Section 2: Status -->
        <div class="${ styles.section }">
          <div class="${ styles.sectionHeader }">
            <h3>Status</h3>
          </div>
          <div class="${ styles.detailGrid }">
            <div class="${ styles.detailItem }">
              <span class="${ styles.label }">Risk Level</span>
              <span class="${ styles.value }">Medium</span>
            </div>
            <div class="${ styles.detailItem }">
              <span class="${ styles.label }">In Custody</span>
              <span class="${ styles.value }">Yes</span>
            </div>
            <div class="${ styles.detailItem }">
              <span class="${ styles.label }">Last Known Location</span>
              <span class="${ styles.value }">Victoria</span>
            </div>
            <div class="${ styles.detailItem }">
              <span class="${ styles.label }">Last Update</span>
              <span class="${ styles.value }">${new Date().toISOString().split('T')[0]}</span>
            </div>
          </div>
        </div>

        <!-- Section 3: Upcoming Events -->
        <div class="${ styles.section }">
          <div class="${ styles.sectionHeader }">
            <h3>Upcoming Events</h3>
            <a class="${ styles.actionButton }" href="${newEventUrl}">+ new event</a>
          </div>
          ${upcomingHtml}
        </div>

        <!-- Section 4: Previous Events -->
        <div class="${ styles.section }">
          <div class="${ styles.sectionHeader }">
            <h3>Previous Events</h3>
          </div>
          ${previousHtml}
        </div>

        <!-- Section 5: Background Information -->
        <div class="${ styles.section }">
          <div class="${ styles.sectionHeader }">
            <h3>Background Information</h3>
            <a class="${ styles.actionButton }" href="${newReviewUrl}">+ new item</a>
          </div>
          ${reviewsHtml}
        </div>
      </div>
    `;
  }

  protected get dataVersion(): Version {
    return Version.parse('1.0');
  }
}




