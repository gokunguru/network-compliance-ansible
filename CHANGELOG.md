# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- CHECK-013: IP source routing must be disabled.

## [1.0.0] - 2026-10-24

First stable release: offline and live audit of Cisco IOS devices, reporting, and closed-loop remediation.

### Added

**Audit**
- Data-driven compliance rules in `rules/cisco_ios.yml`, with severity and remediation per rule.
- 12 Cisco IOS checks: telnet on VTY, SSHv2, password encryption, enable secret, remote syslog, login banner, VTY idle timeout, VTY access-class, unused interfaces, NTP, HTTP server, default SNMP communities.
- Two rule engines: regex on the raw configuration, and structural checks on configuration parsed with `cisco.ios` resource modules (`state: parsed`).
- Severity-weighted compliance score per device and for the whole run.
- Configuration source switch: configuration files (offline) or `show running-config` over SSH (live devices).

**Reporting**
- Consolidated HTML report with per-device scores and findings, including the affected interfaces.
- Machine-readable JSON report, and a summary table published on every CI run.
- Per-device remediation plans (`reports/remediation/<device>.cfg`); fixes that need a human decision are flagged as manual.

**Remediation**
- `playbooks/remediate.yml`: config backup, fixes applied with `cisco.ios.ios_config` one device at a time, then re-audit. Refuses to run offline or without explicit confirmation.

**Engineering**
- `compliance_audit` role with documented defaults and Galaxy metadata.
- Python filter plugin for structural checks, covered by `pytest` unit tests.
- Rule regression tests: every rule needs passing and failing cases and a remediation.
- Molecule scenario against a golden configuration and a fully non-compliant configuration.
- Execution Environment definition (`ansible-builder`) and a workflow that builds it and runs the audit inside it.
- CI: `ansible-lint` (production profile), `ruff`, `pytest`, rule tests, Molecule, offline audit, `gitleaks`.
- GNS3 lab guide (`docs/lab.md`), lab inventory template and device bootstrap configurations.

[Unreleased]: https://github.com/gokunguru/network-compliance-ansible/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/gokunguru/network-compliance-ansible/releases/tag/v1.0.0
