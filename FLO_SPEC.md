# Flo Language Specification v0.1

## Overview

Flo is a capability-based, async-first programming language designed for building secure, concurrent applications. It combines immutable-by-default data structures, explicit async/await semantics, built-in security primitives, and a robust capability model for controlled resource access.

## Design Principles

1. **Security by Default**: Capability-based security model, encrypted secrets storage, secure password handling
2. **Async-First**: Built on asyncio primitives with lightweight concurrency (strands)
3. **Explicit over Implicit**: Clear syntax for side effects, capabilities, and state mutations
4. **Type Safety**: Strong typing with Option[T] and Result[T,E] for error handling
5. **Developer Experience**: Rich standard library, interactive REPL, comprehensive tooling

## Syntax and Grammar

### Comments

```flo
# Single-line comment
## Documentation comment
```

### Module System

Imports use the `bind` keyword with the `:::` operator:

```flo
bind Math ::: std/math@^1.0 as Math
bind HTTP ::: std/http@^1.0 as HTTP
bind DB ::: std/db@^1.0 as DB
bind Auth ::: std/auth@^1.0 as Auth
bind AI ::: std/ai@^1.0 as AI
bind Crypto ::: std/crypto@^1.0 as Crypto
bind Email ::: std/email@^1.0 as Email
```

### Variable Declarations

```flo
# Immutable binding (default)
let x := 42
let name := "Alice"

# Mutable variable
var counter := 0
counter = counter + 1

# Compile-time constant
const PI !:= 3.14159
const MAX_USERS !:= 1000
```

### Functions

```flo
# Function declaration
fn add(a: int, b: int) -> int do
  return a + b
end

# Anonymous function
let double := fn(x: int) -> int do
  return x * 2
end

# Multi-line function with implicit return
fn greet(name: string) -> string do
  "Hello, " + name + "!"
end

# Async function
fn fetch_user(id: int) -> User do
  let result := await DB.findOne(conn, "users", {id: id})
  match result do
    Some(user) => return user
    None => raise UserNotFound(id)
  end
end
```

### Types

**Primitive Types:**
- `int`: 64-bit signed integer
- `float`: 64-bit floating-point
- `string`: UTF-8 string
- `bool`: true/false
- `nil`: null value

**Collection Types:**
- `List[T]`: ordered collection
- `Map[K, V]`: key-value map
- `Set[T]`: unique values

**Algebraic Types:**
- `Option[T]`: Some(value) or None
- `Result[T, E]`: Ok(value) or Err(error)

**Type Annotations:**
```flo
let users: List[User] := []
let config: Map[string, any] := {}
fn process(data: Option[string]) -> Result[int, Error] do
  # ...
end
```

### Control Flow

**If/Elif/Else:**
```flo
if x > 0 do
  print("positive")
elif x < 0 do
  print("negative")
else
  print("zero")
end
```

**Match Expression:**
```flo
match value do
  Some(x) => print(x)
  None => print("no value")
end

match status_code do
  200 => "OK"
  404 => "Not Found"
  500 => "Server Error"
  _ => "Unknown"
end
```

**For Loop:**
```flo
for i in range(0, 10) do
  print(i)
end

for user in users do
  print(user.name)
end
```

**While Loop:**
```flo
var i := 0
while i < 10 do
  print(i)
  i = i + 1
end
```

### Error Handling

```flo
# Attempt/rescue/finally
attempt do
  let result := risky_operation()
  print(result)
rescue err do
  print("Error: " + err.message)
finally do
  cleanup()
end

# Result type
fn divide(a: int, b: int) -> Result[float, string] do
  if b == 0 do
    return Err("Division by zero")
  end
  return Ok(a / b)
end

let result := divide(10, 2)
match result do
  Ok(value) => print(value)
  Err(msg) => print("Error: " + msg)
end
```

### Concurrency (Strands)

Strands are lightweight async tasks built on asyncio:

```flo
# Spawn a strand
let handle := strand do
  await slow_operation()
  return result
end

# Wait for strand to complete
let result := await handle

# Multiple concurrent strands
let handles := []
for i in range(0, 10) do
  let h := strand do
    await process_item(i)
  end
  handles.push(h)
end

for h in handles do
  await h
end
```

### Capability Model

Resources require explicit capability requests:

```flo
# Request capabilities at module level
request cap db as DBCap
request cap net as NetCap
request cap ai as AICap
request cap email as EmailCap
request cap mnstor as MStoreCap

# Use capabilities in code
fn create_user(data: Map) -> Result[User, Error] do
  # DBCap is implicitly available due to request at top
  let result := await DB.insert(DBCap, "users", data)
  return result
end
```

