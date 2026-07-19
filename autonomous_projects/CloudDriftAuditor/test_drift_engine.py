"""
test_drift_engine.py

Strict Test-Driven Development (TDD) suite for CloudDriftAuditor.
Validates mathematical accuracy, I/O integration, and Win32 safety
without using any mocks.
"""

import io
import pathlib
from decimal import Decimal
from typing import Generator

import pytest

from drift_engine import AuditReport, audit_stream
from io_handler import stream_billing_file


def test_audit_stream_normal() -> None:
    """
    Test Case 1: Normal accumulation.
    Validates standard parsing and accumulation without drift or spikes.
    """
    lines = io.StringIO("ts,svc,cost\n1,a,10.50\n2,b,20.25\n")
    report: AuditReport = audit_stream(lines)
    
    assert report.total_decimal == Decimal('30.75')
    assert report.drift == Decimal('0')
    assert len(report.anomalies) == 0


def test_audit_stream_spike() -> None:
    """
    Test Case 2: Spike detection.
    Validates that charges exceeding the default threshold are flagged.
    """
    lines = io.StringIO("ts,svc,cost\n1,a,2000000.00\n")
    report: AuditReport = audit_stream(lines)
    
    assert len(report.anomalies) == 1
    assert report.anomalies[0].startswith('SPIKE')


def test_audit_stream_float_drift() -> None:
    """
    Test Case 3: Float drift detection.
    Validates that IEEE 754 float accumulation drifts from exact Decimal
    accumulation over many iterations of 0.10.
    """
    def generate_lines() -> Generator[str, None, None]:
        yield "ts,svc,cost"
        for _ in range(1000):
            yield "1,a,0.10"
            
    report: AuditReport = audit_stream(generate_lines())
    
    assert report.drift > Decimal('0')


def test_integration_with_io(tmp_path: pathlib.Path) -> None:
    """
    Test Case 4: Integration with I/O.
    Validates that stream_billing_file correctly feeds data to audit_stream.
    """
    file_path = tmp_path / "billing.csv"
    file_path.write_text("ts,svc,cost\n1,a,100.00\n2,b,50.00\n", encoding="utf-8")
    
    lines = stream_billing_file(str(file_path))
    report: AuditReport = audit_stream(lines)
    
    assert report.total_decimal == Decimal('150.00')
    assert report.drift == Decimal('0')
    assert len(report.anomalies) == 0


def test_empty_file_guard(tmp_path: pathlib.Path) -> None:
    """
    Test Case 5: Empty file guard.
    Validates that 0-byte files do not crash mmap on Win32 and return
    an AuditReport with zeroed totals.
    """
    file_path = tmp_path / "empty.csv"
    file_path.touch()
    
    lines = stream_billing_file(str(file_path))
    report: AuditReport = audit_stream(lines)
    
    assert report.total_decimal == Decimal('0.0')
    assert report.total_float == 0.0
    assert report.drift == Decimal('0')
    assert report.max_charge == Decimal('0.0')
    assert len(report.anomalies) == 0