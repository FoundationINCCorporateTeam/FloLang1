"""Tests for the Flo interpreter."""

import pytest
import asyncio
from flo_lang.interpreter import run, eval_module
from flo_lang.parser.parser import parse


class TestBasicEvaluation:
    """Test basic expression evaluation."""
    
    def test_integer_literal(self):
        result = run("42")
        assert result == 42
    
    def test_float_literal(self):
        result = run("3.14")
        assert result == 3.14
    
    def test_string_literal(self):
        result = run('"hello"')
        assert result == "hello"
    
    def test_boolean_true(self):
        result = run("true")
        assert result is True
    
    def test_boolean_false(self):
        result = run("false")
        assert result is False


class TestArithmetic:
    """Test arithmetic operations."""
    
    def test_addition(self):
        result = run("2 + 3")
        assert result == 5
    
    def test_subtraction(self):
        result = run("10 - 3")
        assert result == 7
    
    def test_multiplication(self):
        result = run("4 * 5")
        assert result == 20
    
    def test_division(self):
        result = run("10 / 2")
        assert result == 5.0
    
    def test_operator_precedence(self):
        result = run("2 + 3 * 4")
        assert result == 14  # 2 + (3 * 4)


class TestVariables:
    """Test variable declarations."""
    
    def test_let_declaration(self):
        result = run("let x := 42\nx")
        assert result == 42
    
    def test_var_declaration(self):
        result = run("var x := 10\nx")
        assert result == 10
    
    def test_const_declaration(self):
        result = run("const PI !:= 3.14\nPI")
        assert result == 3.14
    
    def test_var_assignment(self):
        result = run("var x := 5\nx = 10\nx")
        assert result == 10


class TestFunctions:
    """Test function definitions and calls."""
    
    def test_simple_function(self):
        source = """
fn add(a, b) do
  return a + b
end

add(3, 4)
"""
        result = run(source)
        assert result == 7
    
    def test_recursive_function(self):
        source = """
fn factorial(n) do
  if n <= 1 do
    return 1
  end
  return n * factorial(n - 1)
end

factorial(5)
"""
        result = run(source)
        assert result == 120
    
    def test_closure(self):
        source = """
fn make_adder(x) do
  return fn(y) do
    return x + y
  end
end

let add5 := make_adder(5)
add5(3)
"""
        result = run(source)
        assert result == 8


class TestControlFlow:
    """Test control flow structures."""
    
    def test_if_expression(self):
        source = """
let x := 10
if x > 5 do
  42
end
"""
        result = run(source)
        assert result == 42
    
    def test_if_else(self):
        source = """
let x := 3
if x > 5 do
  1
else do
  2
end
"""
        result = run(source)
        assert result == 2


class TestLoops:
    """Test loop constructs."""
    
    def test_for_loop(self):
        source = """
var sum := 0
for i in range(1, 6) do
  sum = sum + i
end
sum
"""
        result = run(source)
        assert result == 15  # 1+2+3+4+5
    
    def test_while_loop(self):
        source = """
var count := 5
var sum := 0
while count > 0 do
  sum = sum + count
  count = count - 1
end
sum
"""
        result = run(source)
        assert result == 15  # 5+4+3+2+1


class TestCollections:
    """Test collection literals."""
    
    def test_list_creation(self):
        result = run("[1, 2, 3]")
        assert result == [1, 2, 3]
    
    def test_list_indexing(self):
        source = """
let list := [10, 20, 30]
list[1]
"""
        result = run(source)
        assert result == 20
    
    def test_map_creation(self):
        result = run('{name: "Alice", age: 30}')
        assert result == {"name": "Alice", "age": 30}
    
    def test_map_access(self):
        source = """
let person := {name: "Bob", age: 25}
person.name
"""
        result = run(source)
        assert result == "Bob"


class TestAsync:
    """Test async/await functionality."""
    
    def test_strand_await(self):
        source = """
let s := strand do
  return 42
end

await s
"""
        result = run(source)
        assert result == 42
    
    def test_multiple_strands(self):
        source = """
fn double(x) do
  return x * 2
end

let s1 := strand do
  return double(5)
end

let s2 := strand do
  return double(10)
end

let r1 := await s1
let r2 := await s2

r1 + r2
"""
        result = run(source)
        assert result == 30  # (5*2) + (10*2) = 10 + 20


class TestErrorHandling:
    """Test error handling."""
    
    def test_attempt_rescue(self):
        source = """
attempt do
  42
rescue err do
  0
end
"""
        result = run(source)
        assert result == 42


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
