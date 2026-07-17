"""
NetGhostAgent Test Suite

This module provides a strict unit test suite for the NetGhostAgent system,
validating the parser, state-machine engine, and CLI components.
"""

import json
import pathlib
from typing import List

import pytest

from models import EventType, LogEvent, Anomaly
from parser import parse_line
from engine import detect_anomalies
from cli import main


def test_parse_line_valid_dhcp() -> None:
    """Test parsing a valid DHCP assignment log line."""
    line = "1620000000 DHCPACK on 192.168.1.10 to aa:bb:cc:dd:ee:ff"
    event = parse_line(line)
    
    assert event is not None
    assert event.timestamp == 1620000000
    assert event.event_type == EventType.DHCP_ASSIGN
    assert event.ip == "192.168.1.10"
    assert event.mac == "aa:bb:cc:dd:ee:ff"


def test_parse_line_valid_arp() -> None:
    """Test parsing a valid ARP update log line."""
    line = "1620000005 ARP update for 192.168.1.10 at aa:bb:cc:dd:ee:ff"
    event = parse_line(line)
    
    assert event is not None
    assert event.timestamp == 1620000005
    assert event.event_type == EventType.ARP_UPDATE
    assert event.ip == "192.168.1.10"
    assert event.mac == "aa:bb:cc:dd:ee:ff"


def test_parse_line_valid_nat() -> None:
    """Test parsing a valid NAT translation log line."""
    line = "1620000010 NAT translation for 192.168.1.10:8080"
    event = parse_line(line)
    
    assert event is not None
    assert event.timestamp == 1620000010
    assert event.event_type == EventType.NAT_TRANSLATE
    assert event.ip == "192.168.1.10"
    assert event.port == 8080


def test_parse_line_garbage() -> None:
    """Test parsing garbage strings returns None."""
    assert parse_line("this is just some random text") is None
    assert parse_line("") is None
    assert parse_line("DHCPACK on invalid_ip to mac") is None
    assert parse_line(None) is None  # type: ignore


def test_detect_anomalies_normal_flow() -> None:
    """Test detect_anomalies with a normal flow yielding no anomalies."""
    events: List[LogEvent] = [
        LogEvent(timestamp=1, event_type=EventType.DHCP_ASSIGN, ip="10.0.0.1", mac="aa:bb:cc:dd:ee:ff"),
        LogEvent(timestamp=2, event_type=EventType.ARP_UPDATE, ip="10.0.0.1", mac="aa:bb:cc:dd:ee:ff"),
        LogEvent(timestamp=3, event_type=EventType.NAT_TRANSLATE, ip="10.0.0.1", port=80),
        LogEvent(timestamp=4, event_type=EventType.DHCP_RELEASE, ip="10.0.0.1", mac="aa:bb:cc:dd:ee:ff"),
    ]
    
    anomalies = detect_anomalies(events)
    assert len(anomalies) == 0


def test_detect_anomalies_ghost_client() -> None:
    """Test detect_anomalies flags NAT without DHCP/ARP."""
    events: List[LogEvent] = [
        LogEvent(timestamp=10, event_type=EventType.NAT_TRANSLATE, ip="10.0.0.99", port=443),
    ]
    
    anomalies = detect_anomalies(events)
    
    assert len(anomalies) == 1
    anomaly = anomalies[0]
    assert anomaly.timestamp == 10
    assert anomaly.ip == "10.0.0.99"
    assert "Ghost Client" in anomaly.description


def test_cli_main_empty_file(tmp_path: pathlib.Path) -> None:
    """Test cli.main with an empty log file returns 0 without ValueError."""
    log_file = tmp_path / "empty.log"
    log_file.write_text("")
    
    exit_code = main(["--logfile", str(log_file)])
    
    assert exit_code == 0


def test_cli_main_ghost_client_log(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Test cli.main with a ghost client log outputs valid JSON anomaly."""
    log_file = tmp_path / "ghost.log"
    log_file.write_text("100 NAT translation for 192.168.1.50:22\n")
    
    exit_code = main(["--logfile", str(log_file)])
    assert exit_code == 0
    
    captured = capsys.readouterr()
    output_data = json.loads(captured.out)
    
    assert isinstance(output_data, list)
    assert len(output_data) == 1
    assert output_data[0]["ip"] == "192.168.1.50"
    assert "Ghost Client" in output_data[0]["description"]