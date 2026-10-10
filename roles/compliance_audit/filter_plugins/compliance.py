"""Custom Jinja2 filters for the compliance_audit role.

They take the structured output of cisco.ios resource modules (state: parsed)
and turn it into audit findings and remediation blocks. Keeping this logic in
Python instead of long Jinja expressions makes it readable and unit-testable.
"""

from __future__ import annotations

L2_USAGE_KEYS = ("mode", "access", "trunk")
L3_USAGE_KEYS = ("ipv4", "ipv6")


def _names_with_any_key(entries, keys):
    """Return the names of entries that define at least one of the given keys."""
    return {entry["name"] for entry in entries or [] if any(entry.get(key) for key in keys)}


def unused_interfaces(interfaces, l2_interfaces=None, l3_interfaces=None):
    """Return the enabled interfaces that look unused.

    An interface is unused when it has no description, no switchport
    configuration and no IP address. IOS interfaces are enabled unless
    explicitly shut down, so a missing ``enabled`` key counts as enabled.
    """
    used = _names_with_any_key(l2_interfaces, L2_USAGE_KEYS) | _names_with_any_key(l3_interfaces, L3_USAGE_KEYS)
    return [
        iface["name"]
        for iface in interfaces or []
        if not iface.get("description") and iface.get("enabled", True) and iface["name"] not in used
    ]


def interface_remediation(names, lines=("shutdown",)):
    """Build one remediation block per interface, in ios_config parents/lines format."""
    return [{"parents": [f"interface {name}"], "lines": list(lines)} for name in names or []]


class FilterModule:
    """Ansible filter plugin entry point."""

    def filters(self):
        return {
            "unused_interfaces": unused_interfaces,
            "interface_remediation": interface_remediation,
        }