**Available Capabilities:**
- `db`: Database access
- `net`: Network operations (HTTP client/server)
- `ai`: AI model access
- `email`: Email sending
- `mnstor`: Encrypted secrets storage access
- `fs`: Filesystem operations
- `env`: Environment variable access

### Pipeline Operators

```flo
# Forward pipeline (left to right)
let result := data
  |> validate
  |> transform
  |> save

# Backward pipeline (right to left)
let result := save <| transform <| validate <| data
```

### Optional Chaining

```flo
let email := user?.profile?.email

# Equivalent to:
let email := match user do
  Some(u) => match u.profile do
    Some(p) => p.email
    None => None
  end
  None => None
end
```

## Standard Library

### std/http

**Server:**
```flo
bind HTTP ::: std/http@^1.0 as HTTP
request cap net as NetCap

let app := HTTP.app()

app.route("/hello").get(fn(req) do
  return HTTP.json(200, {message: "Hello, World!"})
end)

app.route("/users/:id").get(fn(req) do
  let id := req.params.id
  let user := await DB.findOne(conn, "users", {id: id})
  match user do
    Some(u) => HTTP.json(200, u)
    None => HTTP.json(404, {error: "User not found"})
  end
end)

app.listen(8000)
```

**Client:**
```flo
let client := HTTP.client({timeout: 30, retries: 3})
let response := await client.get("https://api.example.com/data")

match response do
  Ok(resp) => print(resp.json())
  Err(err) => print("Request failed: " + err.message)
end
```

### std/db

**Connection:**
```flo
bind DB ::: std/db@^1.0 as DB
request cap db as DBCap

let config := {
  adapter: "postgres",
  host: "localhost",
  port: 5432,
  database: "myapp",
  user: "dbuser",
  password: Mnstor.get("DB_PASSWORD")
}

let conn := await DB.connect(config)
```

**Queries:**
```flo
# Find one
let user := await DB.findOne(conn, "users", {email: "alice@example.com"})

# Query with SQL
let users := await DB.query(conn, "SELECT * FROM users WHERE age > $1", [18])

# Insert
let new_user := await DB.insert(conn, "users", {
  email: "bob@example.com",
  name: "Bob",
  age: 25
})

# Update
await DB.update(conn, "users", {id: 1}, {age: 26})

# Transaction
let result := await DB.transaction(conn, fn(tx) do
  await DB.insert(tx, "users", user_data)
  await DB.insert(tx, "profiles", profile_data)
  return Ok("success")
end)
```

**Supported Adapters:**
- `inmemory`: In-memory storage (testing)
- `postgres`: PostgreSQL via asyncpg
- `mysql`: MySQL via aiomysql
- `mongo`: MongoDB via motor

### std/auth

**Configuration:**
```flo
bind Auth ::: std/auth@^1.0 as Auth
request cap db as DBCap
request cap email as EmailCap

Auth.configure({
  db_conn: conn,
  mailer: mailer,
  token_secret: Mnstor.get("JWT_SECRET"),
  jwt_algo: "HS256",
  token_ttls: {access: 900, refresh: 604800},
  password_kdf_params: {
    memory_cost: 65536,
    time_cost: 3,
    parallelism: 4
  }
})
```

**Signup:**
```flo
fn signup(req) -> HTTP.Response do
  let body := req.parse_json()
  
  attempt do
    let user := await Auth.signup({db: DBCap, email: EmailCap}, {
      email: body.email,
      password: body.password,
      name: body.name,
      custom_fields: {phone: body.phone}
    })
    
    return HTTP.json(201, {ok: true, user: user})
  rescue err do
    return HTTP.json(400, {ok: false, error: err.message})
  end
end
```

**Login:**
```flo
fn login(req) -> HTTP.Response do
  let body := req.parse_json()
  
  let result := await Auth.login({db: DBCap}, {
    email: body.email,
    password: body.password
  })
  
  match result do
    Ok(session) => HTTP.json(200, {
      ok: true,
      token: session.token,
      user: session.user
    })
    Err(err) => HTTP.json(401, {ok: false, error: err.message})
  end
end
```

**Email Verification:**
```flo
fn verify_email(req) -> HTTP.Response do
  let token := req.query.token
  
  let result := await Auth.verify_email({db: DBCap}, token)
  
  match result do
    Ok(user) => HTTP.json(200, {ok: true, message: "Email verified"})
    Err(err) => HTTP.json(400, {ok: false, error: err.message})
  end
end
```

