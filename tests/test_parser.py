"""Comprehensive tests for the Flo parser.

Tests cover all language constructs including:
- Literals and basic expressions
- Variable declarations (let, var, const)
- Functions and closures
- Control flow (if, match, for, while)
- Error handling (attempt/rescue/finally)
- Async (strand, await)
- Collections (lists, maps)
- Option and Result types
- Operators and precedence
- Module system
"""

import pytest
from flo_lang.parser.parser import parse, ParseError
from flo_lang.ast.nodes import *


class TestLiterals:
    """Test parsing of literal values."""
    
    def test_integer_literal(self):
        ast = parse("42")
        assert isinstance(ast, Module)
        assert len(ast.statements) == 1
        expr_stmt = ast.statements[0]
        assert isinstance(expr_stmt, ExprStmt)
        assert isinstance(expr_stmt.expr, IntLiteral)
        assert expr_stmt.expr.value == 42
    
    def test_float_literal(self):
        ast = parse("3.14")
        expr_stmt = ast.statements[0]
        assert isinstance(expr_stmt.expr, FloatLiteral)
        assert expr_stmt.expr.value == 3.14
    
    def test_string_literal_double_quotes(self):
        ast = parse('"hello world"')
        expr_stmt = ast.statements[0]
        assert isinstance(expr_stmt.expr, StringLiteral)
        assert expr_stmt.expr.value == "hello world"
    
    def test_string_literal_single_quotes(self):
        ast = parse("'hello'")
        expr_stmt = ast.statements[0]
        assert isinstance(expr_stmt.expr, StringLiteral)
        assert expr_stmt.expr.value == "hello"
    
    def test_boolean_true(self):
        ast = parse("true")
        expr_stmt = ast.statements[0]
        assert isinstance(expr_stmt.expr, BoolLiteral)
        assert expr_stmt.expr.value is True
    
    def test_boolean_false(self):
        ast = parse("false")
        expr_stmt = ast.statements[0]
        assert isinstance(expr_stmt.expr, BoolLiteral)
        assert expr_stmt.expr.value is False
    
    def test_nil_literal(self):
        ast = parse("nil")
        expr_stmt = ast.statements[0]
        assert isinstance(expr_stmt.expr, NilLiteral)


class TestVariableDeclarations:
    """Test parsing of variable declarations."""
    
    def test_let_declaration(self):
        ast = parse("let x := 42")
        assert len(ast.statements) == 1
        let_decl = ast.statements[0]
        assert isinstance(let_decl, LetDecl)
        assert let_decl.name == "x"
        assert isinstance(let_decl.value, IntLiteral)
        assert let_decl.value.value == 42
    
    def test_var_declaration(self):
        ast = parse("var count := 0")
        var_decl = ast.statements[0]
        assert isinstance(var_decl, VarDecl)
        assert var_decl.name == "count"
        assert isinstance(var_decl.value, IntLiteral)
    
    def test_const_declaration(self):
        ast = parse("const PI !:= 3.14")
        const_decl = ast.statements[0]
        assert isinstance(const_decl, ConstDecl)
        assert const_decl.name == "PI"
        assert isinstance(const_decl.value, FloatLiteral)
    
    def test_let_with_type_annotation(self):
        ast = parse("let x: int := 42")
        let_decl = ast.statements[0]
        assert isinstance(let_decl, LetDecl)
        assert let_decl.type_annotation is not None
        assert isinstance(let_decl.type_annotation, SimpleType)
        assert let_decl.type_annotation.name == "int"


