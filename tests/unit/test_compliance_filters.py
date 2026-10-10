"""Unit tests for roles/compliance_audit/filter_plugins/compliance.py."""

import importlib.util
from pathlib import Path

import pytest

PLUGIN = Path(__file__).resolve().parents[2] / "roles/compliance_audit/filter_plugins/compliance.py"
spec = importlib.util.spec_from_file_location("compliance_filters", PLUGIN)
compliance = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compliance)


def iface(name, **kwargs):
    return {"name": name, **kwargs}


class TestUnusedInterfaces:
    def test_bare_enabled_interface_is_unused(self):
        assert compliance.unused_interfaces([iface("Gi0/2", enabled=True)]) == ["Gi0/2"]

    def test_missing_enabled_key_counts_as_enabled(self):
        assert compliance.unused_interfaces([iface("Gi0/2")]) == ["Gi0/2"]

    def test_shutdown_interface_is_ignored(self):
        assert compliance.unused_interfaces([iface("Gi0/2", enabled=False)]) == []

    def test_described_interface_is_used(self):
        assert compliance.unused_interfaces([iface("Gi0/1", enabled=True, description="Uplink")]) == []

    @pytest.mark.parametrize("l2", [{"mode": "access"}, {"access": {"vlan": 10}}, {"trunk": {"allowed_vlans": ["10"]}}])
    def test_switchport_config_marks_interface_used(self, l2):
        assert compliance.unused_interfaces([iface("Gi0/1", enabled=True)], [iface("Gi0/1", **l2)]) == []

    @pytest.mark.parametrize("l3", [{"ipv4": [{"address": "10.0.0.1/24"}]}, {"ipv6": [{"address": "2001:db8::1/64"}]}])
    def test_ip_address_marks_interface_used(self, l3):
        assert compliance.unused_interfaces([iface("Gi0/0", enabled=True)], None, [iface("Gi0/0", **l3)]) == []

    def test_l2_entry_without_usage_keys_does_not_count(self):
        # cisco.ios lists every interface in l2 output, even with no switchport config
        assert compliance.unused_interfaces([iface("Gi0/2", enabled=True)], [iface("Gi0/2")]) == ["Gi0/2"]

    def test_empty_inputs(self):
        assert compliance.unused_interfaces(None) == []
        assert compliance.unused_interfaces([]) == []

    def test_keeps_input_order(self):
        result = compliance.unused_interfaces([iface("Gi0/3"), iface("Gi0/1", description="x"), iface("Gi0/2")])
        assert result == ["Gi0/3", "Gi0/2"]


class TestInterfaceRemediation:
    def test_one_block_per_interface(self):
        assert compliance.interface_remediation(["Gi0/1", "Gi0/2"]) == [
            {"parents": ["interface Gi0/1"], "lines": ["shutdown"]},
            {"parents": ["interface Gi0/2"], "lines": ["shutdown"]},
        ]

    def test_custom_lines(self):
        blocks = compliance.interface_remediation(["Gi0/1"], lines=["description UNUSED", "shutdown"])
        assert blocks == [{"parents": ["interface Gi0/1"], "lines": ["description UNUSED", "shutdown"]}]

    def test_empty(self):
        assert compliance.interface_remediation([]) == []
        assert compliance.interface_remediation(None) == []


def test_filter_module_exposes_filters():
    filters = compliance.FilterModule().filters()
    assert set(filters) == {"unused_interfaces", "interface_remediation"}
