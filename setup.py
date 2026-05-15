"""Setup script for Muralis - Qutility Suite."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="muralis",
    version="0.1.0",
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
    install_requires=[
        "requests>=2.25.0",
        "Pillow>=8.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.12.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "mypy>=0.910",
        ],
        "gui": [
            "PyGObject>=3.42.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "muralis=muralis.__main__:main",
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
        "Operating System :: POSIX :: Linux",
    ],
    keywords="wallpaper, desktop, linux, automation, background",
    license="MIT",
    include_package_data=True,
    zip_safe=False,
)