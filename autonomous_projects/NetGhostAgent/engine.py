"""
NetGhostAgent State-Machine Engine

This module provides the core logic for processing chronological network
events and detecting state contradictions, such as NAT translations
occurring for IP addresses that lack active DHCP leases or ARP entries.
"""

from typing import Iterable, List, Dict

from models import EventType, LogEvent, Anomaly


def detect_anomalies(events: Iterable[LogEvent]) -> List[Anomaly]:
    """
    Processes a chronological iterable of network events to detect anomalies.

    This pure function maintains internal state for active DHCP leases and
    ARP table entries. It flags any NAT translation events where the source
    IP does not have a corresponding active lease or ARP entry.

    Args:
        events: An iterable of LogEvent objects, assumed to be chronological.

    Returns:
        A list of Anomaly objects representing detected contradictions.
    """
    active_leases: Dict[str, str] = {}
    arp_table: Dict[str, str] = {}
    anomalies: List[Anomaly] = []

    for event in events:
        try:
            if event.event_type == EventType.DHCP_ASSIGN:
                if event.mac:
                    active_leases[event.ip] = event.mac

            elif event.event_type == EventType.DHCP_RELEASE:
                active_leases.pop(event.ip, None)

            elif event.event_type == EventType.ARP_UPDATE:
                if event.mac:
                    arp_table[event.ip] = event.mac

            elif event.event_type == EventType.NAT_TRANSLATE:
                if event.ip not in active_leases and event.ip not in arp_table:
                    anomaly = Anomaly(
                        timestamp=event.timestamp,
                        ip=event.ip,
                        description="Ghost Client: NAT activity without DHCP/ARP presence"
                    )
                    anomalies.append(anomaly)
        except Exception:
            # Gracefully handle unexpected errors for individual events
            # to ensure the engine continues processing the stream.
            continue

    return anomalies