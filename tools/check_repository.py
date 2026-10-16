"""Validate documentation and GitHub configuration; never access audio devices."""

from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

import yaml


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "README.md", "LICENSE", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md",
    "docs/architecture.md", "docs/decisions/0001-initial-architecture.md",
    "docs/development.md", "docs/measurement.md", "docs/platforms.md",
    "docs/roadmap.md", "docs/testing.md", "docs/releases.md", "docs/references.md",
    ".github/workflows/repository-checks.yml",
    ".github/pull_request_template.md", ".github/ISSUE_TEMPLATE/config.yml",
    ".github/ISSUE_TEMPLATE/bug_report.yml",
    ".github/ISSUE_TEMPLATE/feature_request.yml",
    ".github/ISSUE_TEMPLATE/hardware_report.yml",
)
LINK = re.compile(r"\[[^\]]*\]\(([^\s)]+)(?:\s+\"[^\"]*\")?\)")


def main():
    errors = []
    for name in REQUIRED:
        if not (ROOT / name).is_file():
            errors.append(f"Missing required file: {name}")

    files = [ROOT / "LICENSE", ROOT / "requirements-dev.txt"]
    files += list(ROOT.glob("*.md"))
    files += list((ROOT / "docs").rglob("*.md"))
    files += [p for p in (ROOT / ".github").rglob("*") if p.suffix in {".md", ".yml", ".yaml"}]
    for path in files:
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeError as exc:
            errors.append(f"{relative}: invalid UTF-8: {exc}")
            continue
        if not content.endswith("\n"):
            errors.append(f"{relative}: missing final newline")
        for line_number, line in enumerate(content.splitlines(), 1):
            if line.rstrip() != line:
                errors.append(f"{relative}:{line_number}: trailing whitespace")
        if path.suffix == ".md":
            for match in LINK.finditer(content):
                target = match.group(1).strip("<>")
                parsed = urlsplit(target)
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                destination = (path.parent / unquote(parsed.path)).resolve()
                if not destination.is_relative_to(ROOT) or not destination.exists():
                    errors.append(f"{relative}: missing or external local link: {target}")
        elif path.suffix in {".yml", ".yaml"}:
            try:
                # BaseLoader preserves 'on' as a string (GitHub uses YAML 1.2).
                data = yaml.load(content, Loader=yaml.BaseLoader)
                if not isinstance(data, dict):
                    raise ValueError("expected a YAML mapping")
                if path.parent.name == "workflows":
                    if not all(key in data for key in ("name", "on", "jobs", "permissions")):
                        raise ValueError("workflow lacks essential keys")
                    if data["permissions"] != {"contents": "read"}:
                        raise ValueError("repository workflow should have read-only permissions")
                elif path.name != "config.yml":
                    if not all(key in data for key in ("name", "description", "body")):
                        raise ValueError("issue form lacks essential keys")
                    identifiers = [item["id"] for item in data["body"] if "id" in item]
                    if len(identifiers) != len(set(identifiers)):
                        raise ValueError("duplicate issue field IDs")
            except (yaml.YAMLError, ValueError, TypeError) as exc:
                errors.append(f"{relative}: {exc}")

    if errors:
        print("Repository validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Repository checks passed ({len(files)} documentation/configuration files).")
    print("No application, audio, external URL, or Markdown anchor checks were run.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
