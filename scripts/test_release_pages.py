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

    def write_history(self, products=None):
        self.history.write_text(json.dumps({"schema_version": "working-tools.releases.v1", "products": products if products is not None else [self.product]}))

    def test_renders_complete_history_and_exact_download(self):
        self.write_history()
        self.assertEqual(render(self.history, self.output), (1, 4))
        product_page = (self.output / "sample-studio/index.html").read_text()
        directory = (self.root / "releases/index.html").read_text()
        release_page = (self.output / "sample-studio/releases/1.0.0+test/index.html").read_text()
        prior_page = (self.output / "sample-studio/releases/0.9.0/index.html").read_text()
        self.assertIn("Recorded history", product_page)
        self.assertIn("Current plugins", directory)
        self.assertIn("v0.9.0", product_page)
        self.assertIn("Download v1.0.0+test ZIP", product_page)
        self.assertIn("/releases/1.0.0%2Btest/", product_page)
        self.assertIn("https://github.com/example/releases/download", release_page)
        self.assertIn("SHA-256 " + "a" * 64, release_page)
        self.assertIn("<h4>Changes</h4>", release_page)
        self.assertNotIn("<script>alert(1)</script>", release_page)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", release_page)
        self.assertIn("No public download is confirmed", prior_page)

    def test_page_only_guide_and_frozen_legacy_are_discoverable(self):
        guide = {
            "id": "understanding-ai-2026", "name": "Understanding AI in 2026", "kind": "external",
            "product_kind": "guide", "lifecycle": "active-guide-page", "current_release_key": None,
            "releases": [{"release_key": "legacy:understanding-ai-2026:" + "c" * 40,
                          "version": None, "version_scheme": "revision", "source_commit": "c" * 40,
                          "page_url": "https://example.org/guide/", "distribution_status": "page-only",
                          "assets": []}],
        }
        legacy = {
            "id": "old-tool", "name": "Old Tool", "kind": "external", "product_kind": "plugin",
            "lifecycle": "frozen-legacy", "current_release_key": None,
            "releases": [{"release_key": "legacy:old-tool:" + "d" * 40,
                          "version": None, "version_scheme": "revision", "source_commit": "d" * 40,
                          "distribution_status": "available", "assets": []}],
        }
        self.write_history([self.product, guide, legacy])
        self.assertEqual(render(self.history, self.output), (3, 8))
        directory = (self.root / "releases/index.html").read_text()
        guide_page = (self.output / "understanding-ai-2026/index.html").read_text()
        guide_record = (self.output / ("understanding-ai-2026/releases/revision-" + "c" * 12 + "/index.html")).read_text()
        legacy_page = (self.output / "old-tool/index.html").read_text()
        self.assertIn("Active guides", directory)
        self.assertIn("Preserved resources", directory)
        self.assertIn("Open the guide", guide_page)
        self.assertNotIn("No current downloadable edition", guide_page)
        self.assertIn("Source revision ccccccc", guide_record)
        self.assertIn("preserved earlier resource", legacy_page)

    def test_active_guide_shows_only_verified_direct_files(self):
        guide = {
            "id": "safe-install-review", "name": "Safe Install Review", "kind": "external",
            "product_kind": "skill", "lifecycle": "active-guide-download", "current_release_key": None,
            "releases": [{"release_key": "legacy:safe-install-review:" + "e" * 40,
                          "version": None, "version_scheme": "revision", "source_commit": "e" * 40,
                          "page_url": "https://example.org/mcp/", "distribution_status": "available",
                          "assets": [{"role": "skill-file", "name": "safe-install-review.skill",
                                      "url": "https://example.org/safe-install-review.skill",
                                      "verification": "public-download-bytes"},
                                     {"role": "skill-zip", "name": "unverified.zip",
                                      "url": "https://example.org/unverified.zip"}]}],
        }
        self.write_history([guide])
        render(self.history, self.output)
        page = (self.output / "safe-install-review/index.html").read_text()
        self.assertIn("Open the guide", page)
        self.assertIn("Download safe-install-review.skill", page)
        self.assertNotIn("Download unverified.zip", page)

    def test_external_file_records_withhold_unverified_links_and_show_authored_notes(self):
        legacy = {
            "id": "old-tool", "name": "Old Tool", "kind": "external", "product_kind": "skill",
            "lifecycle": "frozen-legacy", "current_release_key": None,
            "releases": [{"release_key": "legacy:old-tool:" + "d" * 40,
                          "version": "0.1.0", "source_commit": "d" * 40,
                          "distribution_status": "available", "release_notes": "## Original changes\n\nThe first edition.",
                          "assets": [{"role": "skill-file", "name": "old-tool.skill",
                                      "url": "https://example.org/old-tool.skill",
                                      "verification": "git-blob-only"}]}],
        }
        self.write_history([legacy])
        render(self.history, self.output)
        product = (self.output / "old-tool/index.html").read_text()
        detail = (self.output / "old-tool/releases/0.1.0/index.html").read_text()
        self.assertIn("File record, download unverified", product)
        self.assertIn("<h4>Original changes</h4>", detail)
        self.assertIn("A public download has not been verified for this file", detail)
        self.assertNotIn('href="https://example.org/old-tool.skill"', detail)

    def test_integration_uses_host_setup_language(self):
        integration = dict(self.product, id="sample-hooks", name="Sample Hooks", kind="integration")
        self.write_history([integration])
        render(self.history, self.output)
        product = (self.output / "sample-hooks/index.html").read_text()
        directory = (self.root / "releases/index.html").read_text()
        self.assertIn("Set up this integration", product)
        self.assertIn("host-specific setup and trust instructions", product)
        self.assertIn("Current plugins and integrations", directory)

    def test_source_verification_exception_keeps_original_release_context(self):
        historical = self.product["releases"][1]
        historical["distribution_status"] = "unavailable"
        historical["verification"] = {"reason": "Package checksum matches, but a generated source file is absent."}
        historical["release_url"] = "https://github.com/example/releases/tag/sample-studio-v0.9.0"
        historical["assets"] = [{"role": "installation", "name": "sample-studio-0.9.0.zip",
                                 "url": "https://github.com/example/releases/download/sample-studio-v0.9.0/sample-studio.zip"}]
        self.write_history()
        render(self.history, self.output)
        page = (self.output / "sample-studio/releases/0.9.0/index.html").read_text()
        self.assertIn("Source verification exception", page)
        self.assertIn("Package checksum matches, but a generated source file is absent.", page)
        self.assertIn('href="https://github.com/example/releases/tag/sample-studio-v0.9.0"', page)
        self.assertNotIn('href="https://github.com/example/releases/download/sample-studio-v0.9.0/sample-studio.zip"', page)
        self.assertIn("original release may still host this file", page)

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
