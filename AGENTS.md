# Working Tools maintenance

This maintained source is JonathanKHobson/working-tools-site. Compass Suite is
the preserved historical Pages/asset host; do not update or rename those URLs.
The builder retains its route key while selecting this repository as the catalog
source. Keep generated Site history out of this source repository.

Read README.md and docs/project-map.md. data/plugin-releases.json is the pinned projection of current public plugin releases; regenerate it from the verified public package registry. data/storefront-copy.json owns product descriptions and grouping, and data/tool-library.json owns the standalone public guides. suite-manifest.json preserves historical Compass release and download records. Keep editorial changes aligned with content/site-copy.md.

Run `python3 scripts/validate_suite_site.py`; use `--check-links` when public destinations change. Browser QA is required for affected page interactions and layout. The site is static and needs no package installation for its documented validator or Python preview.

Other Compass sites consume shared assets from this repository. Preserve public asset paths, legal pages and compatibility routes. Shared portfolio network source is maintained separately and copied deliberately; do not confuse that update-time dependency with assets fetched at runtime.

Keep private systems and unshipped packages out of the public catalog. A successor release requires its own verified installation and distribution evidence. Preserve existing download URLs while successors are prepared.
