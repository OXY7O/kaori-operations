# KAORI Operations

Git-defined, reviewable **operational automation source** for KAORI. The KAORI application/control plane lives in [OXY7O/KAORI](https://github.com/OXY7O/KAORI). Ansible executes; KAORI orchestrates; Git defines; evidence proves.

> This repository is currently **public**. Never commit real host inventories, credentials, private IP allocations, SSH keys, vault tokens, Kubernetes kubeconfigs, cluster CA material, execution artifacts or privileged internal runbooks.

## First capability: Linux host discovery (read-only)

- Approved operation ID: `linux.host_facts.v1`
- Playbook: `ansible/playbooks/linux_host_facts.yml`
- Test inventory: `ansible/inventory/examples/localhost.ini` (local machine only)
- Source verification: `python3 -m automation.preflight`
- No cluster provisioning, patching, upgrades, unattended remote SSH, or mutation paths are included yet.

The versioned manifest explicitly allowlists the playbook; external callers must not interpret this as a generic YAML executor. Ansible playbook content and Git SHA are reviewed independently. KAORI execution through Celery/ansible-runner is tracked by OXY7O/KAORI#4799 and is **not claimed operational** by this repository alone.

## Operator/developer smoke

Use Python >=3.12 and the pinned Python package dependencies in `execution-environments/requirements.txt` inside an isolated test environment. Run commands from the repository root after checking out an exact commit SHA.

```bash
python3 -m unittest discover -s tests -v
python3 -m automation.preflight --revision "$(git rev-parse HEAD)" --inventory ansible/inventory/examples/localhost.ini --limit localhost
ansible-playbook -i ansible/inventory/examples/localhost.ini --syntax-check ansible/playbooks/linux_host_facts.yml
ansible-playbook -i ansible/inventory/examples/localhost.ini --limit localhost ansible/playbooks/linux_host_facts.yml
```

The final command collects a small, explicitly selected set of **local machine** facts; execute only on a developer-owned UAT host. Do not substitute a production inventory for the example without a separately authorized KAORI Run and safe SSH/credential boundary.

See `runbooks/host-discovery-uat.md` for safety, expected outcomes and evidence. All real-provider/worker UAT is pending.


## Remote preflight source candidate (review only)

Issue #9 / OXY7O/KAORI#5186 introduces `automation/remote_preflight_candidate.json` and
`ansible/playbooks/linux_remote_preflight.yml`. These are **disabled source candidates**,
not an admitted executable operation. The accepted localhost operation and static
Kubespray profile are unchanged. The remote candidate expects a future KAORI-generated
exact non-production pilot group (one control plane, two workers); this public
repository contains no remote inventory or material. The only task is bounded
Ansible setup fact collection, without become or arbitrary commands.

OS, CPU, memory, filesystem, interface, effective identity and clock observations
are not proof of SSH trust, privilege escalation capability, synchronized clock,
DNS, required port reachability, topology or full provisioning readiness.
Worker-side normalization must discard raw events and reject missing/invalid
observations. Existing QA runs the localhost smoke only and checks the candidate
syntax without executing it. Independent source review, immutable executable
source/EE admission, exact approved target/credential/trust, and operator-authorized
remote UAT are required in KAORI before any execution. Do not repin the application
or run this candidate directly on remote hosts. No mutation authority is added.
