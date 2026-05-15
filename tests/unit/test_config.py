"""Tests for configuration management."""

import pytest
from pathlib import Path
from muralis.config import ConfigManager

def test_config_creation(tmp_path):
    config_path = tmp_path / "config.ini"
    config = ConfigManager(str(config_path))
    
    assert config.get('general', 'provider') == 'bing'
    assert config.get_bool('general', 'auto_update') == True

def test_config_modification(tmp_path):
    config_path = tmp_path / "config.ini"
    config = ConfigManager(str(config_path))
    
    config.set('general', 'provider', 'nasa')
    assert config.get('general', 'provider') == 'nasa'
