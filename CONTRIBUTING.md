# Contributing to Muralis

## Welcome

Welcome to the Muralis project! Thanks for your interest in improving this
small wallpaper utility.

## Getting started

### Prerequisites

- Python 3.9 or higher
- Git
- Basic understanding of Linux desktop environments

### Set up the development environment

```bash
git clone https://github.com/quoxiom/muralis.git
cd muralis
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
pytest tests/
```

## How to contribute

### Reporting bugs

Before submitting a bug, please check the issue tracker. Use this template:

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
- OS: [Ubuntu 24.04]
- Python: [3.12]
- Muralis: [0.4.0]
- DE: [GNOME]
```

### Suggesting enhancements

Open an issue with the feature request template.

### Code style

- Follow PEP 8
- Line length: 100 characters
- Use type hints
- Write docstrings for all public functions

#### Testing

```bash
make test       # run the test suite
make coverage   # generate a coverage report
make lint       # flake8
make format     # black
```

#### Commit messages

Use [conventional commits](https://www.conventionalcommits.org/):

```bash
git commit -m "feat(providers): add Unsplash provider"
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`

#### Pull request process

1. Fork the repository
2. Create a feature branch

   ```bash
   git checkout -b feature/your-feature
   ```

3. Make your changes and run the tests locally (`make test`)
4. Push to your fork

   ```bash
   git push origin feature/your-feature
   ```

5. Open a pull request

## Adding a new provider

1. Create `src/muralis/providers/yourprovider.py`.
2. Extend the `WallpaperProvider` base class and implement `name`,
   `get_daily_url`, and `get_metadata`.
3. Register the class in the provider registry at
   `src/muralis/providers/__init__.py` (the `PROVIDER_CLASSES` dict). The CLI,
   GUI and config all pick new providers up automatically from that single
   list.
4. Add tests under `tests/`.

## License

By contributing, you agree that your contributions will be licensed under the
MIT License.

## Contact

- GitHub: [Quoxiom](https://github.com/quoxiom)
- Project: [quoxiom/muralis](https://github.com/quoxiom/muralis)

---

**Thank you for contributing!** 🙌
