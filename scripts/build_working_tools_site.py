#!/usr/bin/env python3
"""Build one static Working Tools Site from pinned public Git revisions.

The companion sites-sources.json pins the source commits. The output directory is a
publication artifact, never a second editable source tree.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
PINS = ROOT / "sites-sources.json"
OUTPUT = ROOT / "dist"
PAGES = "https://jonathankhobson.github.io"
REPOS = (
    "compass-suite",
    "critical-compass",
    "prompt-compass",
    "job-application-compass",
    "ux-heuristic-compass",
    "what-is-an-mcp",
)
RUNTIME_SUFFIXES = {
    ".html", ".css", ".js", ".mjs", ".json", ".png", ".jpg",
    ".jpeg", ".gif", ".webp", ".svg", ".ico", ".woff",
    ".woff2", ".ttf", ".otf", ".webm", ".mp4", ".avif",
}
# Historical route names remain stable after source ownership changes.
SOURCE_REPOSITORIES = {"compass-suite": "working-tools-site"}
DOWNLOAD_SUFFIXES = {".zip", ".skill", ".mcpb", ".pdf", ".md", ".txt"}
TEXT_SUFFIXES = {".html", ".css", ".js", ".mjs", ".json", ".svg"}
IGNORED_PREFIXES = (".git/", ".openai/", "docs/", "scripts/", "content/", "legal/", "snippets/", "output/", "vendor/", "site-sources/")
EXCLUDED_RUNTIME_FILES = {"404.html"}
MCP_SITE = "https://what-is-an-mcp.jkylehobson.chatgpt.site/"
LEGACY_ROUTES = {
    "critical-compass", "prompt-compass", "job-application-compass",
    "ux-heuristic-compass", "creative-writing-studio", "marketing-social-studio",
    "career-grants-studio", "ux-design-toolkit", "builder-tools",
    "ttrpg-gm-director", "humanizer",
}


def legacy_redirect() -> bytes:
    """Retire current-site product pages without discarding their old URLs."""
    return b'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex"><title>Legacy Library | Working Tools</title>
<meta http-equiv="refresh" content="0;url=/legacy/">
<script>const destination = new URL('/legacy/', location.origin);
destination.search = location.search; destination.hash = location.hash;
location.replace(destination.href);</script></head>
<body><p>This earlier product is in the <a href="/legacy/">Legacy Library</a>.
For current tools, <a href="/#library">explore the plugin catalog</a>.</p></body></html>
'''


def git(repo: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(repo), *args], stderr=subprocess.PIPE)


def destination(repo: str, path: str) -> str:
    """Map a source repository path to the common Site root."""
    return path if repo == "compass-suite" else f"{repo}/{path}"


def rewrite(text: str, repo: str, source_path: str, site_origin: str | None) -> str:
    # Public download and documentary endpoints retain their old response URLs.
    # This includes local example PDFs/Markdown, which are not Site runtime files.
    def relative_download(match: re.Match[str]) -> str:
        quote, target = match.groups()
        parsed = urlparse(target)
        if parsed.scheme or target.startswith(("/", "#", "//")):
            return match.group(0)
        if PurePosixPath(parsed.path).suffix.lower() not in DOWNLOAD_SUFFIXES:
            return match.group(0)
        resolved = (PurePosixPath(source_path).parent / parsed.path).as_posix()
        return f"href={quote}{PAGES}/{repo}/{resolved}{'?' + parsed.query if parsed.query else ''}{'#' + parsed.fragment if parsed.fragment else ''}{quote}"

    text = text.replace("https://humanizer-writing-tools.jkylehobson.chatgpt.site/", "/humanizer/").replace("https://humanizer-writing-tools.jkylehobson.chatgpt.site", "/humanizer/")
    if repo == "compass-suite" and source_path == "data/tool-library.json":
        text = text.replace(
            "https://jonathankhobson.github.io/shareables/s/humanizer-writing-enhancement/",
            "/humanizer/",
        )
    if source_path.endswith(".html"):
        text = re.sub(r"href=([\"'])([^\"']+)\1", relative_download, text)

    for name in REPOS:
        before = f"{PAGES}/{name}/"
        after = "/" if name == "compass-suite" else f"/{name}/"

        def pages_link(match: re.Match[str]) -> str:
            trailing = match.group(1)
            # The archive deliberately links to original Pages with forwarding
            # disabled. Rewriting these would create a loop back to /legacy/.
            if "_legacy=1" in urlparse(trailing).query.split("&"):
                return match.group(0)
            if PurePosixPath(trailing.split("?", 1)[0].split("#", 1)[0]).suffix.lower() in DOWNLOAD_SUFFIXES:
                return match.group(0)
            return after + trailing

        text = re.sub(re.escape(before) + r'([^\s"\'<>`)]*)', pages_link, text)
    text = re.sub(r"(?<![A-Za-z0-9.])/compass-suite/", "/", text)
    text = re.sub(
        re.escape(MCP_SITE) + r'([^\s"\'<>`)]*)',
        lambda match: match.group(0) if PurePosixPath(match.group(1).split("?", 1)[0]).suffix.lower() in DOWNLOAD_SUFFIXES else "/what-is-an-mcp/" + match.group(1),
        text,
    )

    if source_path == "assets/js/network-frame.js" and repo == "compass-suite":
        text = text.replace(
            'const isLibrary = path === "/" && currentPath.startsWith("/");',
            'const isLibrary = path === "/" && !["/critical-compass/", "/prompt-compass/", "/job-application-compass/", "/ux-heuristic-compass/", "/what-is-an-mcp/"].some((prefix) => currentPath.startsWith(prefix));',
        )
    if source_path == "assets/js/catalog.js" and repo == "compass-suite":
        text = text.replace(
            'product.learn_more_url?.startsWith("http") ?',
            '(product.learn_more_url?.startsWith("/") || product.learn_more_url?.startsWith("http")) ?',
        )

    if source_path.endswith(".html"):
        if site_origin:
            text = re.sub(
                r'(<link\s+rel="canonical"\s+href=")[^"]+("\s*/?>)',
                lambda m: m.group(1) + site_origin.rstrip("/") + "/" + destination(repo, source_path).removesuffix("index.html") + m.group(2),
                text,
            )
            text = re.sub(
                r'(<meta\s+property="og:url"\s+content=")[^"]+("\s*/?>)',
                lambda m: m.group(1) + site_origin.rstrip("/") + "/" + destination(repo, source_path).removesuffix("index.html") + m.group(2),
                text,
            )
        else:
            text = re.sub(r'^.*<link\s+rel="canonical"[^>]*>\s*\n?', "", text, flags=re.MULTILINE)
            text = re.sub(r'^.*<meta\s+property="og:url"[^>]*>\s*\n?', "", text, flags=re.MULTILINE)
    return text


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root-revision", help="Exact maintained site commit; overrides the historical root pin for this build")
    parser.add_argument("--site-origin", help="Verified published Site origin for canonical metadata")
    parser.add_argument("--site-project-id", help="Returned Site project ID for build provenance")
    parser.add_argument("--sources-dir", type=Path, help="Directory containing pinned companion Git checkouts by repository name")
    args = parser.parse_args()
    if args.site_origin:
        parsed = urlparse(args.site_origin)
        if parsed.scheme != "https" or not parsed.netloc or parsed.path not in ("", "/"):
            parser.error("--site-origin must be an HTTPS origin with no path")

    pins = json.loads(PINS.read_text())
    if set(pins["sources"]) != set(REPOS):
        raise SystemExit("sites-sources.json must pin exactly the six Working Tools repositories")
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir()
    if args.root_revision:
        if not re.fullmatch(r"[0-9a-f]{40}", args.root_revision):
            raise SystemExit("Root revision must be an exact commit SHA")
        pins["sources"]["compass-suite"]["sha"] = args.root_revision
        pins["sources"]["compass-suite"]["checkout"] = "."
    copied = []
    excluded = []
    routes = []
    for repo in REPOS:
        source = pins["sources"][repo]
        checkout = (
            (args.sources_dir / repo).resolve()
            if args.sources_dir and repo != "compass-suite"
            else (ROOT / source["checkout"]).resolve()
        )
        if not (checkout / ".git").exists():
            raise SystemExit(f"Missing Git checkout for {repo}: {checkout}")
        sha = source["sha"]
        if not re.fullmatch(r"[0-9a-f]{40}", sha):
            raise SystemExit(f"Invalid full commit SHA for {repo}")
        repository = SOURCE_REPOSITORIES.get(repo, repo)
        remote = git(checkout, "remote", "get-url", "origin").decode().strip()
        if remote not in (
            f"https://github.com/JonathanKHobson/{repository}.git",
            f"https://github.com/JonathanKHobson/{repository}",
            f"git@github.com:JonathanKHobson/{repository}.git",
        ):
            raise SystemExit(f"Unexpected source remote for {repository}: {remote}")
        git(checkout, "cat-file", "-e", f"{sha}^{{commit}}")
        names = git(checkout, "ls-tree", "-r", "--name-only", sha).decode().splitlines()
        for name in names:
            path = PurePosixPath(name)
            if name in EXCLUDED_RUNTIME_FILES or name.startswith(IGNORED_PREFIXES) or path.suffix.lower() not in RUNTIME_SUFFIXES:
                excluded.append(f"{repo}:{name}")
                continue
            blob = git(checkout, "show", f"{sha}:{name}")
            if path.suffix.lower() in TEXT_SUFFIXES:
                blob = rewrite(blob.decode("utf-8"), repo, name, args.site_origin).encode("utf-8")
            relative = destination(repo, name)
            if path.suffix.lower() == ".html" and relative.split("/", 1)[0] in LEGACY_ROUTES:
                blob = legacy_redirect()
            target = OUTPUT / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(blob)
            copied.append({"source": f"{repository}@{sha}:{name}", "output": relative, "sha256": hashlib.sha256(blob).hexdigest(), "bytes": len(blob)})
            if path.suffix.lower() == ".html":
                routes.append("/" + relative.removesuffix("index.html"))
    # Preserve Humanizer downloads from the same exact maintained source commit.
    root_sha = pins["sources"]["compass-suite"]["sha"]
    root_checkout = (ROOT / pins["sources"]["compass-suite"]["checkout"]).resolve()
    extra_prefix = "site-sources/humanizer/"
    extra_names = git(root_checkout, "ls-tree", "-r", "--name-only", root_sha, "--", extra_prefix).decode().splitlines()
    for name in extra_names:
        path = PurePosixPath(name)
        if path.suffix == ".md": continue
        relative = "humanizer/" + name.removeprefix(extra_prefix)
        target = OUTPUT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        blob = git(root_checkout, "show", f"{root_sha}:{name}")
        if path.suffix == ".html": blob = legacy_redirect()
        target.write_bytes(blob)
        copied.append({"source": f"working-tools-site@{root_sha}:{name}", "output": relative, "sha256": hashlib.sha256(blob).hexdigest(), "bytes": len(blob)})
        if path.suffix == ".html": routes.append("/" + relative.removesuffix("index.html"))
    manifest = {
        "schema_version": "working-tools.site-build.v1",
        "site_origin": args.site_origin,
        "site_project_id": args.site_project_id,
        "source_revisions": {repo: pins["sources"][repo]["sha"] for repo in REPOS},
        "source_repositories": {repo: SOURCE_REPOSITORIES.get(repo, repo) for repo in REPOS},
        "routes": sorted(routes),
        "files": sorted(copied, key=lambda item: item["output"]),
        "excluded_source_files": sorted(excluded),
    }
    (OUTPUT / "build-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Built {len(copied)} runtime files and {len(routes)} HTML routes in {OUTPUT}")
    print("Build manifest:", OUTPUT / "build-manifest.json")


if __name__ == "__main__":
    main()
