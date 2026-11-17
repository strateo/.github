from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

from update_projects import (
    START, END, FILES, fetch_repositories, public_projects, render, replace_section, update,
)


def repo(name, private=False, fork=False, owner="strateo", description="A project."):
    return {"name": name, "private": private, "fork": fork,
            "owner": {"login": owner}, "description": description}


class ProjectsTest(unittest.TestCase):
    def test_public_owned_projects_only(self):
        projects = public_projects([repo("new"), repo("nfse"), repo(".github"),
                                    repo("secret", private=True), repo("fork", fork=True)])
        self.assertEqual([name for name, _ in projects], ["new", "nfse"])
        with self.assertRaises(ValueError):
            public_projects([repo("wrong", owner="other")])
        with self.assertRaises(ValueError):
            public_projects([repo("same"), repo("same")])

    def test_pagination_and_api_failure(self):
        result = SimpleNamespace(returncode=0, stdout='[[{"name":"one"}],[{"name":"two"}]]')
        with patch("update_projects.subprocess.run", return_value=result) as run:
            self.assertEqual(len(fetch_repositories()), 2)
            self.assertIn("--paginate", run.call_args.args[0])
        with patch("update_projects.subprocess.run", return_value=SimpleNamespace(returncode=1)):
            with self.assertRaises(RuntimeError):
                fetch_repositories()

    def test_localization_and_description_safety(self):
        self.assertIn("emissão", render([("nfse", "unused")], "pt"))
        self.assertIn("issuing", render([("nfse", "unused")], "en"))
        output = render([("new", "[link](url)\n<script>")], "en")
        self.assertIn(r"\[link\]\(url\) &lt;script&gt;", output)
        self.assertIn("No public description.", render([("new", None)], "en"))

    def test_valid_empty_response_removes_stale_projects(self):
        self.assertIn("Nenhum projeto", render([], "pt"))
        self.assertIn("No public projects", render([], "en"))

    def test_markers_and_unrelated_content(self):
        original = f"intro\n{START}\nold\n{END}\nfooter\n"
        self.assertEqual(replace_section(original, "new"),
                         f"intro\n{START}\nnew\n{END}\nfooter\n")
        for invalid in ["no markers", f"{END}{START}", f"{START}{START}{END}"]:
            with self.assertRaises(ValueError):
                replace_section(invalid, "new")

    def test_new_repo_discovery_idempotency_and_failure_preservation(self):
        with tempfile.TemporaryDirectory(prefix="strateo-projects-") as scratch:
            root = Path(scratch)
            original = f"intro\n{START}\nold\n{END}\nfooter\n"
            for name in FILES:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(original, encoding="utf-8")
            fetch = lambda: [repo("nfse"), repo("brand-new")]
            self.assertEqual(update(root, fetch), 2)
            self.assertIn("brand-new", (root / "profile/README.md").read_text(encoding="utf-8"))
            self.assertEqual(update(root, fetch), 0)
            (root / "profile/README.en-US.md").write_text("no markers", encoding="utf-8")
            before = (root / "profile/README.md").read_text(encoding="utf-8")
            with self.assertRaises(ValueError):
                update(root, lambda: [repo("another")])
            self.assertEqual((root / "profile/README.md").read_text(encoding="utf-8"), before)
            with self.assertRaises(RuntimeError):
                update(root, lambda: (_ for _ in ()).throw(RuntimeError("API failure")))
            self.assertEqual((root / "profile/README.md").read_text(encoding="utf-8"), before)


if __name__ == "__main__":
    unittest.main()
