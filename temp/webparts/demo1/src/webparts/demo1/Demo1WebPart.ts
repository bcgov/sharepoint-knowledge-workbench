/**
 * Demo1WebPart (SPFx Web Part)
 * ============================
 *
 * Purpose:
 *     Renders a line-of-business application launcher: an icon/link tile grid
 *     sourced from a SharePoint "Applications" list, showing every item marked
 *     "Pinned" (always shown, always first) plus the current user's own
 *     favorited ("hearted") applications, with a heart toggle on each tile and
 *     a "See all applications" link to the full list view.
 *
 * Layer: Frontend / SPFx Web Part
 *
 * Key Input Dependencies:
 *     - SharePoint "Applications" list (fields: `Title`, `IconUrl` (Text),
 *       `Url` (Text), `Pinned` (Yes/No)) on the current site.
 *     - SharePoint "ApplicationFavorites" list (fields: `Title`,
 *       `ApplicationId` (Number) — the favorited item's `Applications` list
 *       item ID). Each item's `Author` is the favoriting user; the web part
 *       filters this list to the current user via `Author/Id eq <userId>`.
 *     - `this.context.spHttpClient` (SPFx REST client),
 *       `this.context.pageContext.web.absoluteUrl`, and
 *       `this.context.pageContext.legacyPageContext.userId` (current user ID).
 *     - `allApplicationsUrl` web part property (property pane) — the URL for
 *       the "See all applications" link (defaults to the Applications list's
 *       default view).
 *
 * Usage Examples:
 *     Add this web part to a page; configure `allApplicationsUrl` via the
 *     property pane if it should point somewhere other than the Applications
 *     list's default view.
 *
 * Key Functions:
 *     - render() - kicks off `_loadAndRender()` and renders a loading state.
 *     - _loadAndRender() - fetches Applications + the current user's
 *       favorites in parallel, merges pinned + favorited items (deduplicated,
 *       pinned first), and renders the tile grid.
 *     - _toggleFavorite(appId, isFavorited) - creates or deletes the current
 *       user's `ApplicationFavorites` item for the given application, then
 *       re-renders.
 *     - _getRequestDigest() - fetches a fresh `X-RequestDigest` token for
 *       POST/DELETE calls.
 *     - _escapeHtml(value) - HTML-entity-encodes a string for safe
 *       interpolation into `innerHTML`.
 *
 * Security notes:
 *     - All list-sourced field values (`Title`, `IconUrl`, `Url`) are
 *       user-editable data and are escaped before rendering (XSS mitigation)
 *       — do not remove `_escapeHtml` calls when editing this file.
 */

import { Version } from '@microsoft/sp-core-library';
import {
  type IPropertyPaneConfiguration,
  PropertyPaneTextField
} from '@microsoft/sp-property-pane';
import { BaseClientSideWebPart } from '@microsoft/sp-webpart-base';
import { SPHttpClient, type SPHttpClientResponse } from '@microsoft/sp-http';

import styles from './Demo1WebPart.module.scss';

const APPLICATIONS_LIST_NAME = 'Applications';
const FAVORITES_LIST_NAME = 'ApplicationFavorites';

export interface IDemo1WebPartProps {
  allApplicationsUrl: string;
}

interface IApplicationItem {
  Id: number;
  Title: string;
  IconUrl: string;
  Url: string;
  Pinned: boolean;
}

export default class Demo1WebPart extends BaseClientSideWebPart<IDemo1WebPartProps> {

  private _renderToken = 0;

  public render(): void {
    this.domElement.innerHTML = `<div class="${styles.demo1}">Loading applications...</div>`;
    const token = ++this._renderToken;
    this._loadAndRender(token).catch((error: unknown) => {
      if (token !== this._renderToken) {
        return;
      }
      const message = error instanceof Error ? error.message : String(error);
      this.domElement.innerHTML = `<div class="${styles.demo1}">Error loading applications: ${this._escapeHtml(message)}</div>`;
    });
  }

  protected get dataVersion(): Version {
    return Version.parse('1.0');
  }

