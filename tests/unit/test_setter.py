#!/usk/bin/env python3
"""Tests for desktop environment setters."""

from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile
from muralis.setter.base import WallpaperSetter
from muralis.setter.gnome import GnomeSetter
from muralis.setter.kde import KdeSetter
from muralis.setter.generic import GenericSetter

class TestSetters:
    """Test desktop environment setters."""

    def setup_method(self):
        """Setup test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_image = Path(self.temp_dir.name) / "test.jpg"
        # Create a dummy image file
        self.test_image.touch()

    @patch('subprocess.run')
    def test_gnome_setter(self, mock_run):
        """Test GNOME setter."""
        mock_run.return_value = MagicMock(returncode=0)
        
        setter = GnomeSetter()
        result = setter.set_wallpaper(str(self.test_image))
        assert result == True

    @patch('subprocess.run')
    def test_kde_setter(self, mock_run):
        """Test KDE setter."""
        mock_run.return_value = MagicMock(returncode=0)
        
        setter = KdeSetter()
        result = setter.set_wallpaper(str(self.test_image))
        assert result == True

    @patch('subprocess.run')
    def test_generic_setter(self, mock_run):
        """Test generic setter fallback."""
        mock_run.return_value = MagicMock(returncode=0)
        
        setter = GenericSetter()
        result = setter.set_wallpaper(str(self.test_image))
        assert result == True

    def test_detect_setter(self):
        """Test desktop environment detection."""
        from muralis.setter import get_wallpaper_setter
        setter = get_wallpaper_setter()
        assert isinstance(setter, WallpaperSetter)

    def teardown_method(self):
        """Clean test fixtures."""
        self.temp_dir.cleanup()
        self.test_image.unlink(missing_ok=True)