# Contributing to GPSkilledGuardian

Thank you for your interest in contributing to GPSkilledGuardian! This document provides guidelines for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other contributors

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in Issues
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)
   - Relevant logs or screenshots

### Suggesting Features

1. Check existing issues and discussions
2. Create a new issue with:
   - Clear feature description
   - Use case and benefits
   - Possible implementation approach
   - Any relevant examples

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes following the code style guidelines
4. Add tests for new functionality
5. Ensure all tests pass
6. Update documentation as needed
7. Commit with clear messages
8. Push to your fork
9. Create a Pull Request

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/NacktGem/GPSkilledGuardian.git
cd GPSkilledGuardian
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
pip install black flake8 mypy pytest pytest-asyncio pytest-cov
```

4. Set up pre-commit hooks (optional):
```bash
pip install pre-commit
pre-commit install
```

## Code Style Guidelines

### Python Code

- Follow PEP 8 style guide
- Use Black for code formatting: `black bot/ api/ config/`
- Use type hints where appropriate
- Maximum line length: 100 characters
- Use meaningful variable and function names
- Add docstrings to all functions, classes, and modules

### Example:

```python
"""Module description."""
from typing import Optional


def calculate_payment(amount: float, rate: float) -> Optional[float]:
    """Calculate payment amount.
    
    Args:
        amount: Base amount
        rate: Conversion rate
        
    Returns:
        Calculated payment or None if invalid
    """
    if amount <= 0 or rate <= 0:
        return None
    
    return amount * rate
```

### Imports

Order imports as:
1. Standard library imports
2. Third-party imports
3. Local application imports

Use absolute imports when possible.

### Async Code

- Use `async`/`await` consistently
- Don't block the event loop
- Use `asyncio.create_task()` for concurrent operations
- Properly handle exceptions in async code

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=bot --cov=api --cov-report=html

# Run specific test file
pytest tests/test_payments.py -v
```

### Writing Tests

- Write tests for all new features
- Aim for >80% code coverage
- Use descriptive test names
- Test edge cases and error conditions
- Use fixtures for common setup

Example:

```python
import pytest
from bot.utils.crypto_payments import CryptoRateConverter


@pytest.mark.asyncio
async def test_usd_to_btc_conversion():
    """Test USD to BTC conversion."""
    result = await CryptoRateConverter.usd_to_btc(100)
    assert result is None or result > 0
```

## Documentation

### Code Documentation

- Add docstrings to all public functions and classes
- Use Google-style docstrings
- Include type information in docstrings
- Document exceptions raised

### User Documentation

- Update README.md for user-facing changes
- Update SETUP.md for setup/deployment changes
- Update QUICKREF.md for new commands
- Add examples where helpful

## Commit Messages

Use clear, descriptive commit messages:

```
Add BTC payment validation

- Implement transaction hash verification
- Add confirmation count checking
- Update payment status based on confirmations
```

Format:
- First line: Brief summary (50 chars or less)
- Blank line
- Detailed description if needed
- List specific changes with bullet points

## Branch Naming

Use descriptive branch names:
- `feature/payment-validation` - New features
- `fix/webhook-timeout` - Bug fixes
- `docs/update-setup-guide` - Documentation
- `refactor/database-queries` - Code refactoring

## Review Process

### Before Submitting PR

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] No merge conflicts
- [ ] Commit messages are clear

### PR Description

Include:
- What changes were made
- Why the changes were needed
- How to test the changes
- Any breaking changes
- Screenshots (if UI changes)

### Review Criteria

PRs will be reviewed for:
- Code quality and style
- Test coverage
- Documentation completeness
- Security considerations
- Performance impact
- Breaking changes

## Areas for Contribution

### High Priority

- Additional payment methods
- Enhanced error handling
- Performance optimization
- Security improvements
- Test coverage increase

### Medium Priority

- UI/Dashboard development
- Additional moderation features
- Analytics and reporting
- Multi-language support
- Database migration tools

### Good First Issues

Look for issues labeled `good first issue` for beginner-friendly tasks:
- Documentation improvements
- Simple bug fixes
- Adding tests
- Code formatting
- Configuration updates

## Security

### Reporting Security Issues

**Do not** open public issues for security vulnerabilities.

Instead:
1. Email security details to the maintainers
2. Include steps to reproduce
3. Describe potential impact
4. Suggest fix if possible

### Security Guidelines

- Never commit secrets or credentials
- Use environment variables for sensitive data
- Validate all user input
- Use parameterized queries
- Follow OWASP guidelines
- Keep dependencies updated

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

- Check existing documentation
- Search closed issues
- Ask in Discussions
- Contact maintainers

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in relevant documentation

Thank you for contributing to GPSkilledGuardian! 🎉