class TestBinaryOperators:
    """Test parsing of binary operators."""
    
    def test_addition(self):
        ast = parse("1 + 2")
        expr = ast.statements[0].expr
        assert isinstance(expr, BinaryExpr)
        assert expr.op == BinaryOp.ADD
        assert isinstance(expr.left, IntLiteral)
        assert isinstance(expr.right, IntLiteral)
    
    def test_subtraction(self):
        ast = parse("5 - 3")
        expr = ast.statements[0].expr
        assert isinstance(expr, BinaryExpr)
        assert expr.op == BinaryOp.SUB
    
    def test_multiplication(self):
        ast = parse("3 * 4")
        expr = ast.statements[0].expr
        assert isinstance(expr, BinaryExpr)
        assert expr.op == BinaryOp.MUL
    
    def test_division(self):
        ast = parse("10 / 2")
        expr = ast.statements[0].expr
        assert isinstance(expr, BinaryExpr)
        assert expr.op == BinaryOp.DIV
    
    def test_equality(self):
        ast = parse("x == y")
        expr = ast.statements[0].expr
        assert isinstance(expr, BinaryExpr)
        assert expr.op == BinaryOp.EQ
    
    def test_inequality(self):
        ast = parse("x != y")
        expr = ast.statements[0].expr
        assert isinstance(expr, BinaryExpr)
        assert expr.op == BinaryOp.NEQ
    
    def test_less_than(self):
        ast = parse("x < y")
        expr = ast.statements[0].expr
        assert expr.op == BinaryOp.LT
    
    def test_greater_than(self):
        ast = parse("x > y")
        expr = ast.statements[0].expr
        assert expr.op == BinaryOp.GT
    
    def test_logical_and(self):
        ast = parse("true && false")
        expr = ast.statements[0].expr
        assert expr.op == BinaryOp.AND
    
    def test_logical_or(self):
        ast = parse("true || false")
        expr = ast.statements[0].expr
        assert expr.op == BinaryOp.OR
    
    def test_operator_precedence(self):
        """Test that multiplication has higher precedence than addition."""
        ast = parse("1 + 2 * 3")
        expr = ast.statements[0].expr
        # Should be: 1 + (2 * 3)
        assert isinstance(expr, BinaryExpr)
        assert expr.op == BinaryOp.ADD
        assert isinstance(expr.right, BinaryExpr)
        assert expr.right.op == BinaryOp.MUL


class TestUnaryOperators:
    """Test parsing of unary operators."""
    
    def test_negation(self):
        ast = parse("-42")
        expr = ast.statements[0].expr
        assert isinstance(expr, UnaryExpr)
        assert expr.op == UnaryOp.NEG
        assert isinstance(expr.expr, IntLiteral)
    
    def test_logical_not(self):
        ast = parse("!true")
        expr = ast.statements[0].expr
        assert isinstance(expr, UnaryExpr)
        assert expr.op == UnaryOp.NOT


class TestFunctions:
    """Test parsing of functions."""
    
    def test_simple_function_declaration(self):
        source = """
fn add(a, b) do
  return a + b
end
"""
        ast = parse(source)
        fn_decl = ast.statements[0]
        assert isinstance(fn_decl, FnDecl)
        assert fn_decl.name == "add"
        assert len(fn_decl.params) == 2
        assert fn_decl.params[0].name == "a"
        assert fn_decl.params[1].name == "b"
    
    def test_function_with_typed_params(self):
        source = """
fn multiply(a: int, b: int) -> int do
  return a * b
end
"""
        ast = parse(source)
        fn_decl = ast.statements[0]
        assert isinstance(fn_decl, FnDecl)
        assert fn_decl.params[0].type_annotation is not None
        assert fn_decl.return_type is not None
    
    def test_function_call(self):
        ast = parse("add(1, 2)")
        expr = ast.statements[0].expr
        assert isinstance(expr, Call)
        assert isinstance(expr.func, VarRef)
        assert expr.func.name == "add"
        assert len(expr.args) == 2
    
    def test_anonymous_function(self):
        source = """
fn(x: int) -> int do
  return x * 2
end
"""
        ast = parse(source)
        expr = ast.statements[0].expr
        assert isinstance(expr, FnExpr)
        assert len(expr.params) == 1
        assert expr.params[0].name == "x"


