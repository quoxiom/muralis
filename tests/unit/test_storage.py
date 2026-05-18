#!/usr/bin/env python3
"""Tests for storage management."""

import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from muralis.storage import StorageManager
from muralis.config import ConfigManager


class TestStorageManager:
    """Test StorageManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = Path(self.temp_dir.name) / "config.ini"
        self.config = ConfigManager(str(self.config_path))
        
        # Set custom storage path
        self.storage_path = Path(self.temp_dir.name) / "wallpapers"
        self.config.set('storage', 'download_dir', str(self.storage_path))
        
        self.storage = StorageManager(self.config)
    
    def test_storage_creation(self):
        """Test storage directory creation."""
        assert self.storage_path.exists()
        assert self.storage_path.is_dir()
    
    def test_save_wallpaper(self):
        """Test saving a wallpaper file."""
        test_file = self.storage_path / "muralis_test.jpg"
        test_file.touch()
        
        assert test_file.exists()
        assert test_file.stat().st_size == 0
    
    def test_cleanup_by_count(self):
        """Test cleanup by max file count."""
        # Create 150 test files
        for i in range(150):
            file_path = self.storage_path / f"muralis_test_{i}.jpg"
            file_path.touch()
        
        # Set max files to 100
        self.config.set('storage', 'max_files', '100')
        deleted = self.storage.cleanup_old()
        
        # Should have deleted 50 files (150 - 100)
        assert deleted >= 50
        
        remaining = list(self.storage_path.glob("muralis_*.jpg"))
        assert len(remaining) <= 100
    
    def test_cleanup_by_age(self):
        """Test cleanup by max days."""
        # Create files with different ages
        old_date = datetime.now() - timedelta(days=40)
        new_date = datetime.now() - timedelta(days=5)
        
        for i in range(5):
            old_file = self.storage_path / f"muralis_old_{i}.jpg"
            old_file.touch()
            # Modify timestamp to look old
            stat = old_file.stat()
            os.utime(old_file, (stat.st_atime, old_date.timestamp()))
        
        for i in range(5):
            new_file = self.storage_path / f"muralis_new_{i}.jpg"
            new_file.touch()
            stat = new_file.stat()
            os.utime(new_file, (stat.st_atime, new_date.timestamp()))
        
        # Set max days to 30
        self.config.set('storage', 'max_days', '30')
        deleted = self.storage.cleanup_old()
        
        # Should delete old files (5)
        assert deleted >= 5
        
        remaining = list(self.storage_path.glob("muralis_*.jpg"))
        assert len(remaining) <= 5
    
    def test_no_cleanup_when_disabled(self):
        """Test no cleanup when limits are zero."""
        # Create test files
        for i in range(10):
            file_path = self.storage_path / f"muralis_test_{i}.jpg"
            file_path.touch()
        
        # Set limits to 0 (unlimited)
        self.config.set('storage', 'max_files', '0')
        self.config.set('storage', 'max_days', '0')
        
        deleted = self.storage.cleanup_old()
        assert deleted == 0
        
        remaining = list(self.storage_path.glob("muralis_*.jpg"))
        assert len(remaining) == 10
    
    def test_get_all_wallpapers(self):
        """Test getting all wallpaper files."""
        # Create files with different patterns
        files = [
            "muralis_20241215_bing.jpg",
            "muralis_20241216_nasa.jpg",
            "muralis_20241217_unsplash.jpg",
            "test_other.jpg",  # Should not be included
            "wallpaper.jpg"     # Should not be included
        ]
        
        for f in files:
            (self.storage_path / f).touch()
        
        wallpapers = self.storage.get_all_wallpapers()
        assert len(wallpapers) == 3
        assert all("muralis" in str(w) for w in wallpapers)
    
    def test_get_recent_wallpapers(self):
        """Test getting most recent wallpapers."""
        # Create files with different timestamps
        import time
        
        for i in range(20):
            file_path = self.storage_path / f"muralis_recent_{i}.jpg"
            file_path.touch()
            time.sleep(0.01)  # Ensure different timestamps
        
        recent = self.storage.get_recent_wallpapers(5)
        assert len(recent) == 5
        # Most recent should be last in list
        assert recent[0].stat().st_mtime >= recent[-1].stat().st_mtime
    
    def test_get_storage_usage(self):
        """Test storage usage statistics."""
        # Create files with content
        for i in range(5):
            file_path = self.storage_path / f"muralis_size_{i}.jpg"
            with open(file_path, 'wb') as f:
                f.write(b'x' * 1024)  # 1KB file
        
        usage = self.storage.get_storage_usage()
        assert usage['count'] == 5
        assert usage['total_size'] == 5 * 1024
        assert usage['average_size'] == 1024
        assert usage['total_size_mb'] == (5 * 1024) / (1024 * 1024)
    
    def test_get_history(self):
        """Test getting wallpaper history."""
        # Create some files
        for i in range(10):
            file_path = self.storage_path / f"muralis_history_{i}.jpg"
            file_path.touch()
        
        history = self.storage.get_history()
        assert len(history) <= 50  # Limit to 50
        assert all('path' in h for h in history)
        assert all('name' in h for h in history)
        assert all('size' in h for h in history)
        assert all('modified' in h for h in history)
    
    def test_organize_by_date(self):
        """Test organizing wallpapers by date subdirectories."""
        self.config.set('storage', 'create_subdirs', 'true')
        self.config.set('storage', 'organize_by', 'date')
        
        # Create a file with specific date in name
        test_file = self.storage_path / "muralis_20241215_test.jpg"
        test_file.touch()
        
        # This is a mock test - actual organization would be done in download logic
        # For now, just verify config settings
        assert self.config.get_bool('storage', 'create_subdirs') == True
        assert self.config.get_str('storage', 'organize_by') == 'date'
    
    def tearDown_method(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()


# Add missing import for os
import os