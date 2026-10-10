# Working Tools

Practical AI plugins and workflows for writing, research, design, building,
teaching, and creative production. Choose one tool for the work you need to do,
try it on a real task, and shape the result yourself.

- **Find your next workflow:** [Working Tools catalog](https://working-tools.jkylehobson.chatgpt.site/)
- **Install a plugin:** [Working Tools Plugins](https://github.com/JonathanKHobson/working-tools-plugins)
- **Start with an example:** [First workflows](https://github.com/JonathanKHobson/working-tools-plugins/blob/main/docs/workflows.md)
- **Earlier products and downloads:** [Legacy library](https://working-tools.jkylehobson.chatgpt.site/legacy/)

## Maintained source

This is the maintained catalog source at
[JonathanKHobson/working-tools-site](https://github.com/JonathanKHobson/working-tools-site).
It preserves the public Compass Suite source history. The predecessor
[compass-suite](https://github.com/JonathanKHobson/compass-suite) is a historical
compatibility host; its Pages URLs, shared assets and release links stay in place.
The generated Site checkout is a publication artifact, not this source repository.

## What this repository contains

This repository contains the public catalog source, shared site assets, legal
notices, and compatibility pages that keep older Working Tools links usable.
The live catalog leads with current plugin releases. Installation, source,
dependencies, licenses, and contribution guidance live with each package in
[Working Tools Plugins](https://github.com/JonathanKHobson/working-tools-plugins).

Earlier product pages remain here for continuity and are reachable from one
legacy library link. They are historical editions; use the current catalog to
choose today's tools.

## Preview and verify

```bash
python3 -m http.server 8787
python3 scripts/validate_suite_site.py
python3 scripts/validate_suite_site.py --check-links
```

The catalog is a reviewed projection of `data/plugin-releases.json`. Its pinned
source revision is recorded in that file. `data/storefront-copy.json` contains
visitor-facing descriptions and product groupings; technical package facts stay
in the plugin repository. `suite-manifest.json` preserves historical release
and download records.

The builder retains `compass-suite` as a historical route key in
`sites-sources.json`, but its catalog input is pinned to this repository. Companion
legacy repositories remain read-only inputs; their public paths are unchanged.