class TestControlFlow:
    """Test parsing of control flow structures."""
    
    def test_if_expression(self):
        source = """
if x > 0 do
  print("positive")
end
"""
        ast = parse(source)
        expr = ast.statements[0].expr
        assert isinstance(expr, IfExpr)
        assert isinstance(expr.condition, BinaryExpr)
        assert len(expr.then_block) > 0
    
    def test_if_elif_else(self):
        source = """
if x > 0 do
  print("positive")
elif x < 0 do
  print("negative")
else do
  print("zero")
end
"""
        ast = parse(source)
        expr = ast.statements[0].expr
        assert isinstance(expr, IfExpr)
        assert len(expr.elif_clauses) == 1
        assert expr.else_block is not None
    
    def test_match_expression(self):
        source = """
match value do
  Some(x) => x
  None => 0
end
"""
        ast = parse(source)
        expr = ast.statements[0].expr
        assert isinstance(expr, MatchExpr)
        assert len(expr.arms) == 2
        assert isinstance(expr.arms[0].pattern, OptionPattern)
        assert isinstance(expr.arms[1].pattern, OptionPattern)
    
    def test_for_loop(self):
        source = """
for i in range(0, 10) do
  print(i)
end
"""
        ast = parse(source)
        expr = ast.statements[0].expr
        assert isinstance(expr, ForExpr)
        assert expr.var == "i"
        assert isinstance(expr.iterable, Call)
    
    def test_while_loop(self):
        source = """
while x < 10 do
  x = x + 1
end
"""
        ast = parse(source)
        expr = ast.statements[0].expr
        assert isinstance(expr, WhileExpr)
        assert isinstance(expr.condition, BinaryExpr)


class TestErrorHandling:
    """Test parsing of error handling constructs."""
    
    def test_attempt_rescue(self):
        source = """
attempt do
  risky_operation()
rescue err do
  print(err)
end
"""
        ast = parse(source)
        expr = ast.statements[0].expr
        assert isinstance(expr, AttemptExpr)
        assert expr.rescue is not None
        assert expr.rescue.var == "err"
    
    def test_attempt_rescue_finally(self):
        source = """
attempt do
  risky_operation()
rescue err do
  print(err)
finally do
  cleanup()
end
"""
        ast = parse(source)
        expr = ast.statements[0].expr
        assert isinstance(expr, AttemptExpr)
        assert expr.rescue is not None
        assert expr.finally_clause is not None


class TestAsync:
    """Test parsing of async constructs."""
    
    def test_strand_expression(self):
        source = """
strand do
  await slow_operation()
end
"""
        ast = parse(source)
        expr = ast.statements[0].expr
        assert isinstance(expr, StrandExpr)
        assert len(expr.body) > 0
    
    def test_await_expression(self):
        ast = parse("await fetch_data()")
        expr = ast.statements[0].expr
        assert isinstance(expr, AwaitExpr)
        assert isinstance(expr.expr, Call)


class TestCollections:
    """Test parsing of collection literals."""
    
    def test_empty_list(self):
        ast = parse("[]")
        expr = ast.statements[0].expr
        assert isinstance(expr, ListExpr)
        assert len(expr.elements) == 0
    
    def test_list_with_elements(self):
        ast = parse("[1, 2, 3]")
        expr = ast.statements[0].expr
        assert isinstance(expr, ListExpr)
        assert len(expr.elements) == 3
    
    def test_empty_map(self):
        ast = parse("{}")
        expr = ast.statements[0].expr
        assert isinstance(expr, MapExpr)
        assert len(expr.entries) == 0
    
    def test_map_with_entries(self):
        ast = parse('{name: "Alice", age: 30}')
        expr = ast.statements[0].expr
        assert isinstance(expr, MapExpr)
        assert len(expr.entries) == 2


class TestOptionAndResult:
    """Test parsing of Option and Result types."""
    
    def test_some_option(self):
        ast = parse("Some(42)")
        expr = ast.statements[0].expr
        assert isinstance(expr, OptionExpr)
        assert expr.variant == "Some"
        assert isinstance(expr.value, IntLiteral)
    
    def test_none_option(self):
        ast = parse("None")
        expr = ast.statements[0].expr
        assert isinstance(expr, OptionExpr)
        assert expr.variant == "None"
    
    def test_ok_result(self):
        ast = parse("Ok(42)")
        expr = ast.statements[0].expr
        assert isinstance(expr, ResultExpr)
        assert expr.variant == "Ok"
    
    def test_err_result(self):
        ast = parse('Err("error message")')
        expr = ast.statements[0].expr
        assert isinstance(expr, ResultExpr)
        assert expr.variant == "Err"


