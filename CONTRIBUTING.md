# Contributing to KAORI Operations

We welcome issue reports and review proposals while the project's public contribution and licensing policy is finalized. **Visibility is not a license**: do not assume or represent that KAORI or this repository are under an OSI-approved license until OXY7O publishes the approved license.

## Before proposing a change

1. Open or link an issue describing one bounded outcome and its owning automation domain. Reuse accepted KAORI standards instead of introducing a parallel execution framework.
2. Open a descriptive, issue-linked work branch; never commit to `main` directly.
3. Use small reviewed pull requests with explicit dependencies, security impact, tested SHA, negative tests and reproducible evidence. No simulated provider output may be presented as real UAT evidence.
4. Keep the automation definition reusable and safe for public code review; use **synthetic inventory/examples only**.
5. Avoid submitting confidential, employer-specific or third-party proprietary material; confirm you have rights to propose any contribution. A separate contribution-license decision may be required before acceptance.

## Quality

For read-only Ansible changes, run the repository's existing `Read-only Automation Source QA` workflow, local Python tests, playbook syntax check and a disposable localhost smoke as applicable. For future mutations, require a separate authority/approval and real provider UAT; CI pass cannot replace it.

## Safety boundary

Git defines source. KAORI governs target/approval, executes through the proper worker and stores auditable evidence. No arbitrary remote inventory, credentials or operator environment state should be introduced into the public repository.

Sensitive vulnerability findings follow [SECURITY.md](SECURITY.md), not public issues or PRs.
