# Contributing to Flo

Thank you for your interest in contributing to the Flo programming language! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Python 3.11 or higher
- Poetry (recommended) or pip
- Git
- Docker and Docker Compose (for integration tests)

### Setting Up Your Environment

1. **Fork and clone the repository**

```bash
git clone https://github.com/FoundationINCCorporateTeam/FloLang1.git
cd FloLang1
```

2. **Install dependencies**

Using Poetry (recommended):
```bash
pip install poetry
poetry install --with dev
poetry shell
```

Using pip:
```bash
pip install -e ".[dev]"
```

3. **Verify installation**

```bash
# Run tests
pytest

# Check linting
black --check src/ tests/
ruff check src/ tests/
mypy src/
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 2. Make Changes

- Write clean, readable code
- Follow the existing code style
- Add tests for new functionality
- Update documentation as needed

### 3. Run Tests and Linters

```bash
# Format code
black src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/

# Run tests
pytest

# Run with coverage
pytest --cov=src/flo_lang --cov-report=html --cov-report=term
```

### 4. Commit Changes

Use clear, descriptive commit messages:

```bash
git add .
git commit -m "Add feature: brief description"
```

Commit message format:
- `feat: Add new feature`
- `fix: Fix bug in module`
- `docs: Update documentation`
- `test: Add tests for feature`
- `refactor: Refactor code`
- `style: Format code`
- `chore: Update dependencies`

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub with:
- Clear title and description
- Reference to related issues
- Description of changes made
- Any breaking changes
- Screenshots (for UI changes)

## Code Style Guidelines

### Python Code

- **Formatting**: Use Black with 100 character line length
- **Linting**: Follow Ruff rules (E, F, W, I, N, UP, B, A, C4, PT, SIM)
- **Type Hints**: Add type hints to function signatures
- **Docstrings**: Use Google-style docstrings for public APIs

Example:

```python
from typing import Optional, List

def parse_file(path: str, encoding: str = "utf-8") -> Optional[AST]:
    """Parse a Flo source file.
    
    Args:
        path: Path to the .flo file
        encoding: File encoding (default: utf-8)
    
    Returns:
        Parsed AST or None if parsing fails
    
    Raises:
        FileNotFoundError: If file doesn't exist
        ParseError: If syntax is invalid
    """
    # Implementation
    pass
```

### Flo Code

- Use 2-space indentation
- Keep lines under 100 characters
- Use descriptive variable names
- Add comments for complex logic

Example:

```flo
# Good
fn calculate_total(items: List[Item]) -> float do
  let subtotal := items.sum(fn(item) do item.price end)
  let tax := subtotal * 0.08
  return subtotal + tax
end

# Avoid
fn calc(x) do
  let y := x.sum(fn(z) do z.p end)
  return y + y * 0.08
end
```

## Testing Guidelines

### Unit Tests

- Place tests in `tests/` directory matching source structure
- Use descriptive test names
- Test both success and failure cases
- Aim for high coverage (>80%)

Example:

```python
import pytest
from flo_lang.parser import parse

def test_parse_let_declaration():
    """Test parsing of let declarations."""
    source = "let x := 42"
    ast = parse(source)
    assert isinstance(ast.statements[0], LetDecl)
    assert ast.statements[0].name == "x"
    assert ast.statements[0].value.value == 42

def test_parse_invalid_syntax_raises_error():
    """Test that invalid syntax raises ParseError."""
    source = "let x ="  # Missing value
    with pytest.raises(ParseError):
        parse(source)
```

### Integration Tests

- Place in `tests/integration/`
- Use Docker Compose for external services
- Test end-to-end workflows
- Clean up resources after tests

Example:

```python
import pytest
from flo_lang.std.db import connect
from flo_lang.std.auth import signup

@pytest.mark.asyncio
async def test_signup_flow_with_database(postgres_container):
    """Test complete signup flow with real database."""
    conn = await connect({
        "adapter": "postgres",
        "host": "localhost",
        "port": postgres_container.port
    })
    
    result = await signup(
        {"db": conn},
        {"email": "test@example.com", "password": "secret123"}
    )
    
    assert result.is_ok()
    assert result.value.email == "test@example.com"
