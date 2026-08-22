"""Setup script for Muralis - Qutility Suite."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="muralis",
    version="0.3.0",
    author="Qamber Haidry",
    author_email="qamber@quoxiom.com",
    description="Muralis - Smart Wallpaper Manager for Linux",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/quoxiom/qutility-muralis",
    project_urls={
        "Bug Tracker": "https://github.com/quoxiom/qutility-muralis/issues",
        "Documentation": "https://github.com/quoxiom/qutility-muralis/wiki",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    
    # Core dependencies (always installed)
    install_requires=[
        "requests>=2.25.0",
        "Pillow>=8.0.0",
    ],
    
    # Optional dependencies (installed via extras)
    extras_require={
        # GUI support
        "gui": [
            "PySide6>=6.5.0",
        ],
        
        # Development dependencies
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        
        # Testing dependencies (alias for dev)
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
        ],
        
        # Documentation dependencies
        "docs": [
            "mkdocs>=1.5.0",
            "mkdocs-material>=9.0.0",
        ],
        
        # All dependencies (full installation)
        "full": [
            "PySide6>=6.5.0",           # GUI
            "pytest>=7.0.0",             # Testing
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "black>=23.0.0",             # Code formatting
            "flake8>=6.0.0",             # Linting
            "mypy>=1.0.0",               # Type checking
            "mkdocs>=1.5.0",             # Documentation
            "mkdocs-material>=9.0.0",
        ],
    },
    
    # Entry points for CLI
    entry_points={
        "console_scripts": [
            "muralis=muralis.__main__:main",
            "muralis-gui=muralis.gui:run_gui",
        ],
    },
    
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Desktop Environment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: POSIX :: Linux",
    ],
    keywords="wallpaper, desktop, linux, automation, background",
    license="MIT",
    include_package_data=True,
    zip_safe=False,
)