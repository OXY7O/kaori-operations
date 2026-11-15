# Read-only host facts pilot — operator UAT

Authority: OXY7O/kaori-operations#1 / OXY7O/KAORI#4799. **Local isolated test only**; not production automation admission.

## Prerequisites

- Clone a reviewed branch/commit of this **public** source repository into a disposable working directory.
- Python 3.12 and isolated environment with pinned \`execution-environments/requirements.txt\`; do not use shared root Python/pip or inject cloud credentials.
- The test target is **localhost** using \`ansible_connection=local\`. No remote SSH, privilege escalation, patching, provisioning or certificate changes.
- Never place credentials, private network details, secret inventory, dynamic tokens or real kubeconfig inside this repository.

## Test actions

1. Run \`python3 -m unittest discover -s tests -v\`; record test count/result.
2. Record exact \`git rev-parse HEAD\` and \`git status --porcelain\` (must be empty).
3. Run \`python3 -m automation.preflight --revision "$(git rev-parse HEAD)" --inventory ansible/inventory/examples/localhost.ini --limit localhost\`. Expect valid bounded JSON with exact SHA and operation.
4. Run \`ansible-playbook --version\` and \`ansible-playbook -i ansible/inventory/examples/localhost.ini --syntax-check ansible/playbooks/linux_host_facts.yml\`.
5. With explicit authorization for the **local** disposable machine, run \`ansible-playbook -i ansible/inventory/examples/localhost.ini --limit localhost ansible/playbooks/linux_host_facts.yml\`. Expect \`ok=1\`, \`changed=0\`, \`failed=0\`; inspect filtered OS/kernel fact output.
6. Negative: change \`--limit localhost\` to \`--limit all\` in the preflight, expect \`BLOCKED\` and exit 2. Change \`--revision\` to a 40-character zero SHA, expect \`BLOCKED\`. No playbook execution should occur.

## Evidence / acceptance

Record revision, Python/Ansible versions, commands, terminal outputs with sensitive values sanitized, and explicit reviewer decision. A PASS in this local test **does not** prove a live KAORI Celery worker, remote SSH trust, provider postcondition or real self-managed Kubernetes readiness. Those require an independently authorized KAORI #4799/#4800/#4801 UAT.

No uncordon/drain/upgrade/patch/cluster creation operations are present. Stop on unexpected target or mutation behavior.
