# Self-managed Kubernetes — versioned support profile

Authority: OXY7O/KAORI#4800 / OXY7O/kaori-operations#5.

First profile: `profiles/kubespray-v2.32.0-pilot.json` records official Kubespray tag v2.32.0, resolved Git commit `9751ea6f63244e433a7a6263d9ecf381e57bb8e9`, Kubernetes 1.36 default minor, Ansible 12.3.0 and ansible-core >=2.19,<2.20 compatibility for an intentionally narrow disposable, **non-HA, non-production existing-host** pilot.

This profile is not a runnable playbook, private inventory, approved Plan, credential reference or approved execution environment digest. `execution_enabled=false` and `mutation_authorized=false` are mandatory. It deliberately cannot execute `cluster.yml` or any other upstream playbook. Upstream requirements and target OS support must be independently qualified in a separately approved Kubespray execution environment.

```bash
python3 -m unittest discover -s tests -v
python3 - <<'PY'
from pathlib import Path
from automation.kubespray_profile import qualify_static_profile
print(qualify_static_profile(Path.cwd()))
PY
```

When KAORI implements a real provider plan, it must pin this repository's approved commit SHA and the upstream Kubespray commit, validate a private authorized host inventory, resolve credentials outside public Git, collect real provider preflight evidence, require RBAC and independent approval, and prove Kubernetes health by API read-back. No Kubernetes creation, patching, upgrade or certificate rotation is authorized by this file.
