"""Read-only qualification of a version-pinned public Kubespray pilot profile.

This module never constructs an inventory, accepts SSH material or invokes Ansible.
A valid profile still requires authoritative provider evidence and Human Approval.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_PROFILE = "kubernetes/self-managed/profiles/kubespray-v2.32.0-pilot.json"


class ProfileDenied(ValueError):
    """Unapproved or mutating profile data cannot be treated as executable."""


def _expected_profile() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "kind": "self_managed_kubernetes_compatibility_profile",
        "profile_key": "kubespray-self-managed-nonprod-pilot-v1",
        "execution_enabled": False,
        "mutation_authorized": False,
        "upstream": {
            "repository": "kubernetes-sigs/kubespray",
            "release": "v2.32.0",
            "commit": "9751ea6f63244e433a7a6263d9ecf381e57bb8e9",
            "kubernetes_default_minor": "1.36",
            "ansible_distribution": "12.3.0",
            "ansible_core_requirement": ">=2.19.0,<2.20.0",
        },
        "pilot": {
            "management": "self_managed",
            "environment": "nonproduction",
            "host_allocation": "existing_vm_or_bare_metal",
            "control_plane_count": 1,
            "worker_count": 2,
            "high_availability": False,
            "supported_os": [
                {"distribution": "OracleLinux", "release": "9"},
                {"distribution": "Ubuntu", "release": "24.04"},
            ],
            "inventory": "runtime_governed_not_stored_in_public_git",
        },
        "readiness": {
            "result_when_static_valid": "requires_provider_evidence",
            "required_provider_gates": [
                "asset_identity",
                "ssh_host_key_and_reachability",
                "host_os_compatibility",
                "dns_time_and_ports",
                "cidr_overlap_readback",
                "capacity_and_backup_recovery_owner",
                "source_and_execution_environment_digest",
                "rbac_risk_approval_window",
            ],
        },
    }


def qualify_static_profile(root: Path) -> dict[str, str]:
    """Fail closed on unreviewed profile content without exposing raw data."""
    root = root.resolve(strict=True)
    path = (root / _PROFILE).resolve(strict=True)
    if not path.is_file() or not path.is_relative_to(root):
        raise ProfileDenied("Profile file must be inside approved Git checkout")
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        raise ProfileDenied("Invalid Kubernetes profile document") from exc
    if raw != _expected_profile():
        raise ProfileDenied("Profile is not the approved non-executable upstream support matrix")
    return {
        "profile_key": raw["profile_key"],
        "upstream_sha": raw["upstream"]["commit"],
        "status": "requires_provider_evidence",
        "execution_enabled": "false",
    }