class TestModuleSystem:
    """Test parsing of imports and capabilities."""
    
    def test_import_statement(self):
        ast = parse("bind HTTP ::: std/http@^1.0 as HTTP")
        import_stmt = ast.statements[0]
        assert isinstance(import_stmt, Import)
        assert import_stmt.name == "HTTP"
        assert import_stmt.path == "std/http"
        assert import_stmt.version == "@^1.0"
        assert import_stmt.alias == "HTTP"
    
    def test_import_without_version(self):
        ast = parse("bind Math ::: std/math as Math")
        import_stmt = ast.statements[0]
        assert isinstance(import_stmt, Import)
        assert import_stmt.version is None
    
    def test_capability_request(self):
        ast = parse("request cap db as DBCap")
        cap_req = ast.statements[0]
        assert isinstance(cap_req, CapabilityRequest)
        assert cap_req.capability == "db"
        assert cap_req.type_name == "DBCap"


class TestOperators:
    """Test special operators."""
    
    def test_pipeline_forward(self):
        ast = parse("data |> transform")
        expr = ast.statements[0].expr
        assert isinstance(expr, BinaryExpr)
        assert expr.op == BinaryOp.PIPELINE_FORWARD
    
    def test_pipeline_backward(self):
        ast = parse("transform <| data")
        expr = ast.statements[0].expr
        assert isinstance(expr, BinaryExpr)
        assert expr.op == BinaryOp.PIPELINE_BACKWARD
    
    def test_attribute_access(self):
        ast = parse("user.name")
        expr = ast.statements[0].expr
        assert isinstance(expr, Attr)
        assert isinstance(expr.expr, VarRef)
        assert expr.name == "name"
    
    def test_optional_chaining(self):
        ast = parse("user?.email")
        expr = ast.statements[0].expr
        assert isinstance(expr, OptionalChain)
        assert expr.name == "email"
    
    def test_index_access(self):
        ast = parse("items[0]")
        expr = ast.statements[0].expr
        assert isinstance(expr, Index)


class TestComments:
    """Test that comments are ignored."""
    
    def test_single_line_comment(self):
        source = """
# This is a comment
let x := 42
"""
        ast = parse(source)
        assert len(ast.statements) == 1
        assert isinstance(ast.statements[0], LetDecl)
    
    def test_multiple_comments(self):
        source = """
# Comment 1
let x := 1
# Comment 2
let y := 2
# Comment 3
"""
        ast = parse(source)
        assert len(ast.statements) == 2


class TestComplexExpressions:
    """Test parsing of complex expressions."""
    
    def test_nested_function_calls(self):
        ast = parse("outer(inner(value))")
        expr = ast.statements[0].expr
        assert isinstance(expr, Call)
        assert isinstance(expr.args[0], Call)
    
    def test_chained_attribute_access(self):
        ast = parse("user.profile.email")
        expr = ast.statements[0].expr
        assert isinstance(expr, Attr)
        assert isinstance(expr.expr, Attr)
    
    def test_mixed_operators(self):
        ast = parse("x + y * z")
        expr = ast.statements[0].expr
        # Should parse as: x + (y * z)
        assert isinstance(expr, BinaryExpr)
        assert expr.op == BinaryOp.ADD


class TestErrorCases:
    """Test that invalid syntax raises errors."""
    
    def test_incomplete_let_declaration(self):
        with pytest.raises(ParseError):
            parse("let x =")
    
    def test_unclosed_function(self):
        with pytest.raises(ParseError):
            parse("fn test() do")
    
    def test_invalid_operator(self):
        with pytest.raises(ParseError):
            parse("x $ y")


class TestAssignment:
    """Test assignment expressions."""
    
    def test_simple_assignment(self):
        ast = parse("x = 42")
        expr = ast.statements[0].expr
        assert isinstance(expr, Assignment)
        assert expr.name == "x"
        assert isinstance(expr.value, IntLiteral)


class TestReturnStatement:
    """Test return statements."""
    
    def test_return_with_value(self):
        source = """
fn test() do
  return 42
end
"""
        ast = parse(source)
        fn_decl = ast.statements[0]
        return_stmt = fn_decl.body[0]
        assert isinstance(return_stmt, ReturnStmt)
        assert isinstance(return_stmt.value, IntLiteral)
    
    def test_return_without_value(self):
        source = """
fn test() do
  return
end
"""
        ast = parse(source)
        fn_decl = ast.statements[0]
        return_stmt = fn_decl.body[0]
        assert isinstance(return_stmt, ReturnStmt)
        assert return_stmt.value is None


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
