# Working Tools project map

## Purpose

`JonathanKHobson/working-tools-site` owns the maintained Working Tools public catalog source, shared site
assets, and compatibility pages for older releases. The live storefront leads
with the released plugin ecosystem; GitHub package pages carry installation,
dependencies, source, and license details.

## Entrypoints

- `behind-the-tools/index.html`: public context, privacy and host-hook explanation.
- `assets/css/system-context.css`: page-scoped layout using the shared palette and typography.

- `index.html`: main catalog page, task filters, and storefront calls to action.
- `assets/js/catalog.js`: loads the released package projection and current
  standalone public guides, groups products, and renders accessible filters.
- `data/storefront-copy.json`: visitor-facing product descriptions and family
  groupings. It does not replace package technical metadata.
- `data/plugin-releases.json`: immutable projection of released public plugin
  packages, versioned destinations, skills, technical details, and source
  revision. Regenerate it from the public plugin source with
  `scripts/sync_plugin_registry.py`.
- `data/tool-library.json`: standalone public guides shown beside plugins.
- `legacy/index.html`: one entry point to preserved earlier product pages.
- `migration/forward.js`: keeps original GitHub Pages routes available.
- `scripts/build_working_tools_site.py`: builds the hosted projection from
  pinned commits and turns retired product pages into Legacy Library redirects,
  while preserving original archive and download destinations.
- `suite-manifest.json`: historical release status, preserved download URLs,
  checksums, and continuity constraints.
- `scripts/validate_suite_site.py`: catalog, privacy, content, route, and
  structural checks.

The `compass-suite` source-pin key identifies the historical root route. The
builder resolves that key to `JonathanKHobson/working-tools-site`; it does not
require new commits in the archived predecessor. Other legacy source pins and
all preserved Pages/download URLs retain their names. Update the root source pin
to a verified commit in this repository before a future build. The generated Site
checkout remains separate; a source commit is not a deployment.

## Data flow

1. The catalog loads `data/plugin-releases.json` and `data/tool-library.json`.
2. Released packages are presented with benefit-led copy from
   `data/storefront-copy.json`; each card links to its versioned GitHub release.
   Preparing a successor retains the most recent released version from the pinned
   registry history. Each product records its own source commit. New unverified
   products and excluded or removed identities stay out of the storefront.
3. Requirements, license, scope, and technical package overview stay behind a
   disclosure on the card and in the GitHub package documentation.
4. Earlier products are accessible through the single Legacy Library link.
   Their original GitHub Pages paths and release assets remain preserved.

## Safe changes

- Edit storefront language and grouping in `data/storefront-copy.json`.
- Update technical package facts at their source in `working-tools-plugins`,
  then regenerate the projection with `scripts/sync_plugin_registry.py`.
- Product names come from each released plugin's display name. The projection
  rejects conflicting storefront overrides so local and public names stay aligned.
- Update standalone guide links in `data/tool-library.json`.
- Preserve `suite-manifest.json` release URLs and checksums during the archive
  transition.
- Keep old compatibility files available until every redirect, asset, and
  download destination has been verified from the replacement source.

## Verification

```bash
python3 scripts/validate_suite_site.py
python3 scripts/test_site_transition.py
python3 scripts/test_plugin_projection.py
python3 scripts/validate_suite_site.py --check-links
```

Use a local HTTP preview for catalog interaction checks. Before publishing,
verify desktop and mobile layouts, keyboard focus, filter states, package links,
and legacy destinations in a rendered browser.
