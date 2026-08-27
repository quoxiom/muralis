# Muralis Makefile
# Muralis - a small wallpaper utility by Quoxiom

.PHONY: help install uninstall dev test clean run setup-service show-config \
        lint format coverage docs build release check \
        test-unit test-integration test-coverage test-quick test-slow \
        test-verbose test-watch test-failed

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Default target
help:
	@echo "${BLUE}═══════════════════════════════════════════════════════════${NC}"
	@echo "${GREEN}Muralis - Smart Wallpaper Manager${NC}"
	@echo "${BLUE}Muralis - a small wallpaper utility by Quoxiom${NC}"
	@echo "${BLUE}═══════════════════════════════════════════════════════════${NC}"
	@echo ""
	@echo "${YELLOW}Installation & Management:${NC}"
	@echo "  ${GREEN}make install${NC}        - Install for current user"
	@echo "  ${GREEN}make uninstall${NC}      - Uninstall completely"
	@echo "  ${GREEN}make dev${NC}            - Install in development mode"
	@echo "  ${GREEN}make clean${NC}          - Clean build artifacts"
	@echo ""
	@echo "${YELLOW}Usage:${NC}"
	@echo "  ${GREEN}make run${NC}            - Run once with default settings"
	@echo "  ${GREEN}make setup-service${NC}  - Install systemd timer for daily updates"
	@echo "  ${GREEN}make show-config${NC}    - Display current configuration"
	@echo "  ${GREEN}make check${NC}          - Check if Muralis is installed"
	@echo ""
	@echo "${YELLOW}Development:${NC}"
	@echo "  ${GREEN}make test${NC}           - Run all tests"
	@echo "  ${GREEN}make lint${NC}           - Run linter (flake8)"
	@echo "  ${GREEN}make format${NC}         - Format code with black"
	@echo "  ${GREEN}make coverage${NC}       - Generate test coverage report"
	@echo "  ${GREEN}make docs${NC}           - Build documentation"
	@echo ""
	@echo "${YELLOW}Packaging:${NC}"
	@echo "  ${GREEN}make build${NC}          - Build distribution packages"
	@echo "  ${GREEN}make release${NC}        - Create release package"
	@echo ""

# Installation
install:
	@echo "${BLUE}Installing Muralis...${NC}"
	@./scripts/install.sh
	@echo "${GREEN}✓ Installation complete${NC}"

uninstall:
	@echo "${BLUE}Uninstalling Muralis...${NC}"
	@./scripts/uninstall.sh
	@echo "${GREEN}✓ Uninstallation complete${NC}"

# Development installation
dev:
	@echo "${BLUE}Installing in development mode...${NC}"
	@pip install -e .[dev]
	@echo "${GREEN}✓ Development installation complete${NC}"
	@echo "${YELLOW}Note: Run 'source venv/bin/activate' if using virtual environment${NC}"

# Code quality
lint:
	@echo "${BLUE}Running linter...${NC}"
	@flake8 src/ --count --statistics --show-source --max-line-length=100
	@echo "${GREEN}✓ Linting complete${NC}"

format:
	@echo "${BLUE}Formatting code...${NC}"
	@black src/ --line-length=100
	@echo "${GREEN}✓ Code formatted${NC}"

coverage:
	@echo "${BLUE}Generating coverage report...${NC}"
	@pytest tests/ --cov=muralis --cov-report=html --cov-report=term --cov-report=xml
	@echo "${GREEN}✓ Coverage report generated in htmlcov/${NC}"
	@echo "${YELLOW}Open htmlcov/index.html to view report${NC}"

# Cleanup
clean:
	@echo "${BLUE}Cleaning build artifacts...${NC}"
	@rm -rf build/ dist/ *.egg-info .pytest_cache .coverage htmlcov/
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name ".DS_Store" -delete
	@echo "${GREEN}✓ Cleanup complete${NC}"

clean-all: clean
	@echo "${BLUE}Removing virtual environment...${NC}"
	@rm -rf venv/
	@echo "${GREEN}✓ Complete cleanup${NC}"

# Build
build:
	@echo "${BLUE}Building distribution packages...${NC}"
	@rm -rf dist/ build/
	@python -m build
	@echo "${GREEN}✓ Build complete${NC}"
	@ls -lh dist/

