# Flo Programming Language

**Flo** is a capability-based, async-first programming language designed for building secure, concurrent applications with built-in security primitives and a robust standard library.

## Features

- ✨ **Async-First**: Built on asyncio with lightweight concurrency (strands)
- 🔒 **Security by Default**: Capability-based security model, encrypted secrets, secure password handling
- 🎯 **Type Safety**: Strong typing with Option[T] and Result[T,E] for error handling
- 🚀 **Rich Standard Library**: HTTP, Database, Auth, AI, Email, Crypto modules
- 🛠️ **Comprehensive Tooling**: REPL, package manager (mn), runtime (flod)
- 📦 **Secure Package Management**: Encrypted secrets storage (.mnstor), dependency management

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/FoundationINCCorporateTeam/FloLang1.git
cd FloLang1

# Install dependencies (using Poetry)
pip install poetry
poetry install

# Or install with pip
pip install -e .
```

### Your First Flo Program

Create `hello.flo`:

```flo
# hello.flo
fn main() -> void do
  print("Hello, Flo!")
end

main()
```

Run it:

```bash
# Using flo command
flo run hello.flo

# Or using flod with capabilities
flod run hello.flo --cap-file caps.json
```

### Interactive REPL

```bash
florepl
```

```
Flo REPL v0.1.0
Type :help for help, :quit to exit

>>> let x := 42
42
>>> x * 2
84
>>> fn double(n: int) -> int do return n * 2 end
<function double>
>>> double(21)
42
>>> :quit
```

## Example: Web API with Auth

```flo
bind HTTP ::: std/http@^1.0 as HTTP
bind Auth ::: std/auth@^1.0 as Auth
bind DB ::: std/db@^1.0 as DB

request cap net as NetCap
request cap db as DBCap
request cap email as EmailCap

# Configure database
let db_config := {
  adapter: "postgres",
  host: "localhost",
  database: "myapp"
}
let conn := await DB.connect(db_config)

# Configure auth
Auth.configure({
  db_conn: conn,
  token_secret: Mnstor.get("JWT_SECRET"),
  jwt_algo: "HS256"
})

# Create HTTP app
let app := HTTP.app()

# Signup endpoint
app.route("/signup").post(fn(req) do
  let body := req.parse_json()
  
  attempt do
    let user := await Auth.signup({db: DBCap, email: EmailCap}, body)
    return HTTP.json(201, {ok: true, user: user})
  rescue err do
    return HTTP.json(400, {ok: false, error: err.message})
  end
end)

# Login endpoint
app.route("/login").post(fn(req) do
  let body := req.parse_json()
  
  let result := await Auth.login({db: DBCap}, body)
  match result do
    Ok(session) => HTTP.json(200, {ok: true, token: session.token})
    Err(err) => HTTP.json(401, {ok: false, error: err.message})
  end
end)

app.listen(8000)
```

## Documentation

- **[Language Specification](FLO_SPEC.md)** - Complete language reference
- **[Quick Start Guide](FLO_QUICKSTART.md)** - 10-minute tutorial
- **[Standard Library](docs/)** - API documentation for stdlib modules
  - [std/auth](docs/FLO_STD_AUTH.md) - Authentication & authorization
  - [std/db](docs/FLO_STD_DB.md) - Database access
  - [std/http](docs/FLO_STD_HTTP.md) - HTTP server & client
  - [std/ai](docs/FLO_STD_AI.md) - AI model integration
  - [std/email](docs/FLO_STD_EMAIL.md) - Email sending
  - [std/crypto](docs/FLO_STD_CRYPTO.md) - Cryptographic primitives
- **[Contributing](CONTRIBUTING.md)** - Development guidelines

## CLI Tools

### flo - Run Flo programs

```bash
flo run <file.flo>                    # Run a Flo file
flo test                              # Run tests
flo check <file.flo>                  # Type check
```

### florepl - Interactive REPL

```bash
florepl                               # Start REPL
florepl --history-file ~/.flo_history # With custom history
```

REPL commands:
- `:load <file>` - Load and execute a file
- `:ast <expr>` - Show AST for expression
- `:type <expr>` - Show type of expression
- `:help` - Show help
- `:quit` - Exit REPL

### flod - Production runtime

```bash
flod run <file.flo> --cap-file caps.json  # Run with capabilities
flod run <file.flo> --deny-net            # Deny network access
flod run <file.flo> --deny-fs             # Deny filesystem access
```

### mn - Package manager

```bash
mn init                               # Initialize project
mn add <package>@<version>            # Add dependency
mn install                            # Install dependencies
mn build                              # Build package
mn publish                            # Publish to registry

