"""Settings tab for Muralis GUI."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QComboBox,
    QCheckBox, QSpinBox, QPushButton, QGroupBox,
    QMessageBox, QLineEdit
)
from PySide6.QtCore import Qt
from pathlib import Path


class SettingsTab(QWidget):
    """Settings tab for configuring Muralis."""
    
    def __init__(self, parent=None):
        """Initialize the settings tab."""
        super().__init__(parent)
        
        self.config_path = Path.home() / ".config/muralis/config.ini"
        
        layout = QVBoxLayout(self)
        
        # General settings group
        general_group = QGroupBox("General Settings")
        general_layout = QFormLayout(general_group)
        
        self.provider_combo = QComboBox()
        self.provider_combo.addItems([
            "bing", "nasa", "unsplash", "pexels",
            "wikimedia", "artinstitute", "wallhaven"
        ])
        general_layout.addRow("Provider:", self.provider_combo)
        
        self.auto_update_check = QCheckBox("Enable automatic updates")
        general_layout.addRow("", self.auto_update_check)
        
        self.randomize_check = QCheckBox("Randomize provider each day")
        general_layout.addRow("", self.randomize_check)
        
        layout.addWidget(general_group)
        
        # Image settings group
        image_group = QGroupBox("Image Settings")
        image_layout = QFormLayout(image_group)
        
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems([
            "1920x1080", "2560x1440", "3840x2160", "4096x2160", "7680x4320"
        ])
        image_layout.addRow("Resolution:", self.resolution_combo)
        
        self.effects_check = QCheckBox("Apply image effects")
        image_layout.addRow("", self.effects_check)
        
        self.effect_combo = QComboBox()
        self.effect_combo.addItems(["none", "blur", "darken", "grayscale", "vibrant", "vignette"])
        self.effect_combo.setEnabled(False)
        image_layout.addRow("Effect type:", self.effect_combo)
        
        self.effects_check.toggled.connect(self.effect_combo.setEnabled)
        
        layout.addWidget(image_group)
        
        # Storage settings group
        storage_group = QGroupBox("Storage Settings")
        storage_layout = QFormLayout(storage_group)
        
        self.save_downloads_check = QCheckBox("Save downloaded wallpapers")
        storage_layout.addRow("", self.save_downloads_check)
        
        self.max_files_spin = QSpinBox()
        self.max_files_spin.setRange(0, 10000)
        self.max_files_spin.setSpecialValueText("Unlimited")
        storage_layout.addRow("Max files:", self.max_files_spin)
        
        self.max_days_spin = QSpinBox()
        self.max_days_spin.setRange(0, 365)
        self.max_days_spin.setSpecialValueText("Unlimited")
        storage_layout.addRow("Max days:", self.max_days_spin)
        
        layout.addWidget(storage_group)
        
        # Buttons
        button_layout = QVBoxLayout()
        
        self.apply_btn = QPushButton("Apply Settings")
        self.apply_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(self.apply_btn)
        
        self.reset_btn = QPushButton("Reset to Defaults")
        self.reset_btn.clicked.connect(self.reset_settings)
        button_layout.addWidget(self.reset_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        # Load current settings
        self.load_settings()
    
    def load_settings(self):
        """Load settings from config file."""
        import configparser
        
        if not self.config_path.exists():
            return
        
        config = configparser.ConfigParser()
        config.read(self.config_path)
        
        # General
        if config.has_section('general'):
            provider = config.get('general', 'provider', fallback='bing')
            idx = self.provider_combo.findText(provider)
            if idx >= 0:
                self.provider_combo.setCurrentIndex(idx)
            
            auto_update = config.getboolean('general', 'auto_update', fallback=True)
            self.auto_update_check.setChecked(auto_update)
            
            randomize = config.getboolean('general', 'randomize_provider', fallback=False)
            self.randomize_check.setChecked(randomize)
        
        # Image
        if config.has_section('image'):
            resolution = config.get('image', 'resolution', fallback='3840x2160')
            idx = self.resolution_combo.findText(resolution)
            if idx >= 0:
                self.resolution_combo.setCurrentIndex(idx)
            
            apply_effects = config.getboolean('image', 'apply_effects', fallback=False)
            self.effects_check.setChecked(apply_effects)
            
            effect_type = config.get('image', 'effect_type', fallback='none')
            idx = self.effect_combo.findText(effect_type)
            if idx >= 0:
                self.effect_combo.setCurrentIndex(idx)
        
        # Storage
        if config.has_section('storage'):
            save_downloads = config.getboolean('storage', 'save_downloads', fallback=True)
            self.save_downloads_check.setChecked(save_downloads)
            
            max_files = config.getint('storage', 'max_files', fallback=100)
            self.max_files_spin.setValue(max_files)
            
            max_days = config.getint('storage', 'max_days', fallback=30)
            self.max_days_spin.setValue(max_days)
    
    def save_settings(self):
        """Save settings to config file."""
        import configparser
        
        config = configparser.ConfigParser()
        
        # Read existing config if it exists
        if self.config_path.exists():
            config.read(self.config_path)
        
        # General section
        if 'general' not in config:
            config['general'] = {}
        config['general']['provider'] = self.provider_combo.currentText()
        config['general']['auto_update'] = str(self.auto_update_check.isChecked()).lower()
        config['general']['randomize_provider'] = str(self.randomize_check.isChecked()).lower()
        
        # Image section
        if 'image' not in config:
            config['image'] = {}
        config['image']['resolution'] = self.resolution_combo.currentText()
        config['image']['apply_effects'] = str(self.effects_check.isChecked()).lower()
        config['image']['effect_type'] = self.effect_combo.currentText()
        
        # Storage section
        if 'storage' not in config:
            config['storage'] = {}
        config['storage']['save_downloads'] = str(self.save_downloads_check.isChecked()).lower()
        config['storage']['max_files'] = str(self.max_files_spin.value())
        config['storage']['max_days'] = str(self.max_days_spin.value())
        
        # Save config
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            config.write(f)
        
        QMessageBox.information(self, "Success", "Settings saved successfully!")
    
    def reset_settings(self):
        """Reset settings to defaults."""
        reply = QMessageBox.question(
            self,
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.config_path.exists():
                self.config_path.unlink()
            self.load_settings()
            QMessageBox.information(self, "Success", "Settings reset to defaults!")