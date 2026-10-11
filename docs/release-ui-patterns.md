# Release pages

The public catalog keeps a short task-led card. The primary action links to the exact installation ZIP for the current verified edition, with its version and publication date visible. The secondary action opens `/plugins/<id>/`, where visitors can compare every published edition. A version page at `/plugins/<id>/releases/<version>/` keeps its notes, fixed release files, and checksums together.

`data/release-history.json` is the reviewed release projection. `scripts/render_release_pages.py` renders static HTML from it; the generated `plugins/` pages are publication source, not an independent record of release state. Re-run the renderer after changing history and inspect the diff. The main card reads the same file at runtime, while its existing `data/plugin-releases.json` still supplies names, task filters, and package detail. The Site build copies only files present in its pinned source commit, so render and commit the pages before advancing `sites-sources.json`.

The renderer rejects known private identities before writing pages. The source projection must still make the full public/private selection deliberately; the page renderer is a second guard, not a release approval system.

The page follows the current paper, ink, rule, and vermilion system. It uses native links and document headings. Available stable editions may have a recommended installation action; preview or unavailable records remain in history without that action. The release page links every listed asset by its exact URL and shows its SHA-256 when supplied. GitHub remains the file host and release record. Common Markdown headings, lists, links, emphasis, and code render through a small escaped parser. Raw HTML cannot execute. The original GitHub release remains linked for its full source context.

For a bounded rendered review, inspect these source anchors on the homepage and generated pages at 1280 × 900 and 390 × 844. Record the actual visible result, focus path, and any correction before claiming publication quality.

| ID | Page and region | Source anchor | Existing observation | Intended changed action |
| --- | --- | --- | --- | --- |
| R1 | Home, library row | `assets/js/catalog.js` / `.library-row` | Current cards point to a tag page | Show exact current ZIP, version/date, and all-releases link |
| R2 | Product, top | `plugins/<id>/index.html` / `.release-intro` | New page | Name the product, current edition, and install path immediately |
| R3 | Product, history | `.release-history` | New page | Show every edition in order, including preview or unavailable states |
| R4 | Version, files | `.release-assets` | New page | Keep fixed asset links, roles, sizes, and checksums legible |
| R5 | Version, notes | `.release-notes-text` | New page | Preserve full text safely and link the original release |
| R6 | Narrow viewport | `.release-columns`, `.release-history-row` | New page | Stack sections and actions without overflow; keep focus and touch targets usable |

Verification: `python3 scripts/test_release_pages.py`, `python3 scripts/validate_suite_site.py`, then `python3 scripts/render_release_pages.py` after the history data is ready. Preview with `python3 -m http.server 8787` from this checkout and follow the homepage and generated routes. Browser interaction and downloaded-byte checks remain separate from source validation.
