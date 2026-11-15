from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from automation.kubespray_profile import ProfileDenied, qualify_static_profile

ROOT = Path(__file__).resolve().parents[1]
PROFILE = Path("kubernetes/self-managed/profiles/kubespray-v2.32.0-pilot.json")


class KubesprayProfileTests(unittest.TestCase):
    def test_upstream_profile_is_exact_and_non_executable(self) -> None:
        decision = qualify_static_profile(ROOT)
        self.assertEqual(decision["status"], "requires_provider_evidence")
        self.assertEqual(decision["execution_enabled"], "false")
        self.assertEqual(decision["upstream_sha"], "9751ea6f63244e433a7a6263d9ecf381e57bb8e9")

    def test_profile_does_not_contain_target_or_secrets(self) -> None:
        contents = (ROOT / PROFILE).read_text(encoding="utf-8")
        for banned in ("ssh_private_key", "kubeconfig", "ansible_password", "192.168.", "10.0.0."):
            self.assertNotIn(banned, contents)
        self.assertNotIn("playbook", json.loads(contents))

    def test_mutation_toggle_or_moving_release_is_denied(self) -> None:
        original = json.loads((ROOT / PROFILE).read_text(encoding="utf-8"))
        variants = [
            {"execution_enabled": True},
            {"mutation_authorized": True},
            {"upstream": {**original["upstream"], "release": "master"}},
            {"pilot": {**original["pilot"], "management": "aws_eks"}},
        ]
        for alteration in variants:
            with self.subTest(alteration=tuple(alteration)):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    dest = root / PROFILE
                    dest.parent.mkdir(parents=True)
                    dest.write_text(json.dumps({**original, **alteration}), encoding="utf-8")
                    with self.assertRaises(ProfileDenied):
                        qualify_static_profile(root)


if __name__ == "__main__":
    unittest.main()
