"""Storage management for Muralis wallpapers."""

import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional

class StorageManager:
    """Manages wallpaper storage and cleanup."""
    
    def __init__(self, config):
        self.config = config
        self.storage_path = config.get_download_dir()
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def cleanup_old(self) -> int:
        """Remove old wallpapers based on retention policy.
        
        Returns:
            Number of files deleted
        """
        max_files = self.config.get_int('storage', 'max_files', 100)
        max_days = self.config.get_int('storage', 'max_days', 30)
        
        # Get all wallpaper files
        files = self.get_all_wallpapers()
        
        if not files:
            return 0
        
        deleted_count = 0
        
        # Delete by age first (max_days == 0 means unlimited/disabled)
        if max_days > 0:
            cutoff = datetime.now() - timedelta(days=max_days)
            for f in files:
                if datetime.fromtimestamp(f.stat().st_mtime) < cutoff:
                    f.unlink()
                    deleted_count += 1
        
        # Refresh file list
        files = self.get_all_wallpapers()
        
        # Delete by count (oldest first); max_files == 0 means unlimited/disabled
        if max_files > 0 and len(files) > max_files:
            to_delete = files[max_files:]
            for f in to_delete:
                f.unlink()
                deleted_count += 1
        
        if deleted_count > 0:
            print(f"Cleaned up {deleted_count} old wallpapers")
        
        return deleted_count
    
    def get_all_wallpapers(self) -> List[Path]:
        """Get list of all wallpaper files."""
        patterns = ['muralis_*.jpg', 'muralis_*.jpeg', 'muralis_*.png']
        files = []
        
        for pattern in patterns:
            files.extend(self.storage_path.glob(pattern))
        
        # Sort by modification time (oldest first)
        files.sort(key=lambda x: x.stat().st_mtime)
        return files
    
    def get_recent_wallpapers(self, count: int = 10) -> List[Path]:
        """Get most recent wallpapers."""
        files = self.get_all_wallpapers()
        files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        return files[:count]
    
    def get_history(self) -> List[dict]:
        """Get wallpaper history with metadata."""
        files = self.get_all_wallpapers()
        files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        history = []
        for f in files[:50]:  # Limit to last 50
            history.append({
                'path': str(f),
                'name': f.name,
                'size': f.stat().st_size,
                'modified': datetime.fromtimestamp(f.stat().st_mtime).isoformat()
            })
        
        return history
    
    def get_storage_usage(self) -> dict:
        """Get storage usage statistics."""
        files = self.get_all_wallpapers()
        
        if not files:
            return {'count': 0, 'total_size': 0, 'average_size': 0}
        
        total_size = sum(f.stat().st_size for f in files)
        avg_size = total_size // len(files)
        
        return {
            'count': len(files),
            'total_size': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'average_size': avg_size,
            'average_size_mb': avg_size / (1024 * 1024)
        }
