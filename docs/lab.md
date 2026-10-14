# Live lab (GNS3)

The offline mode audits configuration files. This lab runs the same audit against
real Cisco IOS devices over SSH.

## Topology

```
             192.168.100.0/24 (management)
   ┌──────────────┬──────────────┬───────────────┐
   │              │              │               │
 R1 e0/0        SW1 Vlan1     GNS3 server      Ansible control node
 .11            .21 (e0/0)    (Cloud/NAT)      (laptop or VM)
```

- **R1**: Cisco IOL router (`lab/bootstrap/R1.cfg`)
- **SW1**: Cisco IOL L2 switch (`lab/bootstrap/SW1.cfg`)

The bootstrap configs give Ansible SSH access and intentionally reproduce the
findings of `samples/configs/`, so the live audit should match the offline one.

## 1. GNS3 server

Any x86 Linux host works (a Proxmox VM, for example: Ubuntu 22.04, 2 vCPU, 4 GB RAM).
IOL images run as native processes, so nested virtualization is not required.

```bash
curl -O https://raw.githubusercontent.com/GNS3/gns3-server/master/scripts/remote-install.sh
sudo bash remote-install.sh --with-iou --with-i386-repository
```

Install the **same GNS3 version** on the client, then add the server as a remote server.
Cisco IOL images are not distributed with GNS3: use images you are licensed for
(for example from Cisco Modeling Labs Free).

## 2. Devices

1. Create R1 (IOL L3) and SW1 (IOL L2).
2. Connect R1 `e0/0` and SW1 `e0/0` to a switch linked to a **Cloud** node bridged
   to the management network, so the control node can reach `192.168.100.0/24`.
3. Open each console and paste the matching file from `lab/bootstrap/`.
4. From the control node: `ssh admin@192.168.100.11` must work before going further.

## 3. Inventory and secrets

```bash
cp -r inventories/lab.example inventories/lab       # git-ignored
ansible-vault create inventories/lab/group_vars/vault.yml
#   vault_lab_password: <device password>
```

## 4. Run the audit

```bash
ansible-playbook -i inventories/lab playbooks/audit.yml --ask-vault-pass
```

`compliance_audit_config_source: device` (set in the lab inventory) makes the role read
`show running-config` over SSH instead of a file. Reports and remediation plans are
generated exactly as in offline mode.
