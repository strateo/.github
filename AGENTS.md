# Repository guide

This public repository provides Strateo's GitHub organization profile.

- `profile/README.md` is the PT-BR default shown on the organization overview; `profile/README.en-US.md` is the English version.
- Keep language links absolute: GitHub renders the default file outside its repository context.
- Ground company claims and contact details in the public website at https://www.strateo.com.br/. List only public projects. Never disclose private products, clients, or operations.
- Keep the profile dependency-free. Proofread both languages and verify changed links.
- Run `git diff --check` and inspect the staged diff before committing.
- Use a task branch. Initial publication creates remote `main`; later publication needs user authorization.
