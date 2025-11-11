"""
Tests for utility functions
"""

import pytest
from datetime import datetime
from shaed_order_elt.utils import clean_value, get_timestamp_string


def test_clean_value_none():
    """Test cleaning None values"""
    assert clean_value(None) == ''


def test_clean_value_string():
    """Test cleaning string values"""
    assert clean_value("test") == "test"
    assert clean_value('test with "quotes"') == 'test with ""quotes""'
    assert clean_value("test\nwith\nnewlines") == "test with newlines"


def test_clean_value_dict():
    """Test cleaning dictionary values"""
    value = {"key": "value", "nested": {"data": 123}}
    result = clean_value(value)
    assert isinstance(result, str)
    assert "key" in result


def test_clean_value_datetime():
    """Test cleaning datetime values"""
    dt = datetime(2024, 1, 1, 12, 0, 0)
    result = clean_value(dt)
    assert isinstance(result, str)
    assert "2024" in result


def test_clean_value_boolean():
    """Test cleaning boolean values"""
    assert clean_value(True) == "true"
    assert clean_value(False) == "false"


def test_get_timestamp_string():
    """Test timestamp string generation"""
    timestamp = get_timestamp_string()
    assert isinstance(timestamp, str)
    assert len(timestamp) == 15  # YYYYMMDD_HHMMSS
    assert "_" in timestamp

