# Use Case: Content Migration

Item-level SharePoint content (list-item data) migration: batched migration with retry, and the
two-pass lookup-ID re-link technique lookup columns require.

## When to use this

Target lists/fields already exist with the right shape (provisioned separately — see
[Content Provisioning](sharepoint-provisioning.md)) and you need to move the actual row data
across, including lookup columns that reference other migrated items.

## Workflow at a glance

`migrate-sharepoint-list-content` runs in two passes:

1. **First pass** — migrates content, records a source-to-destination ID mapping as each item
   lands.
2. **Second pass** — resolves lookup fields against that mapping, once all target lists the
   lookups reference have been fully migrated (a lookup field can't be populated until the item it
   targets already exists at the destination with a real ID).

**Non-responsibilities:** schema/list/field structure is `sharepoint-provisioning`'s job; page and
link content are `sharepoint-page-modernization`'s and `sharepoint-link-remediation`'s jobs
respectively. Shaping a source record into this plugin's caller-supplied field format is the
caller's responsibility, not this plugin's.

## Full detail

[`plugins/sharepoint-content-migration/README.md`](../../plugins/sharepoint-content-migration/README.md)
