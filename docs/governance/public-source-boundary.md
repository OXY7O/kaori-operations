# Public automation source and private operational context

Authority: OXY7O/KAORI#556, #4796 and OXY7O/kaori-operations#3.

## Architectural decision

Keep `OXY7O/kaori-operations` **public** as a reusable community-facing *source* repository, not as an infrastructure configuration database. Publish playbooks/roles/collections, pinned dependencies and Execution Environment build definitions, tests, synthetic example inventories and non-sensitive runbooks.

**Environment-specific data is never held by the public source repo.** Actual secrets, real inventory and host identity are retrieved from an approved protected authority at the time of a separately authorized run.

```text
Public KAORI Operations repository
  reviewed commit + pinned playbook/role/collection + tests
               |
               | immutable source reference, no secrets
               v
KAORI governance / Jobs & Executions
  scoped RBAC, target identity, risk/approval, plan, audit
               |
               | permitted job with credential references
               v
Isolated Ansible worker + pinned Execution Environment
               |
               | trusted SSH / bounded playbook operation
               v
Explicitly authorized self-managed infrastructure
               |
               | independent authoritative read-back
               v
Committed KAORI evidence / verification / correlation
```

## Public/source allowlist

| Public and reviewable | Must remain private / external authority |
|---|---|
| Versioned playbooks, roles and collection dependency declarations | Real server inventories, private IPs, DNS, tenant identities |
| Generic Kubernetes self-managed provisioning design | Real cluster topology, kubeconfig, cluster certificate chain |
| Read-only example inventory targeting localhost | SSH keys, become passwords, Vault tokens, cloud credentials |
| Build definitions and tests for pinned EE | Real runtime execution artifacts, redacted or full access logs |
| Generic operating and recovery guidance | Employer-specific or confidential operating procedures |

A public repo is not made safe by `.gitignore` alone. Require reviewer checks, scanning/push protection, non-secret inputs, immutable provenance, least privilege and explicit postcondition verification.

## Licensing checkpoint

KAORI's currently committed `LICENSE` is the proprietary **KAORI INTERNAL USE LICENSE**, not an OSI open-source license. This source repository has **no OXY7O-approved LICENSE file yet**. Repository visibility by itself is **not a license grant**. The operator/rights holder must decide whether this repo and KAORI app use Apache-2.0, another compatible license, dual licensing or continue under restrictive terms. Until that decision, do not copy KAORI proprietary application code into the public automation repository or promise external reuse rights.

## Operator settings (manual GitHub UI)

The integration connector cannot confirm/apply every repository setting. A maintainer must check `Settings → Rules/Branches` for protected `main`, PR review and required source QA checks; `Settings → Code security and analysis` for Dependabot alerts, dependency scanning, secret scanning and push protection; enable private vulnerability reporting; and restrict GitHub Actions workflow permission to read by default. Configure appropriate Code Owner enforcement and check for accidental environment-secret exposure in existing Git history.

Any infrastructure mutation, including Kubernetes cluster bootstrap, requires its own approved Plan, role/scope, change window, exact source/EE pins, safe retries and independent postcondition UAT. Do not interpret source PR merge as an operator Run authorization.
