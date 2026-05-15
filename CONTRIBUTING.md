# Contributing to Muralis

## Welcome

Welcome to the Muralis community! We appreciate your interest in improving this project.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic understanding of Linux desktop environments

### Setup Development Environment

```bash
git clone https://github.com/quoxiom/qutility-muralis.git
cd qutility-muralis
python -m venv venv
source venv/bin/activate
pip install -e [dev]
```

## How to Contribute

### Reporting Bugs

Before submitting a bug, please check the issue tracker. Use the following template:

```markdown
#### Summary
[Clear description of the bug]

#### Steps to Reproduce
1. Run `muralis --once`
2. Observe error...

#### Expected Behavior
[What should happen]

#### Actual Behavior
[What actually happens]

#### System Information
- OS: [Ubuntu 22.04]
- Python: [3.10.12]
- Muralis: [1.0.0]
- DE: [GNOME]
```

### Suggesting Enhancements

Open an issue with the feature request template.

### Code Style Guidelines

- Follow PEP 8
- Line length: 100 characters
- Use type hints
- Write docstrings for all public functions

#### Testing

```bash
make test      # Run all tests
make coverage  # Generate coverage report
make lint       # Check code style
make format     # Auto-format code
```

#### Commit Messages

Use conventional commits:

```bash
git commit -m "feat(providers): add Unsplash provider"
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`

#### Pull Request Process

1. Fork the repository
2. Create a feature branch

 ``bash
git checkout -b feature/your-feature
```

3. Make your changes
4. Run tests locally

```bash
make test
```

5. Push to your fork

```bash
git push origin feature/your-feature
```

6. Open a Pull Request

## Adding a New Provider

1. Create `src/muralis/providers/yourprovider.py`

2. Extend `WallpaperProvider` base class

3. Implement `name`, `get_daily_url`, `get_metadata`

4. Register in `__init__.py`

5. Add tests

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Contact

- GitHub: [Quoxiom](https://github.com/quoxiom)
- Email: contributors@quoxiom.com

---

**Thank you for contributing!** 🙊