# Local Library UI/UX Reference

Use this guide to keep the Local Library interface consistent across new pages.
All examples live inside the Django app: `catalog/`.

## Core Layout & Assets
- Base shell (Bootstrap 5.3, sidebar, header): [catalog/templates/base_generic.html](catalog/templates/base_generic.html)
- Primary stylesheet with custom tokens and components: [catalog/static/css/styles.css](catalog/static/css/styles.css)
- Default content wrapper (`.content-panel`) and hero header (`.app-header`): see [catalog/templates/index.html](catalog/templates/index.html)

### Layout Principles
- Two-column layout with a fixed light sidebar and a spacious content area.
- Pages sit inside `.content-panel` while hero/header info uses gradients and subtle shadows.
- Generous spacing and rounded corners (16–20px) keep the look soft and modern.
- Hebrew copy is preferred for user-facing text; keep iconography from Bootstrap Icons for quick affordances.

## Visual Language
- **Color accents:** leverage Bootstrap primary (`#0d6efd`) and purple (`#6610f2`) gradients. Soft blues (`#eef2f9`, `#f4f8ff`) for backgrounds, dashed borders for empty states.
- **Typography:** Inter/Segoe UI stack; bold headings, small uppercase labels for metadata.
- **Shadows:** Long, soft drop shadows (`0 25px 45px -30px`) paired with semi-transparent borders to create depth.
- **Icons:** Bootstrap Icons (`bi bi-*`) precede labels for clarity.

## Key Components & Examples
- **Tables (`.data-table`):** striped, rounded tables with hover states. See [catalog/templates/catalog/book_list.html](catalog/templates/catalog/book_list.html).
- **Entity cards (`.entity-card`, `.copy-card`):** stacked info blocks with transitions and status chips. Example: [catalog/templates/catalog/book_detail.html](catalog/templates/catalog/book_detail.html).
- **Info grid (`.info-grid` + `.info-item`):** compact metadata tiles. Used in detail views and the renew form header.
- **Status badges (`.status-badge` + variants):** color-coded pills for availability and alerts.
- **Empty state panel (`.empty-state`):** dashed borders, centered content for “no data” scenarios.
- **Forms (`.form-card`):** centered cards with rounded inputs, pill buttons, and contextual helper text. Reference the refreshed renew flow in [catalog/templates/catalog/book_renew_librarian.html](catalog/templates/catalog/book_renew_librarian.html).

## Interaction Guidelines
1. Primary actions use `btn btn-primary` with icon prefixes; secondary/back links use `btn-outline-secondary`.
2. Always surface contextual information (borrower, due date, counts) in either `.intro-card` or `.info-grid` blocks above the action form.
3. Highlight urgency with `status-maintenance` (red) for overdue items and `status-on-loan` (amber) for active loans.
4. Provide helper text below inputs (`.form-text`) and inline validation via `invalid-feedback d-block`.

## Creating a New Page
1. Extend `base_generic.html`, wrap content with `.content-panel`.
2. Start with an `intro-card` or hero section describing the context.
3. Choose the component pattern that matches the content (table, entity cards, form card).
4. Use icons + concise Hebrew copy, keeping buttons descriptive.
5. When in doubt, inspect the referenced templates and reuse their structure.

Following these patterns ensures future pages inherit the calm, modern dashboard feel established across the app.
