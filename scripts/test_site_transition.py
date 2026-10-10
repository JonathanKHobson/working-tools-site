"""Regression checks for archive navigation in the published Site build."""
import unittest

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


if __name__ == "__main__":
    unittest.main()