  protected getPropertyPaneConfiguration(): IPropertyPaneConfiguration {
    return {
      pages: [
        {
          header: { description: 'Configure the application launcher' },
          groups: [
            {
              groupName: 'Settings',
              groupFields: [
                PropertyPaneTextField('allApplicationsUrl', {
                  label: 'See all applications URL'
                })
              ]
            }
          ]
        }
      ]
    };
  }

  /**
   * Fetches Applications + the current user's favorites, merges pinned and
   * favorited items, and renders the tile grid.
   */
  private async _loadAndRender(token: number): Promise<void> {
    const siteUrl = this.context.pageContext.web.absoluteUrl;
    const userId = this.context.pageContext.legacyPageContext
      ? this.context.pageContext.legacyPageContext.userId
      : undefined;

    const [applications, favoritedIds] = await Promise.all([
      this._fetchApplications(siteUrl),
      userId !== undefined ? this._fetchFavoriteIds(siteUrl, userId) : Promise.resolve<number[]>([])
    ]);

    if (token !== this._renderToken) {
      return;
    }

    const favoritedIdSet = new Set(favoritedIds);
    const pinned = applications.filter(app => app.Pinned);
    const favorited = applications.filter(app => !app.Pinned && favoritedIdSet.has(app.Id));
    const visible = [...pinned, ...favorited];

    const allApplicationsUrl = this.properties.allApplicationsUrl
      || `${siteUrl}/Lists/${APPLICATIONS_LIST_NAME}/AllItems.aspx`;

    const tiles = visible.map(app => this._renderTile(app, app.Pinned || favoritedIdSet.has(app.Id))).join('');

    this.domElement.innerHTML = `
      <div class="${styles.demo1}">
        <div class="${styles.tileGrid}">
          ${tiles || `<div class="${styles.emptyNotice}">No pinned or favorited applications yet.</div>`}
        </div>
        <a class="${styles.seeAllLink}" href="${this._escapeHtml(allApplicationsUrl)}">See all applications &gt;</a>
      </div>`;

    this.domElement.querySelectorAll<HTMLElement>(`.${styles.favoriteToggle}`).forEach(el => {
      el.addEventListener('click', (evt: MouseEvent) => {
        evt.preventDefault();
        evt.stopPropagation();
        const appId = parseInt(el.dataset.appId || '', 10);
        const isFavorited = el.dataset.favorited === 'true';
        if (!isNaN(appId)) {
          this._toggleFavorite(appId, isFavorited).catch((error: unknown) => {
            console.error('Failed to toggle favorite', error);
          });
        }
      });
    });
  }

  private _renderTile(app: IApplicationItem, isFavorited: boolean): string {
    const heartClass = isFavorited ? styles.heartFilled : styles.heartOutline;
    return `
      <div class="${styles.tile}">
        <a class="${styles.tileLink}" href="${this._escapeHtml(app.Url)}" target="_blank" rel="noopener noreferrer">
          <img class="${styles.tileIcon}" src="${this._escapeHtml(app.IconUrl)}" alt="${this._escapeHtml(app.Title)}" />
          <span class="${styles.tileLabel}">${this._escapeHtml(app.Title)}</span>
        </a>
        <button
          type="button"
          class="${styles.favoriteToggle} ${heartClass}"
          data-app-id="${app.Id}"
          data-favorited="${isFavorited && !app.Pinned}"
          title="${isFavorited ? 'Remove from favorites' : 'Add to favorites'}"
          aria-label="${isFavorited ? 'Remove from favorites' : 'Add to favorites'}"
        >&#9825;</button>
      </div>`;
  }

  private async _fetchApplications(siteUrl: string): Promise<IApplicationItem[]> {
    const url = `${siteUrl}/_api/web/lists/getbytitle('${APPLICATIONS_LIST_NAME}')/items?$select=Id,Title,IconUrl,Url,Pinned&$orderby=Title asc`;
    const response: SPHttpClientResponse = await this.context.spHttpClient.get(
      url,
      SPHttpClient.configurations.v1,
      { headers: { Accept: 'application/json;odata=nometadata' } }
    );
    if (!response.ok) {
      throw new Error(`Failed to load ${APPLICATIONS_LIST_NAME} list (${response.status})`);
    }
    const data = await response.json();
    const values: unknown[] = data && Array.isArray(data.value) ? data.value : [];
    return values.map((raw: unknown) => {
      const item = raw as Record<string, unknown>;
      return {
        Id: typeof item.Id === 'number' ? item.Id : parseInt(String(item.Id), 10),
        Title: typeof item.Title === 'string' ? item.Title : '',
        IconUrl: typeof item.IconUrl === 'string' ? item.IconUrl : '',
        Url: typeof item.Url === 'string' ? item.Url : '',
        Pinned: item.Pinned === true
      };
    });
  }

