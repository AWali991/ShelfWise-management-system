# ShelfWise accessibility check (WCAG 2.2 level AA)

The page design (HTML and CSS) was made by Sahan. Before it went into the app we checked the
colours and keyboard use against WCAG 2.2 level AA (W3C, 2023) and changed what failed.

| Check | Sahan's original stylesheet | Final ShelfWise stylesheet |
|---|---|---|
| Text contrast below 4.5:1 (or 3:1 for large text) | 1,169 | 0 |
| Keyboard focus not visible | 386 | 0 |
| Buttons or fields smaller than 24 x 24 px | 50 | 0 |
| **Total problems (every page at desktop and phone width)** | **1,605** | **0** |

How to repeat the check: start ShelfWise (`python run.py`), then run `python tools/a11y_check.py`.
It needs Playwright. Results are saved in `docs/accessibility_results.json`;
the "before" figures are in `docs/accessibility_before.json`.
`python tools/contrast.py` prints the contrast ratio of any colour pair.

## Brand colour

The group later changed the brand colour from green to navy blue (side menu #1b2a4a, buttons and links #2456a6, 7.1:1 with white text). The check was run again and still found 0 problems. After the low stock alerts page was added, the check covers 25 pages (50 page views) and still finds 0 problems.

## Main colour changes

| Used for | Before | Ratio | After | Ratio |
|---|---|---|---|---|
| Grey helper text (on page background) | #697b72 | 4.2:1 | #4b5768 | 6.8:1 |
| Breadcrumb | #83978b | 2.9:1 | #4b5768 | 6.8:1 |
| Card footnotes | #819288 | 3.3:1 | #4b5768 | 7.3:1 |
| Table headings | #76867b on #fafcfa | 3.7:1 | #3a4556 on #f2f5f9 | 8.9:1 |
| Footer | #92a198 | 2.5:1 | #4b5768 | 6.8:1 |
| Warning (amber) text | #b66f05 | 4.0:1 | #8a5100 | 6.5:1 |
| "Used" / "Low stock" badge | #aa6700 on #fff2da | 4.1:1 | #7a4700 on #fff2da | 7.0:1 |
| Form field and outline-button borders | #ccd9d0 | 1.5:1 | #6e7d92 | 4.2:1 |
| Keyboard focus ring | 12% green glow | 1.2:1 | 3 px #111c33 outline (yellow on the side menu) | 17.0:1 |

## Other changes
- "Skip to main content" link, `<main>` landmark, `aria-current="page"` on the menu.
- Table headings use `<th scope="col">`; totals use `<tfoot>`.
- The daily sales chart has a "Show the chart as a table" option for screen reader users.
- Badges always contain a word, so colour is never the only clue.
- Icons in the menu are hidden from screen readers; the sale total is announced when it changes.
- Required fields are marked with a red star and the `required` attribute; hints are linked with `aria-describedby`.
- Show / Hide password button has `aria-pressed`.

Reference: W3C (2023) *Web Content Accessibility Guidelines (WCAG) 2.2*. Available at: https://www.w3.org/TR/WCAG22/
