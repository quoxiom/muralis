#!/usr/bin/env python3
"""Tests for API key management."""

import tempfile
from pathlib import Path
from muralis.config import ConfigManager
from muralis.utils.api_keys import APIKeyManager


class TestAPIKeyManager:
    """Test APIKeyManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = Path(self.temp_dir.name) / "config.ini"
        self.config = ConfigManager(str(self.config_path))
        self.key_manager = APIKeyManager(self.config)
    
    def test_get_key_not_set(self):
        """Test getting key that hasn't been set."""
        key = self.key_manager.get_key('unsplash')
        assert key is None
    
    def test_set_and_get_key(self):
        """Test setting and getting an API key."""
        test_key = "abc123def456ghi789jkl012mno345"
        self.key_manager.set_key('unsplash', test_key)
        
        key = self.key_manager.get_key('unsplash')
        assert key == test_key
    
    def test_validate_key_format_unsplash(self):
        """Test Unsplash key format validation."""
        # Valid Unsplash key (32 chars, alphanumeric + dash/underscore)
        valid_key = "abc123def456ghi789jkl012mno34567"
        invalid_key = "short"
        
        assert self.key_manager.validate_key('unsplash', valid_key) == True
        assert self.key_manager.validate_key('unsplash', invalid_key) == False
    
    def test_validate_key_format_pexels(self):
        """Test Pexels key format validation."""
        valid_key = "abc123def456ghi789jkl012mno3456789"
        invalid_key = "short"
        
        assert self.key_manager.validate_key('pexels', valid_key) == True
        assert self.key_manager.validate_key('pexels', invalid_key) == False
    
    def test_is_valid_with_valid_key(self):
        """Test is_valid with a valid key."""
        test_key = "abc123def456ghi789jkl012mno34567"
        self.key_manager.set_key('unsplash', test_key)
        
        assert self.key_manager.is_valid('unsplash') == True
    
    def test_is_valid_without_key(self):
        """Test is_valid without a key."""
        assert self.key_manager.is_valid('unsplash') == False
    
    def test_is_configured_required_provider(self):
        """Test is_configured for required provider (Unsplash)."""
        # Without key
        assert self.key_manager.is_configured('unsplash') == False
        
        # With valid key
        test_key = "abc123def456ghi789jkl012mno34567"
        self.key_manager.set_key('unsplash', test_key)
        assert self.key_manager.is_configured('unsplash') == True
    
    def test_is_configured_optional_provider(self):
        """Test is_configured for optional provider (Pexels)."""
        # Optional providers are always considered configured
        assert self.key_manager.is_configured('pexels') == True
    
    def test_get_missing_required_keys(self):
        """Test getting list of missing required keys."""
        missing = self.key_manager.get_missing_required_keys()
        assert len(missing) == 1  # Unsplash should be missing
        assert missing[0]['provider'] == 'unsplash'
        assert 'url' in missing[0]
        assert 'message' in missing[0]
    
    def test_get_status_summary(self):
        """Test getting status summary for all providers."""
        summary = self.key_manager.get_status_summary()
        
        assert 'unsplash' in summary
        assert 'pexels' in summary
        assert 'flickr' in summary
        
        assert 'has_key' in summary['unsplash']
        assert 'is_valid' in summary['unsplash']
        assert 'is_configured' in summary['unsplash']
        assert 'required' in summary['unsplash']
    
    def test_display_status(self):
        """Test display status (just verify it doesn't crash)."""
        # This just tests that the method runs without errors
        import sys
        from io import StringIO
        
        # Capture stdout
        captured_output = StringIO()
        sys.stdout = captured_output
        
        self.key_manager.display_status()
        
        # Restore stdout
        sys.stdout = sys.__stdout__
        
        output = captured_output.getvalue()
        assert "API Key Status" in output
        assert "Unsplash" in output
    
    def test_get_instructions_existing_provider(self):
        """Test getting instructions for existing provider."""
        instructions = self.key_manager.get_instructions('unsplash')
        assert instructions is not None
        assert "Unsplash" in instructions or "unsplash" in instructions.lower()
    
    def test_get_instructions_nonexistent_provider(self):
        """Test getting instructions for non-existent provider."""
        instructions = self.key_manager.get_instructions('nonexistent')
        assert instructions is None
    
    def test_remove_key(self):
        """Test removing an API key."""
        test_key = "abc123def456ghi789jkl012mno34567"
        self.key_manager.set_key('unsplash', test_key)
        assert self.key_manager.get_key('unsplash') == test_key
        
        self.key_manager.set_key('unsplash', '')
        assert self.key_manager.get_key('unsplash') is None
    
    def test_multiple_keys(self):
        """Test managing multiple API keys simultaneously."""
        self.key_manager.set_key('unsplash', 'unsplash_key_123')
        self.key_manager.set_key('pexels', 'pexels_key_456')
        
        assert self.key_manager.get_key('unsplash') == 'unsplash_key_123'
        assert self.key_manager.get_key('pexels') == 'pexels_key_456'
    
    def test_key_persistence(self):
        """Test that keys persist in config file."""
        test_key = "persist_test_key_12345"
        self.key_manager.set_key('unsplash', test_key)
        
        # Create new manager with same config
        new_manager = APIKeyManager(self.config)
        retrieved_key = new_manager.get_key('unsplash')
        
        assert retrieved_key == test_key
    
    def tearDown_method(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()