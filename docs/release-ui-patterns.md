# Release pages

The public catalog keeps a short task-led card. A current plugin or optional integration card links to its exact installation ZIP, with its version and publication date visible. Its history link opens `/plugins/<id>/`. Current guide cards link to the relevant product histories too. `/releases/` lists all public products in current plugin and integration, active guide, and preserved resource groups. A record page at `/plugins/<id>/releases/<version-or-revision>/` keeps notes, file evidence, and checksums together. These are recorded editions, including page-only and unavailable entries; a record does not by itself mean a public download was verified.

`data/release-history.json` is the reviewed release projection. `scripts/render_release_pages.py` renders static HTML from it; the generated `plugins/` pages are publication source, not an independent record of release state. Re-run the renderer after changing history and inspect the diff. The main card reads the same file at runtime, while its existing `data/plugin-releases.json` still supplies names, task filters, and package detail. The Site build copies only files present in its pinned source commit, so render and commit the pages before advancing `sites-sources.json`.

The renderer rejects known private identities before writing pages. The source projection must still make the full public/private selection deliberately; the page renderer is a second guard, not a release approval system.

The page follows the current paper, ink, rule, and vermilion system. It uses native links and document headings. Available stable plugin editions may have a recommended installation action; preview or unavailable records remain in history without that action. Active page-only guides offer an Open guide action. External asset links appear only when exact public download bytes have been verified; unverified file records remain visible with their status. A record that fails exact source verification shows the reason and can still link to its original GitHub release, which may host a historical file. Supplied SHA-256 values appear beside files. GitHub remains the file host and release record when applicable. Common Markdown headings, lists, links, emphasis, and code render through a small escaped parser. Raw HTML cannot execute. The original GitHub release remains linked for its full source context when one exists.

For a bounded rendered review, inspect these source anchors on the homepage and generated pages at 1280 × 900 and 390 × 844. Record the actual visible result, focus path, and any correction before claiming publication quality.

| ID | Page and region | Source anchor | Existing observation | Intended changed action |
| --- | --- | --- | --- | --- |
| R1 | Home, library row | `assets/js/catalog.js` / `.library-row` | Current cards point to a tag page | Show exact current ZIP, version/date, and all-releases link |
| R2 | Product, top | `plugins/<id>/index.html` / `.release-intro` | New page | Name the product, current edition, and install path immediately |
| R3 | Product, history | `.release-history` | New page | Show every edition in order, including preview or unavailable states |
| R4 | Version, files | `.release-assets` | New page | Keep fixed asset links, roles, sizes, and checksums legible |
| R5 | Version, notes | `.release-notes-text` | New page | Preserve full text safely and link the original release |
| R6 | Narrow viewport | `.release-columns`, `.release-history-row` | New page | Stack sections and actions without overflow; keep focus and touch targets usable |
| R7 | Directory, groups | `releases/index.html` / `.release-directory-group` | New page | Show all public products and honest per-group counts |
| R8 | Active guide and preserved record | `plugins/<id>/index.html` / `.release-intro` | New page | Open public guides; distinguish verified files from source-only evidence |

Verification: `python3 scripts/test_release_pages.py`, `python3 scripts/validate_suite_site.py`, then `python3 scripts/render_release_pages.py` after the history data is ready. Preview with `python3 -m http.server 8787` from this checkout and follow the homepage and generated routes. The fixture tests and local route audit verify source logic and generated links only; they do not establish rendered viewport quality, interaction behavior, deployed availability, or downloaded-byte checks. Record those outcomes separately after browser review and publication.