# Secrets management
mn mnstor create --out secrets.mnstor # Create encrypted secrets
mn mnstor read secrets.mnstor         # Read secrets
mn mnstor rotate secrets.mnstor       # Rotate encryption key
```

## Project Structure

```
FloLang1/
├── src/flo_lang/           # Core implementation
│   ├── cli/                # CLI tools (flo, florepl, mn, flod)
│   ├── parser/             # Parser and grammar
│   ├── ast/                # AST node definitions
│   ├── interpreter/        # Runtime and evaluator
│   ├── std/                # Standard library
│   │   ├── http/           # HTTP server & client
│   │   ├── db/             # Database adapters
│   │   ├── auth/           # Authentication
│   │   ├── crypto/         # Cryptographic primitives
│   │   ├── ai/             # AI integration
│   │   └── email/          # Email sending
│   └── mnstor/             # Encrypted secrets storage
├── grammar/                # Lark grammar files
├── samples/                # Sample applications
│   ├── hello/              # Hello world
│   ├── user-api/           # Auth demo
│   └── todo-app/           # CRUD demo
├── tests/                  # Test suite
├── docs/                   # Documentation
└── scripts/                # Build & deploy scripts
```

## Development

### Setup Development Environment

```bash
# Install dev dependencies
poetry install --with dev

# Or with pip
pip install -e ".[dev]"
```

### Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=src/flo_lang --cov-report=html

# Specific test file
pytest tests/test_parser.py

# Integration tests (requires Docker)
docker-compose -f scripts/docker-compose.yml up -d
pytest tests/integration/
```

### Linting and Formatting

```bash
# Format code
black src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/
```

### Run Sample Applications

```bash
# Hello world
flo run samples/hello/main.flo

# User API (with database)
cd samples/user-api
docker-compose up -d postgres smtp
flo run main.flo

# Todo app
cd samples/todo-app
flo run main.flo
```

## Security

Flo is designed with security as a core principle:

- **Capability Model**: Explicit permissions for sensitive operations (db, net, ai, email, etc.)
- **Encrypted Secrets**: .mnstor uses AES-256-GCM encryption with Argon2id key derivation
- **Secure Password Handling**: Argon2id with recommended parameters
- **JWT Security**: Short-lived tokens, secure signing algorithms
- **Input Validation**: SQL parameterization, XSS prevention
- **Network Security**: Domain allowlists, private IP blocking

**Security Policy**: Report security issues to security@example.com

## Testing

The project includes comprehensive test coverage:

- **Parser Tests**: ≥40 test cases covering all language constructs
- **Interpreter Tests**: Semantics, control flow, async/await, error handling
- **Standard Library Tests**: Unit tests for all stdlib modules
- **Integration Tests**: End-to-end tests with real databases, SMTP, etc.
- **Security Tests**: Encryption, password hashing, capability enforcement

Run the full test suite:

```bash
pytest --cov=src/flo_lang --cov-report=term --cov-report=html
```

## CI/CD

GitHub Actions CI pipeline:

- Code formatting (Black)
- Linting (Ruff)
- Type checking (mypy)
- Unit tests (pytest)
- Integration tests (Docker Compose)
- Coverage reporting

## Roadmap

- [ ] v0.1: Prototype implementation (current)
- [ ] v0.2: Bytecode compiler and VM
- [ ] v0.3: Static type checker
- [ ] v0.4: Package registry
- [ ] v1.0: Production-ready release

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

TBD (to be specified by Foundation INC Corporate Team)

## Acknowledgments

Built with:
- [Lark](https://github.com/lark-parser/lark) - Parser
- [FastAPI](https://fastapi.tiangolo.com/) - HTTP framework
- [Typer](https://typer.tiangolo.com/) - CLI framework
- [prompt_toolkit](https://python-prompt-toolkit.readthedocs.io/) - REPL
- [cryptography](https://cryptography.io/) - Cryptographic primitives
- [argon2-cffi](https://argon2-cffi.readthedocs.io/) - Password hashing

---

**Foundation INC Corporate Team** | [Website](https://example.com) | [Documentation](FLO_SPEC.md)