**Password Reset:**
```flo
fn forgot_password(req) -> HTTP.Response do
  let body := req.parse_json()
  
  await Auth.forgot_password({db: DBCap, email: EmailCap}, body.email)
  return HTTP.json(200, {ok: true, message: "Reset email sent"})
end

fn reset_password(req) -> HTTP.Response do
  let body := req.parse_json()
  
  let result := await Auth.reset_password({db: DBCap}, {
    token: body.token,
    new_password: body.new_password
  })
  
  match result do
    Ok(_) => HTTP.json(200, {ok: true, message: "Password reset"})
    Err(err) => HTTP.json(400, {ok: false, error: err.message})
  end
end
```

### std/crypto

**Key Derivation:**
```flo
bind Crypto ::: std/crypto@^1.0 as Crypto

# Argon2id (recommended)
let hash := Crypto.argon2id_hash("password", {
  memory_cost: 65536,
  time_cost: 3,
  parallelism: 4
})

let valid := Crypto.argon2id_verify(hash, "password")

# PBKDF2 (fallback)
let hash := Crypto.pbkdf2_hash("password", {
  iterations: 100000,
  algorithm: "sha256"
})
```

**AEAD Encryption:**
```flo
# AES-256-GCM
let key := Crypto.random_bytes(32)
let nonce := Crypto.random_bytes(12)
let ciphertext := Crypto.aes_gcm_encrypt(key, nonce, plaintext, associated_data)
let plaintext := Crypto.aes_gcm_decrypt(key, nonce, ciphertext, associated_data)

# ChaCha20-Poly1305
let ciphertext := Crypto.chacha20_encrypt(key, nonce, plaintext, associated_data)
```

### std/ai

**Configuration:**
```flo
bind AI ::: std/ai@^1.0 as AI
request cap ai as AICap

AI.configure({
  provider: "openai",
  api_key: Mnstor.get("OPENAI_API_KEY"),
  base_url: "https://api.openai.com/v1"
})
```

**Text Generation:**
```flo
fn generate_bio(name: string) -> string do
  let result := await AI.generate("gpt-3.5-turbo", {
    messages: [
      {role: "system", content: "You are a helpful assistant"},
      {role: "user", content: "Write a short bio for " + name}
    ],
    temperature: 0.7,
    max_tokens: 100
  })
  
  match result do
    Ok(resp) => return resp.choices[0].message.content
    Err(err) => return "Failed to generate bio"
  end
end
```

**Streaming:**
```flo
fn stream_response() -> void do
  let stream := AI.stream("gpt-3.5-turbo", {
    messages: [{role: "user", content: "Tell me a story"}],
    stream: true
  })
  
  for chunk in stream do
    print(chunk.delta)
  end
end
```

**Custom Provider:**
```flo
AI.register_adapter("custom", {
  base_url: "https://my-llm.example.com",
  auth_header: "X-API-Key",
  api_key: Mnstor.get("CUSTOM_API_KEY"),
  request_mapping: {
    model: "$.model",
    prompt: "$.messages[*].content",
    temperature: "$.temperature"
  }
})
```

### std/email

**SMTP Client:**
```flo
bind Email ::: std/email@^1.0 as Email
request cap email as EmailCap

let mailer := Email.new({
  host: "smtp.example.com",
  port: 587,
  use_tls: true,
  username: "sender@example.com",
  password: Mnstor.get("SMTP_PASSWORD")
})

await mailer.send({
  to: ["recipient@example.com"],
  subject: "Welcome to Flo",
  text: "Welcome to our platform!",
  html: "<h1>Welcome to our platform!</h1>",
  attachments: [{
    filename: "welcome.pdf",
    content: file_data
  }]
})
```

## Package Management (mn)

### .mnproj Format

```yaml
name: my-app
version: 1.0.0
entry: src/main.flo
runtime: flo@0.1.0

dependencies:
  std/http: ^1.0.0
  std/db: ^1.0.0
  std/auth: ^1.0.0

scripts:
  dev: flod run src/main.flo --cap-file dev.caps.json
  test: flo test
  build: mn build

env:
  NODE_ENV: production

firewall:
  allowed_domains:
    - api.example.com
    - *.googleapis.com
  deny_private_ips: true
```

### Commands

```bash
# Initialize project
mn init

# Add dependency
mn add std/http@^1.0.0

# Install dependencies
mn install

# Build package
mn build

# Publish to registry
mn publish

# Database migrations
mn db migrate up
mn db migrate down
```

## Secrets Management (.mnstor)

### File Format

Encrypted envelope with AEAD:
```json
{
  "version": "1.0",
  "kdf": "argon2id",
  "kdf_params": {
    "memory_cost": 65536,
    "time_cost": 3,
    "parallelism": 4,
    "salt": "base64_encoded_salt"
  },
  "cipher": "aes-256-gcm",
  "nonce": "base64_encoded_nonce",
  "ciphertext": "base64_encoded_ciphertext",
  "tag": "base64_encoded_auth_tag"
}
```

