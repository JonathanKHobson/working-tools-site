#!/usr/bin/env python3
"""Project verified releases reachable from one public registry commit."""
import argparse
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import quote

PUBLIC_REPOSITORY = 'https://github.com/JonathanKHobson/working-tools-plugins'


def project(checkout, revision, site_root):
    def git(*args):
        return subprocess.check_output(['git', '-C', str(checkout), *args], text=True)

    remote = git('remote', 'get-url', 'origin').strip()
    if remote.removesuffix('.git') != PUBLIC_REPOSITORY:
        raise SystemExit('Expected the public Working Tools Plugins source')
    sha = git('rev-parse', revision + '^{commit}').strip()
    data = json.loads(git('show', sha + ':catalog/packages.json'))
    merch = json.loads((site_root / 'data/storefront-copy.json').read_text())
    excluded = set(merch.get('excluded_ids', []))
    current = [r for r in data['packages'] if r['id'] not in excluded]
    releases = {r['id']: (r, sha) for r in current if r['distribution'] == 'released'}
    pending = {r['id'] for r in current if r['distribution'] == 'prepared'}

    # A candidate must not remove the version visitors can already install.
    # Removed, excluded or explicitly withdrawn identities are never restored.
    if pending:
        for prior in git('rev-list', '--first-parent', sha, '--', 'catalog/packages.json').splitlines():
            previous = json.loads(git('show', prior + ':catalog/packages.json'))
            for record in previous['packages']:
                if record['id'] in pending and record['distribution'] == 'released':
                    releases[record['id']] = (record, prior)
                    pending.remove(record['id'])
            if not pending:
                break

    items = []
    for current_record in current:
        if current_record['id'] not in releases:
            continue
        record, source = releases[current_record['id']]
        identity = record['id']
        if identity not in merch['products']:
            raise SystemExit('Missing storefront copy for released package: ' + identity)
        names = git('ls-tree', '-r', '--name-only', source, 'plugins/' + identity + '/skills').splitlines()
        skills = [re.search(r'^name:\s*(.+)$', git('show', source + ':' + n), re.M)[1]
                  for n in names if n.endswith('/SKILL.md')]
        manifest = json.loads(git('show', source + ':plugins/' + identity + '/.codex-plugin/plugin.json'))
        display_name = manifest.get('interface', {}).get('displayName', record['name'])
        storefront = merch['products'][identity]
        if 'name' in storefront and storefront['name'] != display_name:
            raise SystemExit('Storefront name differs from the released plugin: ' + identity)
        item = {k: record[k] for k in ['id', 'version', 'description', 'requirements', 'edition', 'license']}
        item['name'] = display_name
        aliases = {'market': 'write', 'play': 'table', 'security': 'build', 'review': 'build'}
        jobs = list(dict.fromkeys(aliases.get(job, job) for job in record.get('jobs', ['build'])))
        item.update(storefront, skill_names=skills, jobs=jobs, source_revision=source,
                    release_url=PUBLIC_REPOSITORY + '/releases/tag/' + identity + '/' + quote('v' + record['version'], safe=''))
        items.append(item)
    return {'schema_version': 'working-tools.plugins.v1', 'source_repository': remote,
            'source_revision': sha, 'packages': items}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('checkout', type=Path)
    parser.add_argument('revision')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = project(args.checkout, args.revision, root)
    (root / 'data/plugin-releases.json').write_text(json.dumps(output, indent=2) + '\n')
    print(f"Projected {len(output['packages'])} released packages from {output['source_revision']}")


if __name__ == '__main__':
    main()
