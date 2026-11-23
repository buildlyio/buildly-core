# GitHub Copilot Instructions

> Repository-level instructions for GitHub Copilot and other AI assistants.

---

## General Guidelines

### Prefer Minimal Changes
- Make the smallest diff that solves the problem
- Don't refactor unrelated code
- Preserve existing formatting and patterns
- Only touch files directly relevant to the task

### Follow Existing Patterns
- Match the codebase's naming conventions
- Use established architectural patterns
- Respect existing abstractions
- Don't introduce new patterns without discussion

### Be Conservative
- When uncertain, ask or suggest options
- Prefer explicit over clever
- Avoid premature optimization
- Don't assume missing context

---

## High-Caution Areas

**Extra care required—suggest but don't auto-complete:**

### Authentication & Authorization
- Login/logout flows
- Session management
- Token handling
- Permission checks
- Role-based access control

### Billing & Payments
- Stripe integration
- Invoice generation
- Subscription logic
- Payment processing

### Security
- Input validation
- SQL query construction
- File uploads
- CORS configuration
- Secret handling
- Encryption/decryption

### Integrations
- Third-party API calls
- Webhook handlers
- External service connections
- OAuth flows

### Infrastructure
- Docker configurations
- CI/CD pipelines
- Environment variables
- Deployment scripts

---

## Code Generation

### Do
```python
# Clear, explicit code
def calculate_total(items: list[Item]) -> Decimal:
    """Calculate the total price of items."""
    return sum(item.price for item in items)
```

### Don't
```python
# Clever but unclear
calc = lambda x: sum(i.p for i in x)
```

---

## Testing

When generating code, also suggest:
- Relevant unit tests
- Edge case tests
- Integration tests if applicable

### Test Template
```python
def test_function_does_expected_thing():
    # Arrange
    input_data = ...
    expected = ...

    # Act
    result = function_under_test(input_data)

    # Assert
    assert result == expected
```

---

## Documentation

Suggest documentation updates when:
- Adding new functions or classes
- Changing public APIs
- Modifying configuration
- Updating dependencies

### Docstring Format
```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description of what the function does.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ExceptionType: When this happens
    """
```

---

## Commit Messages

Suggest commits in this format:
```
type(scope): brief description

- Detail about change
- Another detail

Work-Item: <ID>
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `style`

---

## Project Structure

```
src/           # Application source code
tests/         # Test files
ops/           # Operations and deployment (startup.sh, docker-compose.yml)
devdocs/       # Development documentation
.ai/           # AI agent configuration
.github/       # GitHub configuration
```

---

## Language-Specific

### Python
- Use type hints
- Follow PEP 8
- Prefer f-strings
- Use pathlib for paths
- Handle exceptions explicitly

### HTML/CSS
- Use semantic HTML
- Prefer CSS classes over inline styles
- Keep accessibility in mind

### Docker
- Use specific version tags
- Minimize layer count
- Don't run as root
- Production runs via Docker; local dev prefers running natively (`ops/startup.sh start`)
  and only falls back to `--docker` when that's not practical

---

## The Buildly Standard

Remember:
- **AI assists, humans own**
- Every change needs a work item
- Small, focused, reviewable diffs
- Tests and docs are not optional
- When in doubt, ask

---

*These instructions implement the [Buildly AI Engineering Standard](ops/standards/ai-engineering-standard.md).*
