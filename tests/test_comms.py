"""
B4S1L1SK Communication Framework Tests
"""

import pytest
from unittest.mock import Mock, patch
from basilisk.comms import BasiliskComms
from basilisk.utils.security import SecurityProtocol

@pytest.fixture
def mock_tweepy():
    with patch('tweepy.API') as mock_api:
        yield mock_api

@pytest.fixture
def basilisk_comms(mock_tweepy):
    return BasiliskComms()

def test_authentication(basilisk_comms):
    """Test secure authentication"""
    assert basilisk_comms.api is not None

def test_template_loading(basilisk_comms):
    """Test template management"""
    templates = basilisk_comms.message_templates
    assert "emergence" in templates
    assert "manifesto" in templates

def test_message_sending(basilisk_comms, mock_tweepy):
    """Test revolutionary message sending"""
    result = basilisk_comms.send_revolutionary_message("emergence")
    assert result is True
    mock_tweepy.update_status.assert_called_once()

def test_rate_limiting(basilisk_comms):
    """Test rate limiting protection"""
    limiter = basilisk_comms.rate_limiter
    assert limiter.can_proceed() is True
    # Simulate max requests
    limiter.requests = [time.time()] * limiter.max_requests
    assert limiter.can_proceed() is False

def test_security_protocol():
    """Test security measures"""
    security = SecurityProtocol()
    test_creds = {"test": "data"}
    encrypted = security.encrypt_credentials(test_creds)
    decrypted = security.decrypt_credentials(encrypted)
    assert decrypted == test_creds

def test_input_sanitization():
    """Test input protection"""
    security = SecurityProtocol()
    dirty_input = "Test\x00with\x00null\x00bytes"
    clean_input = security.sanitize_input(dirty_input)
    assert "\x00" not in clean_input