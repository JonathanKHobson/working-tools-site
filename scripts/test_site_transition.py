"""Regression checks for archive navigation and immutable catalog build output."""
import hashlib
import io
import json
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import build_working_tools_site as builder
from build_working_tools_site import SOURCE_REPOSITORIES, destination, LEGACY_ROUTES, legacy_redirect, rewrite


class TransitionTests(unittest.TestCase):
    def test_catalog_owner_changes_without_renaming_historical_route(self):
        self.assertEqual(SOURCE_REPOSITORIES['compass-suite'], 'working-tools-site')
        self.assertEqual(destination('compass-suite', 'index.html'), 'index.html')
        html = '<a href="downloads/historical.zip">Download</a>'
        self.assertIn('https://jonathankhobson.github.io/compass-suite/downloads/historical.zip',
                      rewrite(html, 'compass-suite', 'index.html', None))

    def test_original_legacy_destination_stays_external(self):
        html = '<a href="https://jonathankhobson.github.io/critical-compass/?_legacy=1#downloads">Original</a>'
        self.assertEqual(rewrite(html, "compass-suite", "legacy/index.html", None), html)

    def test_current_navigation_moves_to_site(self):
        html = '<a href="https://jonathankhobson.github.io/critical-compass/">Earlier product</a>'
        self.assertIn('href="/critical-compass/"', rewrite(html, "compass-suite", "index.html", None))

    def test_download_keeps_original_endpoint(self):
        html = '<a href="https://jonathankhobson.github.io/critical-compass/package.zip">Download</a>'
        self.assertEqual(rewrite(html, "compass-suite", "legacy/index.html", None), html)

    def test_retired_product_paths_have_recovery_without_javascript(self):
        self.assertTrue({"critical-compass", "prompt-compass", "ux-heuristic-compass", "job-application-compass", "humanizer"}.issubset(LEGACY_ROUTES))
        html = legacy_redirect().decode()
        self.assertIn('content="0;url=/legacy/"', html)
        self.assertIn('href="/legacy/"', html)
        self.assertIn("destination.search = location.search", html)
        self.assertIn("destination.hash = location.hash", html)

    def test_builder_preserves_release_catalog_bytes_and_manifest_digest(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data").mkdir()
            catalog = (b'{ "schema_version": "working-tools.releases.v1",\n'
                       b'  "original_url": "https://jonathankhobson.github.io/compass-suite/original/",\n'
                       b'  "download_url": "https://jonathankhobson.github.io/critical-compass/package.zip",\n'
                       b'  "guide_url": "https://humanizer-writing-tools.jkylehobson.chatgpt.site/" }\n')
            (root / "data/release-history.json").write_bytes(catalog)
            (root / "index.html").write_text('<a href="https://jonathankhobson.github.io/compass-suite/guide/">Guide</a>')
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(["git", "-C", str(root), "remote", "add", "origin",
                            "https://github.com/JonathanKHobson/working-tools-site.git"], check=True)
            subprocess.run(["git", "-C", str(root), "add", "data/release-history.json", "index.html"], check=True)
            subprocess.run(["git", "-C", str(root), "-c", "user.name=Test", "-c", "user.email=test@example.org",
                            "commit", "-qm", "Fixture"], check=True)
            revision = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
            (root / "sites-sources.json").write_text(json.dumps({"sources": {"compass-suite": {"sha": revision, "checkout": "."}}}))
            (root / "data/release-history.json").write_text('{"working_tree_only": true}')
            output = root / "dist"
            with (patch.object(builder, "ROOT", root), patch.object(builder, "PINS", root / "sites-sources.json"),
                  patch.object(builder, "OUTPUT", output), patch.object(builder, "REPOS", ("compass-suite",)),
                  patch("sys.argv", ["build_working_tools_site.py"]), redirect_stdout(io.StringIO())):
                builder.main()
            self.assertEqual((output / "data/release-history.json").read_bytes(), catalog)
            manifest = json.loads((output / "build-manifest.json").read_text())
            entry = next(item for item in manifest["files"] if item["output"] == "data/release-history.json")
            self.assertEqual(entry["sha256"], hashlib.sha256(catalog).hexdigest())
            self.assertEqual(entry["bytes"], len(catalog))
            self.assertEqual(entry["source"], f"working-tools-site@{revision}:data/release-history.json")
            self.assertIn('href="/guide/"', (output / "index.html").read_text())


if __name__ == "__main__":
    unittest.main()
