from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

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

    def test_remote_candidate_does_not_broaden_local_operation(self) -> None:
        with self.assertRaises(PreflightDenied):
            validate_manifest(
                ROOT, operation="linux.remote_preflight.v1",
                inventory=DEMO_INVENTORY, limit="kaori_remote_pilot",
            )

    def test_remote_candidate_manifest_and_playbook_are_review_only(self) -> None:
        candidate = json.loads(
            (ROOT / "automation/remote_preflight_candidate.json").read_text(encoding="utf-8")
        )
        self.assertEqual(candidate, {
            "schema_version": 1,
            "kind": "remote_read_only_source_candidate",
            "operation": "linux.remote_preflight.v1",
            "playbook": "ansible/playbooks/linux_remote_preflight.yml",
            "mode": "read_only",
            "become": False,
            "execution_enabled": False,
            "mutation_authorized": False,
            "inventory": "canonical_kaori_worker_generated",
            "limit": "kaori_remote_pilot",
            "target": {
                "environment": "nonproduction", "allocation": "existing_linux_hosts",
                "control_plane_count": 1, "worker_count": 2,
            },
            "facts_contract": "linux.remote_preflight.facts.v1",
        })
        play = yaml.safe_load((ROOT / candidate["playbook"]).read_text(encoding="utf-8"))
        self.assertEqual(len(play), 1)
        self.assertEqual(set(play[0]), {
            "name", "hosts", "gather_facts", "become", "strategy", "serial",
            "any_errors_fatal", "tasks",
        })
        self.assertEqual(play[0]["hosts"], "kaori_remote_pilot")
        self.assertIs(play[0]["become"], False)
        self.assertIs(play[0]["gather_facts"], False)
        self.assertEqual(play[0]["strategy"], "linear")
        self.assertEqual(play[0]["serial"], 1)
        self.assertIs(play[0]["any_errors_fatal"], True)
        tasks = play[0]["tasks"]
        self.assertEqual(len(tasks), 1)
        self.assertEqual(set(tasks[0]), {"name", "ansible.builtin.setup"})
        setup = tasks[0]["ansible.builtin.setup"]
        self.assertEqual(set(setup), {"gather_subset", "filter"})
        self.assertEqual(set(setup["gather_subset"]), {
            "!all", "!min", "distribution", "kernel", "hardware", "network",
            "date_time", "user", "pkg_mgr", "python",
        })
        self.assertEqual(set(setup["filter"]), {
            "ansible_distribution", "ansible_distribution_version",
            "ansible_distribution_major_version", "ansible_os_family", "ansible_kernel",
            "ansible_architecture", "ansible_pkg_mgr", "ansible_processor_vcpus",
            "ansible_memtotal_mb", "ansible_mounts", "ansible_default_ipv4",
            "ansible_all_ipv4_addresses", "ansible_interfaces", "ansible_date_time",
            "ansible_effective_user_id", "ansible_python_version",
        })

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
