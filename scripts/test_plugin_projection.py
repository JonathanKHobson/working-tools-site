"""Release continuity and product-name regression checks with a local Git history."""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from sync_plugin_registry import PUBLIC_REPOSITORY, project


class ReleaseProjectionTests(unittest.TestCase):
    def test_candidate_preserves_verified_release_and_exclusions(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repository, site = root / 'repository', root / 'site'
            repository.mkdir()
            (repository / 'catalog').mkdir()
            (site / 'data').mkdir(parents=True)

            def git(*args):
                return subprocess.check_output(['git', '-C', str(repository), *args], text=True).strip()

            git('init', '-q')
            git('config', 'user.name', 'Projection Fixture')
            git('config', 'user.email', 'fixture@example.invalid')
            git('remote', 'add', 'origin', PUBLIC_REPOSITORY + '.git')

            def record(identity, version, state, display):
                package = repository / 'plugins' / identity
                (package / '.codex-plugin').mkdir(parents=True, exist_ok=True)
                (package / 'skills' / 'sample').mkdir(parents=True, exist_ok=True)
                (package / '.codex-plugin/plugin.json').write_text(json.dumps({'interface': {'displayName': display}}))
                (package / 'skills/sample/SKILL.md').write_text('---\nname: sample-' + version + '\n---\n')
                return dict(id=identity, name=display, version=version, distribution=state,
                            description='Fixture', requirements=['A task'], edition='Fixture', license='MIT')

            def commit(records, message):
                (repository / 'catalog/packages.json').write_text(json.dumps({'packages': records}))
                git('add', '.')
                git('commit', '-qm', message)
                return git('rev-parse', 'HEAD')

            stable = record('reasoning-studio', '1.0.0', 'released', 'Reasoning Toolkit')
            private = record('discord', '1.0.0', 'released', 'Discord')
            old = commit([stable, private], 'Verified release')
            candidate = record('reasoning-studio', '2.0.0', 'prepared', 'Candidate label')
            new = record('new-package', '1.0.0', 'prepared', 'New Package')
            head = commit([candidate, private, new], 'Unverified candidates')
            merchandising = {'products': {'reasoning-studio': {'family': 'toolkits'}}, 'excluded_ids': ['discord']}
            copy = site / 'data/storefront-copy.json'
            copy.write_text(json.dumps(merchandising))
            projected = project(repository, head, site)
            self.assertEqual(len(projected['packages']), 1)
            item = projected['packages'][0]
            self.assertEqual((item['name'], item['version'], item['skill_names']),
                             ('Reasoning Toolkit', '1.0.0', ['sample-1.0.0']))
            self.assertEqual(item['source_revision'], old)
            self.assertEqual(projected['source_revision'], head)

            merchandising['products']['reasoning-studio']['name'] = 'Reasoning Studio'
            copy.write_text(json.dumps(merchandising))
            with self.assertRaisesRegex(SystemExit, 'Storefront name differs'):
                project(repository, head, site)
            del merchandising['products']['reasoning-studio']['name']
            copy.write_text(json.dumps(merchandising))
            released = record('reasoning-studio', '2.0.0', 'released', 'Reasoning Toolkit')
            promoted = commit([released, private, new], 'Verified successor')
            self.assertEqual(project(repository, promoted, site)['packages'][0]['version'], '2.0.0')
            extended = record('reasoning-studio', '2.0.1+ecosystem.20261010', 'released', 'Reasoning Toolkit')
            extended_head = commit([extended, private, new], 'Verified extended version')
            self.assertTrue(project(repository, extended_head, site)['packages'][0]['release_url'].endswith(
                '/v2.0.1%2Becosystem.20261010'))
            withdrawn = commit([private, new], 'Remove product')
            self.assertEqual(project(repository, withdrawn, site)['packages'], [])


if __name__ == '__main__':
    unittest.main()
