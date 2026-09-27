# network-compliance-ansible

Network compliance audit and remediation framework built with Ansible.

> 🚧 Work in progress

## Roadmap
- [ ] Level 1: inventory, first checks (SSHv2, telnet)
- [ ] Level 2: roles per domain, YAML-defined rules, HTML report
- [ ] Level 3: resource modules, `show` output parsing
- [ ] Level 4: remediation (check/diff, backup, serial)
- [ ] Level 5: custom plugins, Molecule, Execution Environment, AWX

## Run locally
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
ansible-galaxy collection install -r requirements.yml
ansible-playbook playbooks/audit.yml
```
