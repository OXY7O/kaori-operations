# KAORI Operations

Public source repository for reusable, reviewable operational automation associated with the KAORI control plane.

**Status:** Initial community/security baseline. Being publicly visible does **not** by itself grant an open-source license. A license for this repository has **not yet been selected** by OXY7O. The KAORI application currently has a separate **KAORI INTERNAL USE LICENSE**; no redistribution or reuse rights are implied by this README.

## Public source, private environment

Operational automation definitions, reusable Ansible roles/playbooks, example data, tests and generic runbooks belong here. Actual server inventories, internal addressing/topology, identities, secrets, kubeconfig, access controls, runtime artifacts and host-specific confidential runbooks do **not**.

Git defines the reviewed source. KAORI authorizes and orchestrates each operation. Ansible executes against explicitly approved infrastructure. Independent provider read-back and committed evidence prove the result.

Read [public-source boundary](docs/governance/public-source-boundary.md), [contribution rules](CONTRIBUTING.md) and [security policy](SECURITY.md). Until a rights-holder-approved license exists, contributions must not be assumed to be redistributable.

## Review and delivery

All functional changes require an issue, an issue-scoped work branch, review, reproducible tests, explicit scope, security assessment and a pull request. No push directly to `main`; the source repo never grants KAORI permission to mutate infrastructure on its own.

Initial read-only Linux facts source is under [issue #1](https://github.com/OXY7O/kaori-operations/issues/1); community-security baseline is under [issue #3](https://github.com/OXY7O/kaori-operations/issues/3).