release: clean build
	@echo "${BLUE}Creating release package...${NC}"
	@twine check dist/*
	@echo "${GREEN}✓ Release package ready${NC}"
	@echo "${YELLOW}To upload to PyPI: twine upload dist/*${NC}"

# Usage
run:
	@echo "${BLUE}Running Muralis...${NC}"
	@muralis --once
	@echo "${GREEN}✓ Wallpaper update complete${NC}"

run-verbose:
	@muralis --once --verbose

setup-service:
	@echo "${BLUE}Setting up daily automatic updates...${NC}"
	@muralis --set-daily
	@echo "${GREEN}✓ Daily updates scheduled${NC}"

show-config:
	@muralis --show-config

# Check installation
check:
	@echo "${BLUE}Checking Muralis installation...${NC}"
	@which muralis > /dev/null && echo "${GREEN}✓ Muralis is installed: $(which muralis)${NC}" || echo "${RED}✗ Muralis not found in PATH${NC}"
	@muralis --version 2>/dev/null && echo "${GREEN}✓ Version: $(muralis --version)${NC}" || echo "${RED}✗ Version check failed${NC}"
	@test -f ~/.config/muralis/config.ini && echo "${GREEN}✓ Configuration exists${NC}" || echo "${YELLOW}⚠ Configuration not found (will be created on first run)${NC}"

# Documentation
docs:
	@echo "${BLUE}Building documentation...${NC}"
	@if command -v mkdocs > /dev/null; then \
		mkdocs build; \
		echo "${GREEN}✓ Documentation built in site/${NC}"; \
	else \
		echo "${RED}✗ mkdocs not installed. Run: pip install mkdocs mkdocs-material${NC}"; \
	fi

# Quick start
quickstart:
	@echo "${BLUE}Quick start guide:${NC}"
	@echo ""
	@echo "1. ${GREEN}make install${NC}     - Install Muralis"
	@echo "2. ${GREEN}make run${NC}         - Get your first wallpaper"
	@echo "3. ${GREEN}make setup-service${NC} - Enable daily updates"
	@echo "4. ${GREEN}muralis --help${NC}    - See all options"
	@echo ""
	@echo "${BLUE}For development:${NC}"
	@echo "   ${GREEN}make dev${NC}          - Setup development environment"
	@echo "   ${GREEN}make test${NC}         - Run tests"
	@echo "   ${GREEN}make format${NC}       - Format code"

# Provider-specific runs
bing:
	@muralis --once --provider bing

nasa:
	@muralis --once --provider nasa

unsplash:
	@muralis --once --provider unsplash

wallhaven:
	@muralis --once --provider wallhaven

# Status
status:
	@echo "${BLUE}Muralis Status${NC}"
	@echo "═══════════════════════════════════"
	@echo -n "Installation: "; test -f ~/.local/bin/muralis && echo "${GREEN}✓${NC}" || echo "${RED}✗${NC}"
	@echo -n "Configuration: "; test -f ~/.config/muralis/config.ini && echo "${GREEN}✓${NC}" || echo "${YELLOW}⚠${NC}"
	@echo -n "Storage: "; test -d ~/Pictures/Muralis && echo "${GREEN}✓${NC}" || echo "${YELLOW}⚠${NC}"
	@echo -n "Systemd Timer: "; systemctl --user is-active muralis.timer 2>/dev/null | grep -q active && echo "${GREEN}✓${NC}" || echo "${RED}✗${NC}"
	@echo ""
	@if test -d ~/Pictures/Muralis; then \
		count=$$(ls -1 ~/Pictures/Muralis/muralis_*.jpg 2>/dev/null | wc -l); \
		echo "Saved wallpapers: $$count"; \
	fi

test:
	@echo "Running all tests..."
	@pytest tests/ -v --tb=short

test-unit:
	@echo "Running unit tests..."
	@pytest tests/unit/ -v

test-integration:
	@echo "Running integration tests..."
	@pytest tests/integration/ -v

test-coverage:
	@echo "Running tests with coverage..."
	@pytest tests/ --cov=muralis --cov-report=html --cov-report=term
	@echo "Coverage report: htmlcov/index.html"

test-quick:
	@echo "Running quick tests..."
	@pytest tests/ -v -m "not slow"

test-slow:
	@echo "Running slow tests..."
	@pytest tests/ -v -m slow

test-verbose:
	@echo "Running tests with verbose output..."
	@pytest tests/ -v --tb=long -s

test-watch:
	@echo "Watching for changes..."
	@pytest-watch -- -v

test-failed:
	@echo "Re-running failed tests..."
	@pytest --lf -v

# Help alias
default: help