  private async _fetchFavoriteIds(siteUrl: string, userId: number): Promise<number[]> {
    const url = `${siteUrl}/_api/web/lists/getbytitle('${FAVORITES_LIST_NAME}')/items?$select=ApplicationId&$filter=AuthorId eq ${userId}`;
    const response: SPHttpClientResponse = await this.context.spHttpClient.get(
      url,
      SPHttpClient.configurations.v1,
      { headers: { Accept: 'application/json;odata=nometadata' } }
    );
    if (!response.ok) {
      // No favorites list, or no access — treat as "no favorites" rather than failing the whole web part.
      return [];
    }
    const data = await response.json();
    const values: unknown[] = data && Array.isArray(data.value) ? data.value : [];
    return values
      .map((raw: unknown) => {
        const item = raw as Record<string, unknown>;
        return typeof item.ApplicationId === 'number' ? item.ApplicationId : parseInt(String(item.ApplicationId), 10);
      })
      .filter(id => !isNaN(id));
  }

  /**
   * Adds or removes the current user's ApplicationFavorites item for the given
   * application, then re-renders the web part.
   */
  private async _toggleFavorite(appId: number, isFavorited: boolean): Promise<void> {
    const siteUrl = this.context.pageContext.web.absoluteUrl;
    const digest = await this._getRequestDigest(siteUrl);

    if (isFavorited) {
      const userId = this.context.pageContext.legacyPageContext
        ? this.context.pageContext.legacyPageContext.userId
        : undefined;
      const existingUrl = `${siteUrl}/_api/web/lists/getbytitle('${FAVORITES_LIST_NAME}')/items?$select=Id&$filter=ApplicationId eq ${appId} and AuthorId eq ${userId}`;
      const existingRes = await this.context.spHttpClient.get(existingUrl, SPHttpClient.configurations.v1, {
        headers: { Accept: 'application/json;odata=nometadata' }
      });
      if (existingRes.ok) {
        const data = await existingRes.json();
        const favoriteItemId = data && Array.isArray(data.value) && data.value.length > 0 ? data.value[0].Id : undefined;
        if (favoriteItemId !== undefined) {
          await this.context.spHttpClient.post(
            `${siteUrl}/_api/web/lists/getbytitle('${FAVORITES_LIST_NAME}')/items(${favoriteItemId})`,
            SPHttpClient.configurations.v1,
            {
              headers: {
                Accept: 'application/json;odata=nometadata',
                'X-RequestDigest': digest,
                'X-HTTP-Method': 'DELETE',
                'IF-MATCH': '*'
              }
            }
          );
        }
      }
    } else {
      await this.context.spHttpClient.post(
        `${siteUrl}/_api/web/lists/getbytitle('${FAVORITES_LIST_NAME}')/items`,
        SPHttpClient.configurations.v1,
        {
          headers: {
            Accept: 'application/json;odata=nometadata',
            'Content-type': 'application/json;odata=nometadata',
            'X-RequestDigest': digest
          },
          body: JSON.stringify({ Title: `Favorite-${appId}`, ApplicationId: appId })
        }
      );
    }

    this.render();
  }

  private async _getRequestDigest(siteUrl: string): Promise<string> {
    const response: SPHttpClientResponse = await this.context.spHttpClient.post(
      `${siteUrl}/_api/contextinfo`,
      SPHttpClient.configurations.v1,
      { headers: { Accept: 'application/json;odata=nometadata' } }
    );
    const data = await response.json();
    return data.FormDigestValue;
  }

  private _escapeHtml(value: string): string {
    return value
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }
}
