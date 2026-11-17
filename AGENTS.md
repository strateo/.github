# Repository guide

This public repository provides Strateo's GitHub organization profile.

- `profile/README.md` is the PT-BR default shown on the organization overview; `profile/README.en-US.md` is the English version.
- Keep language links absolute: GitHub renders the default file outside its repository context.
- Ground company claims and contact details in the public website at https://www.strateo.com.br/. List only public projects. Never disclose private products, clients, or operations.
- Keep the profile dependency-free. Proofread both languages and verify changed links.
- Run `git diff --check` and inspect the staged diff before committing.
- Use a task branch. Initial publication creates remote `main`; later publication needs user authorization.

## Public project automation

The user authorized automatic discovery of new public Strateo repositories, weekly on Sunday at 22:00 America/Sao_Paulo (Monday 01:00 UTC). The `Update public projects` workflow may also run manually or after updater/workflow changes land on `main`. As `github-actions[bot]`, it may commit and push only the two profile README files to `strateo/.github` remote `main`, replacing only the `PROJECTS` marker blocks.

- Discover all pages of public organization repositories. Exclude forks and the `.github` profile repository. Never include private repositories.
- Preserve curated bilingual descriptions for existing projects; use new repositories' public descriptions until translated.
- On API or validation errors, fail without changing the profile. A valid empty public-project list removes stale entries.
- Run `python -B -m unittest discover -s scripts -p 'test_*.py' -v` before publication.
- Run `python -B scripts/update_projects.py` to refresh using the existing authenticated `gh` CLI.
