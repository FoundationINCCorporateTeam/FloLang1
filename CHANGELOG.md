# Changelog

All notable changes to the Flo programming language will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial prototype implementation (v0.1.0)
- Lark-based parser for Flo language
- AST-walking interpreter with asyncio support
- Standard library modules:
  - `std/http`: HTTP server (FastAPI) and client with middleware support
  - `std/db`: Database adapters (in-memory, Postgres, MySQL, MongoDB)
  - `std/auth`: Full authentication flows (signup, login, verify, reset) with Argon2id
  - `std/crypto`: KDF (Argon2id, PBKDF2) and AEAD (AES-256-GCM, ChaCha20-Poly1305)
  - `std/ai`: AI provider adapters (OpenAI, generic HTTP) with streaming support
  - `std/email`: SMTP client and dev SMTP server
- Secure encrypted secrets storage (.mnstor) with AEAD encryption
- CLI tools:
  - `flo`: Run Flo programs
  - `florepl`: Interactive REPL with prompt_toolkit
  - `mn`: Package manager (init, add, install, build, publish, mnstor commands)
  - `flod`: Production runtime with capability enforcement
- Capability-based security model with runtime enforcement
- Async concurrency with strands (asyncio tasks)
- Pattern matching with Option[T] and Result[T,E] types
- Sample applications:
  - `samples/hello`: Hello world example
  - `samples/user-api`: Full auth demo with DB and email
  - `samples/todo-app`: CRUD application example
- Comprehensive test suite:
  - Parser tests (≥40 test cases)
  - Interpreter tests (control flow, async, error handling)
  - Standard library unit tests
  - Integration tests with Docker Compose
- CI/CD pipeline with GitHub Actions:
  - Code formatting (Black)
  - Linting (Ruff)
  - Type checking (mypy)
  - Test execution with coverage
- Documentation:
  - Language specification (FLO_SPEC.md)
  - Quick start guide (FLO_QUICKSTART.md)
  - Standard library API docs
  - Contributing guidelines

### Changed
- N/A (initial release)

### Deprecated
- N/A (initial release)

### Removed
- N/A (initial release)

### Fixed
- N/A (initial release)

### Security
- Argon2id for password hashing with secure defaults
- AES-256-GCM for .mnstor encryption
- JWT token signing with configurable algorithms
- SQL parameterization to prevent injection
- Input validation and sanitization
- Capability enforcement for sensitive operations
- No secrets in repository or code

## [0.1.0] - 2024-01-XX (Prototype)

Initial prototype release of the Flo programming language.

### Core Language Features
- Immutable-by-default with `let`, mutable `var`, and compile-time `const`
- Functions with closures and return values
- Control flow: if/elif/else, match, for, while
- Error handling: attempt/rescue/finally
- Async/await with strand concurrency primitive
- Option[T] and Result[T,E] for type-safe error handling
- Pattern matching on algebraic types
- Pipeline operators (|>, <|)
- Optional chaining (?.)
- Module system with bind operator (:::)

### Runtime
- AST-walking interpreter
- Asyncio-based async execution
- Capability-based security enforcement
- Foreign function interface for stdlib

### Standard Library
- HTTP server and client
- Database access (Postgres, MySQL, MongoDB, in-memory)
- Authentication and authorization
- Cryptographic primitives
- AI model integration
- Email sending

### Tooling
- Interactive REPL
- Package manager (mn)
- Secure secrets storage (.mnstor)
- Production runtime (flod)

### Development
- Lark grammar parser
- Comprehensive test coverage
- Type checking with mypy
- Code formatting with black
- Linting with ruff
- CI/CD with GitHub Actions

---

**Note**: This is a prototype implementation. Production-ready features will be added in future releases.

## Version History

- **v0.1.0** - Initial prototype (current)
- **v0.2.0** - Planned: Bytecode compiler and VM
- **v0.3.0** - Planned: Static type checker
- **v0.4.0** - Planned: Package registry
- **v1.0.0** - Planned: Production-ready release
