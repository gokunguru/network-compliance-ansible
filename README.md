# network-compliance-ansible

![CI](https://github.com/gokunguru/network-compliance-ansible/actions/workflows/ci.yml/badge.svg)
![Ansible](https://img.shields.io/badge/ansible--core-2.16%2B-EE0000?logo=ansible)
![License](https://img.shields.io/badge/license-MIT-blue)

Network compliance audit framework built with Ansible. It checks network device configurations against a set of security rules and produces a consolidated HTML report.

![Compliance report](docs/report-example.png)

## Features

- **Data-driven rules**: compliance checks are defined in YAML, not hard-coded in tasks. Adding a check means adding four lines of YAML.
- **Full audit, then verdict**: every check runs on every device; the play only fails at the end if a device is non-compliant.
- **Consolidated HTML report**: one report for all devices, with per-device scores and check details.
- **Remediation plans**: for every non-compliant device, a ready-to-review IOS command file (`reports/remediation/<device>.cfg`) that fixes each finding. Site-specific values (syslog server, management network) come from the inventory; fixes that need a human decision, like secrets, are flagged as manual. Nothing is ever pushed automatically.
- **JSON export**: the same results as machine-readable JSON, ready for a SIEM, a GRC tool or a CI gate. The CI publishes a summary table on every run.
- **Weighted scoring**: each rule has a severity (high / medium / low); the compliance score weights findings accordingly, so a single critical gap costs more than several minor ones.
- **Two rule engines**: simple rules match the raw config with a regex; structural rules (`type: parsed`) parse the config with `cisco.ios` resource modules (`state: parsed`) and reason on structured data, e.g. *every interface with no description, no switchport config and no IP must be shut down*.
- **Offline mode**: audits configuration files without any live device, which makes the whole project testable in CI.
- **Quality gates**: `ansible-lint` (production profile) and `gitleaks` secret scanning on every push.

## How it works

```
rules/cisco_ios.yml ──┐
                      ├──► role: compliance_audit ──► console summary
samples/configs/*.cfg ┘                            └► reports/compliance-report.html
```

A rule looks like this:

```yaml
- id: CHECK-001
  title: Telnet must be disabled on VTY lines
  pattern: 'transport input (all|.*telnet)'
  expect: absent   # present = must be found, absent = must not be found
```

## Current checks (Cisco IOS)

| ID | Check |
|---|---|
| CHECK-001 | Telnet must be disabled on VTY lines |
| CHECK-002 | SSH version 2 must be enabled |
| CHECK-003 | Password encryption service must be enabled |
| CHECK-004 | Enable secret must be used instead of enable password |
| CHECK-005 | Remote syslog server must be configured |
| CHECK-006 | Login banner must be configured |
| CHECK-007 | VTY lines must have an idle timeout |
| CHECK-008 | VTY access must be restricted with an access-class |
| CHECK-009 | Unused interfaces must be administratively shut down *(parsed)* |

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
ansible-galaxy collection install -r requirements.yml
ansible-playbook playbooks/audit.yml
open reports/compliance-report.html   # macOS (use xdg-open on Linux)
```

Example remediation plan (`reports/remediation/SW1.cfg`):

```
! CHECK-008 [HIGH] VTY access must be restricted with an access-class
ip access-list standard MGMT-ACCESS
 permit 192.168.100.0 0.0.0.255
line vty 0 4
 access-class MGMT-ACCESS in
!
! CHECK-009 [MEDIUM] Unused interfaces must be administratively shut down
interface GigabitEthernet0/2
 shutdown
```

Query the JSON report, e.g. list every failed high-severity check:

```bash
jq -r '.devices[] | .name as $d | .results[] | select(.status == "FAIL" and .severity == "high") | "\($d) \(.id) \(.title)"' reports/compliance-report.json
```

The sample configs are intentionally imperfect: `R1` is non-compliant and `SW1` is compliant, so the audit is expected to fail on `R1`.

## Role variables

| Variable | Default | Description |
|---|---|---|
| `compliance_audit_checks` | `[]` | List of checks to evaluate |
| `compliance_audit_config_file` | `""` | Path to the device configuration to audit |
| `compliance_audit_fail_on_noncompliance` | `true` | Fail the host if at least one check fails |
| `compliance_audit_severity_weights` | `{high: 3, medium: 2, low: 1}` | Weight of each severity in the compliance score |
| `compliance_audit_remediation_enabled` | `true` | Generate per-device remediation plans |
| `compliance_audit_remediation_syslog_host` | `<syslog-server-ip>` | Syslog server used in remediation commands |
| `compliance_audit_remediation_mgmt_network` | `<mgmt-network> <wildcard>` | Network allowed on VTY lines |
| `compliance_audit_remediation_mgmt_acl` | `MGMT-ACCESS` | Name of the management ACL |
| `compliance_audit_json_report_enabled` | `true` | Generate the JSON report |
| `compliance_audit_json_report_path` | `reports/compliance-report.json` | JSON report output path |
| `compliance_audit_report_enabled` | `true` | Generate the HTML report |
| `compliance_audit_report_path` | `reports/compliance-report.html` | Report output path |

## Project structure

```
├── inventories/offline/      # Inventory for offline (file-based) audits
├── playbooks/audit.yml       # Entry point
├── roles/compliance_audit/   # Audit logic, report template
├── rules/cisco_ios.yml       # Compliance rules
├── samples/configs/          # Sample device configurations
└── .github/workflows/ci.yml  # Lint + secret scanning
```

## Roadmap

- [x] **Level 1**: inventory, first checks (SSHv2, telnet)
- [x] **Level 2**: role, YAML-defined rules, HTML report
- [ ] **Level 3**: structured parsing with resource modules *(in progress)*, live devices (GNS3 lab)
- [ ] **Level 4**: remediation: per-device remediation plans *(done)*; apply with check/diff mode, config backup, rolling changes *(next, on the GNS3 lab)*
- [ ] **Level 5**: custom plugins, Molecule tests, Execution Environment, AWX

## License

MIT
