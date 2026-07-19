"""
Unit and integration tests for the FloatDriftAuditorAgent.
"""
import pathlib
from decimal import Decimal
from typing import List

import pytest

from models import DriftReport
from auditor import parse_cost, audit_stream
from main import process_file


def test_parse_cost_valid() -> None:
    """Assert parse_cost correctly parses a valid transaction line."""
    result = parse_cost('tx1,aws,0.0001')
    assert result == (0.0001, Decimal('0.0001'))


def test_parse_cost_invalid() -> None:
    """Assert parse_cost returns None for an invalid line."""
    result = parse_cost('header')
    assert result is None


def test_audit_stream_drift() -> None:
    """Assert float sum drifts while Decimal sum remains exact over 10,000 transactions."""
    lines: List[str] = ['tx1,aws,0.0001'] * 10000
    report: DriftReport = audit_stream(lines)
    
    assert report.decimal_total == Decimal('1.0000')
    assert report.divergence != 0
    assert report.transaction_count == 10000


def test_process_file_integration(tmp_path: pathlib.Path) -> None:
    """Integration test: process a temporary CSV file with known data."""
    file_path = tmp_path / "transactions.csv"
    lines = ['tx,aws,0.0001'] * 100
    file_path.write_text('\n'.join(lines) + '\n')
    
    report: DriftReport = process_file(str(file_path))
    
    assert report.transaction_count == 100
    assert report.decimal_total == Decimal('0.0100')
    assert isinstance(report.float_total, float)
    assert isinstance(report.divergence, float)


def test_process_file_empty_win32_guard(tmp_path: pathlib.Path) -> None:
    """Integration test: process an empty file without raising exceptions."""
    file_path = tmp_path / "empty.csv"
    file_path.write_text('')
    
    report: DriftReport = process_file(str(file_path))
    
    assert report.transaction_count == 0
    assert report.decimal_total == Decimal('0')
    assert report.float_total == 0.0
    assert report.divergence == 0.0