```

## Documentation Guidelines

### Code Documentation

- Add docstrings to all public functions, classes, and modules
- Use type hints
- Include examples in docstrings when helpful
- Keep documentation up-to-date with code changes

### User Documentation

- Update README.md for user-facing changes
- Update FLO_SPEC.md for language changes
- Add examples to demonstrate new features
- Keep quick start guide current

## Adding New Features

### Standard Library Modules

1. Create module directory in `src/flo_lang/std/`
2. Implement module with clear Python API
3. Add foreign function interface for Flo runtime
4. Write comprehensive tests
5. Document API in `docs/FLO_STD_<MODULE>.md`
6. Add examples to `samples/`

### Grammar Changes

1. Update `grammar/flo.lark`
2. Add corresponding AST nodes in `src/flo_lang/ast/nodes.py`
3. Update parser in `src/flo_lang/parser/parser.py`
4. Update interpreter to handle new nodes
5. Add parser tests (minimum 5 test cases)
6. Update FLO_SPEC.md
7. Add examples

### CLI Tools

1. Implement in `src/flo_lang/cli/`
2. Use Typer for CLI framework
3. Add comprehensive help text
4. Write tests for commands
5. Update README.md with usage examples

## Security Guidelines

### Security-Sensitive Code

When working with security-sensitive code:

- **Never commit secrets** (API keys, passwords, tokens)
- **Use AEAD encryption** for sensitive data
- **Use Argon2id** for password hashing
- **Validate all inputs** (SQL injection, XSS, etc.)
- **Follow principle of least privilege**
- **Document security assumptions**

### Reporting Security Issues

**DO NOT** open public issues for security vulnerabilities.

Email security@example.com with:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

## Review Process

### Pull Request Checklist

Before submitting a PR, ensure:

- [ ] All tests pass
- [ ] Code is formatted (black)
- [ ] Code is linted (ruff)
- [ ] Type checks pass (mypy)
- [ ] New code has tests
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated
- [ ] Commit messages are clear
- [ ] No merge conflicts

### Review Criteria

Reviewers will check:

- **Correctness**: Does the code work as intended?
- **Tests**: Are there adequate tests?
- **Security**: Are there security implications?
- **Performance**: Are there performance concerns?
- **Documentation**: Is it well-documented?
- **Style**: Does it follow code style?
- **Design**: Is it well-designed?

### Addressing Feedback

- Respond to all review comments
- Make requested changes
- Mark conversations as resolved
- Request re-review when ready

## Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Open a GitHub Issue with reproduction steps
- **Features**: Open a GitHub Issue with use case and proposal
- **Chat**: Join our Discord/Slack (TBD)

## Development Tips

### Running Parser Tests

```bash
pytest tests/test_parser.py -v
```

### Testing Specific Modules

```bash
pytest tests/std/test_auth.py -v -k test_signup
```

### Debugging

Use pytest with pdb:

```bash
pytest --pdb tests/test_parser.py
```

### Working with Grammar

After changing grammar:

```bash
# Test grammar immediately
python -c "from flo_lang.parser import parse; parse('let x := 42')"
```

### Integration Test Setup

```bash
# Start services
docker-compose -f scripts/docker-compose.yml up -d

# Run integration tests
pytest tests/integration/

# Stop services
docker-compose -f scripts/docker-compose.yml down
```

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers
- Accept constructive criticism
- Focus on what's best for the community
- Show empathy

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or insulting comments
- Personal or political attacks
- Publishing private information
- Other unprofessional conduct

### Enforcement

Violations may result in:
- Warning
- Temporary ban
- Permanent ban

Report issues to conduct@example.com

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (TBD).

## Questions?

Feel free to ask questions by:
- Opening a GitHub Discussion
- Commenting on relevant issues
- Reaching out to maintainers

Thank you for contributing to Flo! 🚀
