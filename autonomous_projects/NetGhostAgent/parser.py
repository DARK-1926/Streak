"""
NetGhostAgent Log Parser

This module provides pure functions for parsing standard syslog text
into structured LogEvent models. It uses compiled regular expressions
to efficiently extract network events without side effects.
"""

import re
from typing import Optional

from models import EventType, LogEvent

# Compiled regex patterns for standard syslog formats.
# They optionally capture a Unix epoch timestamp and use word
# boundaries (\b) to ensure robustness against partial matches.
RE_DHCP_ASSIGN = re.compile(
    r"(?:(?P<timestamp>\d+)\b.*?)?\bDHCPACK\s+on\s+(?P<ip>[0-9.]+)\s+to\s+(?P<mac>[a-f0-9:]+)\b",
    re.IGNORECASE
)

RE_DHCP_RELEASE = re.compile(
    r"(?:(?P<timestamp>\d+)\b.*?)?\bDHCPRELEASE\s+of\s+(?P<ip>[0-9.]+)\s+from\s+(?P<mac>[a-f0-9:]+)\b",
    re.IGNORECASE
)

RE_ARP_UPDATE = re.compile(
    r"(?:(?P<timestamp>\d+)\b.*?)?\bARP\s+update\s+for\s+(?P<ip>[0-9.]+)\s+at\s+(?P<mac>[a-f0-9:]+)\b",
    re.IGNORECASE
)

RE_NAT_TRANSLATE = re.compile(
    r"(?:(?P<timestamp>\d+)\b.*?)?\bNAT\s+translation\s+for\s+(?P<ip>[0-9.]+):(?P<port>[0-9]+)\b",
    re.IGNORECASE
)


def parse_line(line: str) -> Optional[LogEvent]:
    """
    Parses a single log line and returns a LogEvent if a match is found.

    This function evaluates the input string against compiled regular
    expressions for DHCP, ARP, and NAT events. It is a pure function
    with no side effects.

    Args:
        line: The raw syslog line to parse.

    Returns:
        A populated LogEvent if a recognized pattern is matched,
        otherwise None.
    """
    if not line or not isinstance(line, str):
        return None

    match = RE_DHCP_ASSIGN.search(line)
    if match:
        return LogEvent(
            timestamp=int(match.group("timestamp") or 0),
            event_type=EventType.DHCP_ASSIGN,
            ip=match.group("ip"),
            mac=match.group("mac")
        )

    match = RE_DHCP_RELEASE.search(line)
    if match:
        return LogEvent(
            timestamp=int(match.group("timestamp") or 0),
            event_type=EventType.DHCP_RELEASE,
            ip=match.group("ip"),
            mac=match.group("mac")
        )

    match = RE_ARP_UPDATE.search(line)
    if match:
        return LogEvent(
            timestamp=int(match.group("timestamp") or 0),
            event_type=EventType.ARP_UPDATE,
            ip=match.group("ip"),
            mac=match.group("mac")
        )

    match = RE_NAT_TRANSLATE.search(line)
    if match:
        return LogEvent(
            timestamp=int(match.group("timestamp") or 0),
            event_type=EventType.NAT_TRANSLATE,
            ip=match.group("ip"),
            port=int(match.group("port"))
        )

    return None