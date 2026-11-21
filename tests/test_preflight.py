from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from automation.preflight import (
    DEMO_INVENTORY,
    OPERATION_ID,
    PLAYBOOK,
    PreflightDenied,
    ROOT,
    validate_manifest,
    verify_source_revision,
)


class PreflightTests(unittest.TestCase):
    def test_execution_environment_security_pins_are_exact(self) -> None:
        requirements = (
            (ROOT / "execution-environments/requirements.txt")
            .read_text(encoding="utf-8")
            .splitlines()
        )
        self.assertIn("ansible-core==2.19.15", requirements)
        self.assertNotIn("ansible-core==2.19.3", requirements)
        self.assertIn("ansible-runner==2.4.3", requirements)

    def test_local_read_only_manifest_accepted(self) -> None:
        result = validate_manifest(ROOT, operation=OPERATION_ID, inventory=DEMO_INVENTORY, limit="localhost")
        self.assertEqual(result["playbook"], PLAYBOOK)

    def test_unknown_operation_denied(self) -> None:
        with self.assertRaises(PreflightDenied):
            validate_manifest(ROOT, operation="linux.patch.v1", inventory=DEMO_INVENTORY, limit="localhost")

    def test_target_broadening_denied(self) -> None:
        for limit in ("all", "pilot", "*", "localhost,other"):
            with self.subTest(limit=limit), self.assertRaises(PreflightDenied):
                validate_manifest(ROOT, operation=OPERATION_ID, inventory=DEMO_INVENTORY, limit=limit)

    def test_inventory_path_traversal_denied(self) -> None:
        with self.assertRaises(PreflightDenied):
            validate_manifest(ROOT, operation=OPERATION_ID, inventory="../../hosts.ini", limit="localhost")

    def test_mutation_playbook_denied(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "automation").mkdir()
            (root / "ansible/playbooks").mkdir(parents=True)
            (root / "ansible/inventory/examples").mkdir(parents=True)
            for relative in ("automation/operations.json", DEMO_INVENTORY, PLAYBOOK):
                src = ROOT / relative
                target = root / relative
                target.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
            with (root / PLAYBOOK).open("a", encoding="utf-8") as fp:
                fp.write("\n    - ansible.builtin.shell: whoami\n")
            with self.assertRaises(PreflightDenied):
                validate_manifest(root, operation=OPERATION_ID, inventory=DEMO_INVENTORY, limit="localhost")

    def test_short_sha_denied_before_git(self) -> None:
        with self.assertRaises(PreflightDenied):
            verify_source_revision(ROOT, "main")

    @patch("automation.preflight.subprocess.run")
    def test_dirty_checkout_denied(self, run) -> None:
        run.side_effect = [
            type("Result", (), {"stdout": "a" * 40 + "\n"})(),
            type("Result", (), {"stdout": " M ansible/playbooks/linux_host_facts.yml\n"})(),
        ]
        with self.assertRaises(PreflightDenied):
            verify_source_revision(ROOT, "a" * 40)

    @patch("automation.preflight.subprocess.run")
    def test_exact_clean_sha_accepted(self, run) -> None:
        run.side_effect = [
            type("Result", (), {"stdout": "a" * 40 + "\n"})(),
            type("Result", (), {"stdout": ""})(),
        ]
        self.assertEqual(verify_source_revision(ROOT, "a" * 40), "a" * 40)


if __name__ == "__main__":
    unittest.main()
