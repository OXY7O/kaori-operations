# Security Policy

## Scope

This repository contains automation **source**, not production inventory, identity or credentials. A playbook change may have operational effects when adopted into KAORI, so security reports and execution review are required even for read-only features.

## Private reporting

**Do not file a public GitHub issue for an exploitable weakness, exposed credential, unprotected deployment topology or sensitive proof-of-concept.** Use GitHub's **Report a vulnerability** / Private Vulnerability Reporting capability for this repository **once the repository administrator has enabled it**. If that option is unavailable, contact OXY7O maintainers via a verified private channel rather than posting the details publicly. No security-reporting email or SLA is asserted here.

If secret exposure is suspected: notify maintainers privately, revoke or rotate the affected credential through its source authority, review audit/access logs, and then use approved history-remediation procedures. Deleting the file alone does not remove it from Git history.

## Security review expectations

- No real inventory, kubeconfigs, SSH keys, passwords, Vault material, cloud tokens, private DNS details or infrastructure access paths.
- No generic shell/run endpoint, implicit privilege escalation, plaintext credential options or unaudited external downloads.
- Review Git source SHA, dependencies, Execution Environment digest, supported platform versions, safe target selection, negative authorization tests and post-change read-back.
- Patching, provisioning, upgrade, PKI changes and control-plane mutation require separately approved governance and provider-specific UAT.

The repository contains **no authority to operate anyone's infrastructure**. Experimental code and example inventory may be used only with explicit authorization to the target.
