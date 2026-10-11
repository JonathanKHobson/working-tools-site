"""Fixture checks for the static release-page renderer."""

import json
import tempfile
import unittest
from pathlib import Path

from render_release_pages import render


class ReleasePageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.history = self.root / "history.json"
        self.output = self.root / "plugins"
        self.product = {
            "id": "sample-studio",
            "name": "Sample Studio",
            "kind": "plugin",
            "repository": "Example/sample-studio",
            "compatibility": "Codex and Claude",
            "upgrade_guidance": "Save your local settings first.",
            "current_release_key": "sample-studio/v1.0.0+test",
            "releases": [
                {
                    "release_key": "sample-studio/v1.0.0+test",
                    "product_id": "sample-studio",
                    "version": "1.0.0+test",
                    "git_tag": "sample-studio/v1.0.0+test",
                    "published_at": "2026-10-11T04:31:11Z",
                    "release_url": "https://github.com/example/releases/tag/sample-studio/v1.0.0%2Btest",
                    "channel": "stable",
                    "distribution_status": "available",
                    "summary": "A clearer first run.",
                    "notes": "## Changes\n\nFixed <script>alert(1)</script>.",
                    "assets": [
                        {"role": "installation", "name": "sample-studio-1.0.0+test.zip", "url": "https://github.com/example/releases/download/sample-studio/v1.0.0%2Btest/sample-studio.zip", "size": 1024, "sha256": "a" * 64},
                        {"role": "checksum", "name": "sample-studio.sha256", "url": "https://github.com/example/releases/download/sample-studio/v1.0.0%2Btest/sample-studio.sha256", "size": 64, "sha256": "b" * 64},
                    ],
                },
                {
                    "release_key": "sample-studio/v0.9.0",
                    "product_id": "sample-studio",
                    "version": "0.9.0",
                    "published_at": "2026-10-10T04:31:11Z",
                    "channel": "preview",
                    "distribution_status": "unavailable",
                    "summary": "Earlier test edition.",
                    "assets": [],
                },
            ],
        }

    def write_history(self):
        self.history.write_text(json.dumps({"schema_version": "working-tools.releases.v1", "products": [self.product]}))

    def test_renders_complete_history_and_exact_download(self):
        self.write_history()
        self.assertEqual(render(self.history, self.output), (1, 3))
        product_page = (self.output / "sample-studio/index.html").read_text()
        release_page = (self.output / "sample-studio/releases/1.0.0+test/index.html").read_text()
        prior_page = (self.output / "sample-studio/releases/0.9.0/index.html").read_text()
        self.assertIn("All releases", product_page)
        self.assertIn("v0.9.0", product_page)
        self.assertIn("Download v1.0.0+test ZIP", product_page)
        self.assertIn("/releases/1.0.0%2Btest/", product_page)
        self.assertIn("https://github.com/example/releases/download", release_page)
        self.assertIn("SHA-256 " + "a" * 64, release_page)
        self.assertIn("<h4>Changes</h4>", release_page)
        self.assertNotIn("<script>alert(1)</script>", release_page)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", release_page)
        self.assertIn("No recommended download", prior_page)

    def test_rejects_path_traversal_identity(self):
        self.product["id"] = "../private"
        self.write_history()
        with self.assertRaisesRegex(ValueError, "Invalid product ID"):
            render(self.history, self.output)

    def test_rejects_known_private_identity(self):
        self.product["id"] = "mental-health-navigation"
        self.write_history()
        with self.assertRaisesRegex(ValueError, "Private product"):
            render(self.history, self.output)

    def test_rejects_non_https_asset_action(self):
        self.product["releases"][0]["assets"][0]["url"] = "javascript:alert(1)"
        self.write_history()
        render(self.history, self.output)
        product_page = (self.output / "sample-studio/index.html").read_text()
        self.assertNotIn("javascript:alert", product_page)
        self.assertNotIn("Download v1.0.0+test ZIP", product_page)

    def test_removes_only_stale_generated_pages(self):
        self.write_history()
        render(self.history, self.output)
        stale = self.output / "sample-studio/releases/0.9.0/index.html"
        manual = self.output / "manual/index.html"
        manual.parent.mkdir()
        manual.write_text("<!doctype html><title>Manual page</title>")
        self.product["releases"].pop()
        self.write_history()
        render(self.history, self.output)
        self.assertFalse(stale.exists())
        self.assertTrue(manual.exists())


if __name__ == "__main__":
    unittest.main()
