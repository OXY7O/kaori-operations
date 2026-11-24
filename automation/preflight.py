"""Fail-closed source/operation preflight for the bounded local host-facts pilot.

Does NOT execute Ansible or accept arbitrary remote inventories/commands.
Runtime authorization and signed inventory scope belong to KAORI #4799.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = "linux.host_facts.v1"
PLAYBOOK = "ansible/playbooks/linux_host_facts.yml"
DEMO_INVENTORY = "ansible/inventory/examples/localhost.ini"
SHA_PATTERN = re.compile(r"[0-9a-f]{40}\Z")
DENIED_MARKERS = ("ansible_become_password", "ansible_ssh_pass", "ansible_password", "private_key_file")


class PreflightDenied(ValueError):
    """An unqualified request cannot be used for Ansible execution."""


def _verified_child(root: Path, relative: str) -> Path:
    if not relative or Path(relative).is_absolute():
        raise PreflightDenied("Absolute or missing paths are not accepted")
    candidate = (root / relative).resolve(strict=True)
    if not candidate.is_relative_to(root.resolve(strict=True)) or not candidate.is_file():
        raise PreflightDenied("Path escapes the approved source checkout")
    return candidate


def validate_manifest(
    root: Path, *, operation: str, inventory: str, limit: str
) -> dict[str, str]:
    if operation != OPERATION_ID:
        raise PreflightDenied("Operation is not allowlisted for the pilot")
    if inventory != DEMO_INVENTORY or limit != "localhost":
        raise PreflightDenied("Only explicit localhost smoke inventory/limit is supported")
    manifest_path = _verified_child(root, "automation/operations.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1:
        raise PreflightDenied("Unrecognized automation manifest schema")
    operations = manifest.get("operations")
    if not isinstance(operations, dict) or set(operations) != {OPERATION_ID}:
        raise PreflightDenied("Unknown or extra operations are not admitted")
    entry = operations[OPERATION_ID]
    expected = {
        "playbook": PLAYBOOK,
        "mode": "read_only",
        "become": False,
        "allowed_inventory": DEMO_INVENTORY,
        "allowed_limit": "localhost",
    }
    if not isinstance(entry, dict) or entry != expected:
        raise PreflightDenied("Automation manifest deviates from the approved read-only contract")
    playbook = _verified_child(root, PLAYBOOK)
    inventory_path = _verified_child(root, DEMO_INVENTORY)
    body = playbook.read_text(encoding="utf-8")
    if not all(marker in body for marker in ("ansible.builtin.setup:", "become: false", "gather_facts: false")):
        raise PreflightDenied("Approved read-only facts shape is missing")
    # This is a narrow defense-in-depth check, never proof that arbitrary YAML is safe.
    if any(term in body.lower() for term in ("ansible.builtin.shell:", "ansible.builtin.command:", "ansible.builtin.raw:", "ansible.builtin.script:", "ansible.builtin.apt:", "ansible.builtin.dnf:", "ansible.builtin.yum:", "ansible.builtin.package:", "become: true")):
        raise PreflightDenied("Mutation or arbitrary command module is outside this pilot")
    if any(secret in inventory_path.read_text(encoding="utf-8").lower() for secret in DENIED_MARKERS):
        raise PreflightDenied("Credential material must not be in source inventory")
    return {"operation": operation, "playbook": PLAYBOOK, "inventory": inventory, "limit": limit}


def verify_source_revision(root: Path, revision: str) -> str:
    if not SHA_PATTERN.fullmatch(revision):
        raise PreflightDenied("Source revision must be a complete immutable Git SHA")
    try:
        head = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=5, check=True,
        ).stdout.strip()
        dirty = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all"],
            capture_output=True, text=True, timeout=5, check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        raise PreflightDenied("Cannot verify immutable Git checkout") from exc
    if head != revision or dirty:
        raise PreflightDenied("Checkout revision mismatch or uncommitted source changes")
    return head


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--operation", default=OPERATION_ID)
    parser.add_argument("--inventory", default=DEMO_INVENTORY)
    parser.add_argument("--limit", default="localhost")
    parser.add_argument("--revision", required=True)
    args = parser.parse_args()
    try:
        checked = validate_manifest(ROOT, operation=args.operation, inventory=args.inventory, limit=args.limit)
        checked["source_sha"] = verify_source_revision(ROOT, args.revision)
    except (PreflightDenied, OSError, json.JSONDecodeError) as exc:
        parser.exit(2, f"BLOCKED: {exc}\n")
    print(json.dumps(checked, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
