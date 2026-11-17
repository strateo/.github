"""Update marked organization-profile sections from public GitHub repositories."""

from html import escape
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
START = "<!-- PROJECTS:START -->"
END = "<!-- PROJECTS:END -->"
FILES = {"profile/README.md": "pt", "profile/README.en-US.md": "en"}
DESCRIPTIONS = {
    "nfse": {
        "pt": "Cliente Python para emissão, consulta e cancelamento de NFS-e no Padrão Nacional. Projeto em estágio inicial de desenvolvimento; consulte os requisitos e limites no repositório.",
        "en": "A Python client for issuing, querying, and canceling Brazilian service invoices (NFS-e) under the national standard. Early-stage software; see the repository for requirements and limitations.",
    },
}


def fetch_repositories():
    result = subprocess.run(
        ["gh", "api", "--paginate", "--slurp",
         "orgs/strateo/repos?type=public&per_page=100"],
        capture_output=True, text=True, encoding="utf-8", check=False,
    )
    if result.returncode:
        raise RuntimeError("GitHub repository listing failed; check authentication and API limits.")
    pages = json.loads(result.stdout)
    if not isinstance(pages, list) or not pages or any(not isinstance(p, list) for p in pages):
        raise ValueError("Unexpected repository response; keeping the existing profile.")
    return [repo for page in pages for repo in page]


def public_projects(repositories):
    projects = {}
    for repo in repositories:
        if repo["private"] or repo.get("visibility", "public") != "public":
            continue
        if repo["owner"]["login"].lower() != "strateo":
            raise ValueError("Repository listing contains an unexpected owner.")
        name = repo["name"]
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", name):
            raise ValueError("Repository name is not safe for Markdown.")
        if name == ".github" or repo["fork"]:
            continue
        if name.lower() in projects:
            raise ValueError("Duplicate repository in paginated response.")
        projects[name.lower()] = (name, repo.get("description"))
    return [projects[key] for key in sorted(projects)]


def render(projects, language):
    lines = []
    for name, description in projects:
        description = DESCRIPTIONS.get(name.lower(), {}).get(language, description)
        if not description:
            description = "Sem descrição pública." if language == "pt" else "No public description."
        description = " ".join(description.split())
        if len(description) > 240:
            description = description[:237].rsplit(" ", 1)[0] + "…"
        description = re.sub(r"([\\`*_[\]{}()!|])", r"\\\1", escape(description))
        label = name.replace("_", r"\_")
        lines.append(f"- **[{label}](https://github.com/strateo/{name})** — {description}")
    if not lines:
        return "Nenhum projeto público disponível no momento." if language == "pt" else "No public projects available yet."
    return "\n".join(lines)


def replace_section(text, content):
    if text.count(START) != 1 or text.count(END) != 1:
        raise ValueError("Expected exactly one project marker pair.")
    before, rest = text.split(START)
    if END in before:
        raise ValueError("Project markers are out of order.")
    _, after = rest.split(END)
    return before + START + "\n" + content + "\n" + END + after


def update(root=ROOT, fetch=fetch_repositories):
    projects = public_projects(fetch())
    planned = []
    for name, language in FILES.items():
        path = root / name
        original = path.read_text(encoding="utf-8")
        replacement = replace_section(original, render(projects, language))
        if original != replacement:
            planned.append((path, replacement))
    for path, content in planned:
        path.write_text(content, encoding="utf-8", newline="\n")
    return len(planned)


if __name__ == "__main__":
    try:
        print(f"Updated {update()} profile file(s).")
    except (OSError, ValueError, KeyError, TypeError, RuntimeError) as error:
        raise SystemExit(f"Project refresh failed: {error}") from None