### CLI Commands

```bash
# Create secrets store
mn mnstor create --out secrets.mnstor --prompt-password

# Read secrets
mn mnstor read secrets.mnstor --key-source=env:MN_KEY

# Rotate encryption key
mn mnstor rotate secrets.mnstor --new-key
```

### Programmatic Access

```flo
request cap mnstor as MStoreCap

let secrets := Mnstor.read("secrets.mnstor", {
  key_source: "env:MN_KEY"
})

let api_key := secrets.get("OPENAI_API_KEY")
```

## Runtime (flod)

### Capability File

```json
{
  "version": "1.0",
  "capabilities": {
    "db": {
      "enabled": true,
      "adapters": ["postgres", "inmemory"],
      "hosts": ["localhost", "db.example.com"]
    },
    "net": {
      "enabled": true,
      "allowed_domains": ["*.example.com", "api.openai.com"],
      "deny_private": false
    },
    "ai": {
      "enabled": true,
      "providers": ["openai", "custom"]
    },
    "email": {
      "enabled": true,
      "smtp_hosts": ["smtp.example.com"]
    },
    "mnstor": {
      "enabled": true,
      "files": ["./secrets.mnstor"]
    }
  }
}
```

### Running with flod

```bash
# Run with capabilities
flod run main.flo --cap-file prod.caps.json

# Deny network access
flod run main.flo --deny-net

# Deny filesystem access
flod run main.flo --deny-fs

# With environment file
flod run main.flo --cap-file caps.json --env-file .env
```

## REPL (florepl)

Interactive REPL with commands:

```
>>> let x := 42
42
>>> x * 2
84
>>> :load samples/hello/main.flo
Loaded samples/hello/main.flo
>>> :ast let x := 42
LetDecl(name='x', value=IntLiteral(42))
>>> :help
Available commands:
  :load <file>  - Load and execute a Flo file
  :ast <expr>   - Show AST for expression
  :type <expr>  - Show type of expression
  :help         - Show this help
  :quit         - Exit REPL
>>> :quit
```

## Operator Precedence

From highest to lowest:

1. Primary: `()`, `[]`, `.`, `?.`
2. Unary: `!`, `-`, `+`
3. Multiplicative: `*`, `/`, `%`
4. Additive: `+`, `-`
5. Relational: `<`, `>`, `<=`, `>=`
6. Equality: `==`, `!=`
7. Logical AND: `&&`
8. Logical OR: `||`
9. Pipeline: `|>`, `<|`
10. Assignment: `:=`, `=`

## Implementation Notes

### This Prototype (v0.1)

**Implementation Language:** Python 3.11+

**Parser:** Lark grammar parser

**Runtime:** AST-walking interpreter with asyncio

**Concurrency:** Strands implemented as asyncio tasks

**Security:**
- Argon2id for password hashing
- AES-256-GCM for .mnstor encryption
- Capability enforcement at runtime
- No secrets in code/repo

**Testing:**
- Parser: ≥40 test cases
- Unit tests for all stdlib modules
- Integration tests for sample apps
- CI with linting (black, ruff, mypy)

### Future Enhancements

- Bytecode compiler and VM
- JIT compilation
- Static type checking
- Advanced pattern matching
- Algebraic effects
- Tree-sitter grammar for editors
- Web-based REPL
- Package signature verification

## Grammar Summary

See `grammar/flo.lark` for complete parseable grammar.

Key constructs:
- Module imports: `bind NAME ::: PATH@VERSION as ALIAS`
- Variables: `let NAME := EXPR`, `var NAME := EXPR`, `const NAME !:= EXPR`
- Functions: `fn NAME(PARAMS) -> TYPE do BODY end`
- Control: `if`, `match`, `for`, `while`, `attempt/rescue/finally`
- Async: `await EXPR`, `strand do BODY end`
- Capabilities: `request cap NAME as TYPE`
- Operators: `|>`, `<|`, `?.`, `:::`, `:=`, `!:=`

## Security Considerations

1. **Capability Model**: All sensitive operations require explicit capability requests
2. **Secrets Storage**: .mnstor uses AEAD encryption with strong KDF
3. **Password Security**: Argon2id with recommended parameters
4. **Token Security**: JWT with secure signing, short-lived access tokens
5. **Network Security**: Domain allowlists, private IP blocking
6. **Input Validation**: SQL parameterization, XSS prevention, email validation
7. **Rate Limiting**: Login attempts, API calls
8. **Audit Logging**: Capability requests, auth events

## License

TBD (to be specified by Foundation INC Corporate Team)

## Contributing

See CONTRIBUTING.md for development setup and guidelines.
