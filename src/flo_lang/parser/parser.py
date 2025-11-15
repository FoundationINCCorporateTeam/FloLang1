"""Flo Language Parser using Lark.

This module provides the parser for the Flo programming language using Lark.
It transforms Flo source code into an AST.
"""

import os
from pathlib import Path
from typing import Optional, List

from lark import Lark, Transformer, Token, Tree
from lark.exceptions import LarkError, UnexpectedInput, UnexpectedCharacters

from flo_lang.ast.nodes import *


class ParseError(Exception):
    """Exception raised for parsing errors."""
    
    def __init__(self, message: str, line: int = 0, column: int = 0):
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column
    
    def __str__(self):
        if self.line > 0:
            return f"ParseError at line {self.line}, column {self.column}: {self.message}"
        return f"ParseError: {self.message}"


class FloTransformer(Transformer):
    """Transformer to convert Lark parse tree to Flo AST."""
    
    def module(self, items):
        """Transform module."""
        statements = [item for item in items if item is not None]
        return Module(statements=statements)
    
    # Imports
    def import_stmt(self, items):
        """Transform import statement."""
        name = str(items[0])
        path_info = items[1]
        alias = str(items[2]) if len(items) > 2 else None
        
        if isinstance(path_info, tuple):
            path, version = path_info
        else:
            path, version = path_info, None
        
        return Import(name=name, path=path, version=version, alias=alias)
    
    def import_path(self, items):
        """Transform import path."""
        path = str(items[0])
        version = str(items[1]) if len(items) > 1 else None
        return (path, version) if version else path
    
    # Capability requests
    def capability_req(self, items):
        """Transform capability request."""
        cap_name = str(items[0])
        type_name = str(items[1])
        return CapabilityRequest(capability=cap_name, type_name=type_name)
    
    # Declarations
    def const_decl(self, items):
        """Transform const declaration."""
        name = str(items[0])
        value = items[1]
        return ConstDecl(name=name, value=value)
    
    def let_decl(self, items):
        """Transform let declaration."""
        name = str(items[0])
        type_ann = None
        value_idx = 1
        
        if len(items) > 2:
            type_ann = items[1]
            value_idx = 2
        
        value = items[value_idx]
        return LetDecl(name=name, value=value, type_annotation=type_ann)
    
    def var_decl(self, items):
        """Transform var declaration."""
        name = str(items[0])
        type_ann = None
        value_idx = 1
        
        if len(items) > 2:
            type_ann = items[1]
            value_idx = 2
        
        value = items[value_idx]
        return VarDecl(name=name, value=value, type_annotation=type_ann)
    
    # Type annotations
    def type_annotation(self, items):
        """Transform type annotation."""
        return items[0]
    
    def simple_type(self, items):
        """Transform simple type."""
        return SimpleType(name=str(items[0]))
    
    def generic_type(self, items):
        """Transform generic type."""
        name = str(items[0])
        type_args = list(items[1:])
        return GenericType(name=name, type_args=type_args)
    
    def function_type(self, items):
        """Transform function type."""
        param_types = []
        return_type = None
        
        if len(items) > 0:
            if isinstance(items[0], list):
                param_types = items[0]
                if len(items) > 1:
                    return_type = items[1]
            else:
                return_type = items[0]
        
        return FunctionType(param_types=param_types, return_type=return_type)
    
    def type_list(self, items):
        """Transform type list."""
        return list(items)
    
    # Functions
    def fn_decl(self, items):
        """Transform function declaration."""
        name = str(items[0])
        params = []
        return_type = None
        body = []
        
        idx = 1
        # Check if we have params (list of Param objects)
        if idx < len(items) and isinstance(items[idx], list) and len(items[idx]) > 0 and isinstance(items[idx][0], Param):
            params = items[idx]
            idx += 1
        
        # Check if we have return type
        if idx < len(items) and isinstance(items[idx], TypeExpr):
            return_type = items[idx]
            idx += 1
        
        # Rest is the body
        if idx < len(items):
            body = items[idx] if isinstance(items[idx], list) else [items[idx]]
        
        return FnDecl(name=name, params=params, return_type=return_type, body=body)
    
    def param_list(self, items):
        """Transform parameter list."""
        return list(items)
    
    def param(self, items):
        """Transform parameter."""
        name = str(items[0])
        type_ann = items[1] if len(items) > 1 else None
        return Param(name=name, type_annotation=type_ann)
    
    def return_type(self, items):
        """Transform return type."""
        return items[0]
    
    def return_stmt(self, items):
        """Transform return statement."""
        value = items[0] if len(items) > 0 else None
        return ReturnStmt(value=value)
    
    def block(self, items):
        """Transform block."""
        return [item for item in items if item is not None]
    
    def expr_stmt(self, items):
        """Transform expression statement."""
        return ExprStmt(expr=items[0])
    
    # Expressions
    def assignment(self, items):
        """Transform assignment."""
        name = str(items[0])
        value = items[1]
        return Assignment(name=name, value=value)
    
    def pipeline_forward(self, items):
        """Transform forward pipeline."""
        left = items[0]
        right = items[1]
        return BinaryExpr(left=left, op=BinaryOp.PIPELINE_FORWARD, right=right)
    
    def pipeline_backward(self, items):
        """Transform backward pipeline."""
        left = items[0]
        right = items[1]
        return BinaryExpr(left=left, op=BinaryOp.PIPELINE_BACKWARD, right=right)
    
    def logical_or(self, items):
        """Transform logical OR."""
        left = items[0]
        right = items[1]
        return BinaryExpr(left=left, op=BinaryOp.OR, right=right)
    
    def logical_and(self, items):
        """Transform logical AND."""
        left = items[0]
        right = items[1]
        return BinaryExpr(left=left, op=BinaryOp.AND, right=right)
    
    def eq(self, items):
        """Transform equality."""
        return BinaryExpr(left=items[0], op=BinaryOp.EQ, right=items[1])
    
    def neq(self, items):
        """Transform inequality."""
        return BinaryExpr(left=items[0], op=BinaryOp.NEQ, right=items[1])
    
    def lt(self, items):
        """Transform less than."""
        return BinaryExpr(left=items[0], op=BinaryOp.LT, right=items[1])
    
    def gt(self, items):
        """Transform greater than."""
        return BinaryExpr(left=items[0], op=BinaryOp.GT, right=items[1])
    
    def lte(self, items):
        """Transform less than or equal."""
        return BinaryExpr(left=items[0], op=BinaryOp.LTE, right=items[1])
    
    def gte(self, items):
        """Transform greater than or equal."""
        return BinaryExpr(left=items[0], op=BinaryOp.GTE, right=items[1])
    
    def add(self, items):
        """Transform addition."""
        return BinaryExpr(left=items[0], op=BinaryOp.ADD, right=items[1])
    
    def sub(self, items):
        """Transform subtraction."""
        return BinaryExpr(left=items[0], op=BinaryOp.SUB, right=items[1])
    
    def mul(self, items):
        """Transform multiplication."""
        return BinaryExpr(left=items[0], op=BinaryOp.MUL, right=items[1])
    
    def div(self, items):
        """Transform division."""
        return BinaryExpr(left=items[0], op=BinaryOp.DIV, right=items[1])
    
    def mod(self, items):
        """Transform modulo."""
        return BinaryExpr(left=items[0], op=BinaryOp.MOD, right=items[1])
    
    def not_op(self, items):
        """Transform NOT."""
        return UnaryExpr(op=UnaryOp.NOT, expr=items[0])
    
    def neg(self, items):
        """Transform negation."""
        return UnaryExpr(op=UnaryOp.NEG, expr=items[0])
    
    def pos(self, items):
        """Transform positive."""
        return UnaryExpr(op=UnaryOp.POS, expr=items[0])
    
    def call(self, items):
        """Transform function call."""
        func = items[0]
        args = items[1] if len(items) > 1 else []
        return Call(func=func, args=args)
    
    def arg_list(self, items):
        """Transform argument list."""
        return list(items)
    
    def index(self, items):
        """Transform index expression."""
        return Index(expr=items[0], index=items[1])
    
    def attr(self, items):
        """Transform attribute access."""
        expr = items[0]
        name = str(items[1])
        return Attr(expr=expr, name=name)
    
    def optional_chain(self, items):
        """Transform optional chaining."""
        expr = items[0]
        name = str(items[1])
        return OptionalChain(expr=expr, name=name)
    
    def var_ref(self, items):
        """Transform variable reference."""
        return VarRef(name=str(items[0]))
    
    # Literals
    def int_lit(self, items):
        """Transform integer literal."""
        return IntLiteral(value=int(items[0]))
    
    def float_lit(self, items):
        """Transform float literal."""
        return FloatLiteral(value=float(items[0]))
    
    def string_lit(self, items):
        """Transform string literal."""
        value = str(items[0])
        # Remove quotes and handle escape sequences
        if value.startswith('"') or value.startswith("'"):
            value = value[1:-1]
        value = value.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"').replace("\\'", "'")
        return StringLiteral(value=value)
    
    def bool_true(self, items):
        """Transform boolean true."""
        return BoolLiteral(value=True)
    
    def bool_false(self, items):
        """Transform boolean false."""
        return BoolLiteral(value=False)
    
    def nil_lit(self, items):
        """Transform nil literal."""
        return NilLiteral()
    
    # Control flow
    def if_expr(self, items):
        """Transform if expression."""
        condition = items[0]
        then_block = items[1] if isinstance(items[1], list) else [items[1]]
        elif_clauses = []
        else_block = None
        
        idx = 2
        while idx < len(items):
            if isinstance(items[idx], ElifClause):
                elif_clauses.append(items[idx])
            elif isinstance(items[idx], list):
                else_block = items[idx]
            idx += 1
        
        return IfExpr(
            condition=condition,
            then_block=then_block,
            elif_clauses=elif_clauses,
            else_block=else_block
        )
    
    def elif_clause(self, items):
        """Transform elif clause."""
        condition = items[0]
        block = items[1] if isinstance(items[1], list) else [items[1]]
        return ElifClause(condition=condition, block=block)
    
    def else_clause(self, items):
        """Transform else clause."""
        return items[0] if isinstance(items[0], list) else [items[0]]
    
    def match_expr(self, items):
        """Transform match expression."""
        expr = items[0]
        arms = list(items[1:])
        return MatchExpr(expr=expr, arms=arms)
    
    def match_arm(self, items):
        """Transform match arm."""
        pattern = items[0]
        expr = items[1]
        return MatchArm(pattern=pattern, expr=expr)
    
    # Patterns
    def literal_pattern(self, items):
        """Transform literal pattern."""
        lit = items[0]
        if isinstance(lit, IntLiteral):
            return LiteralPattern(value=lit.value)
        elif isinstance(lit, FloatLiteral):
            return LiteralPattern(value=lit.value)
        elif isinstance(lit, StringLiteral):
            return LiteralPattern(value=lit.value)
        elif isinstance(lit, BoolLiteral):
            return LiteralPattern(value=lit.value)
        elif isinstance(lit, NilLiteral):
            return LiteralPattern(value=None)
        return LiteralPattern(value=None)
    
    def var_pattern(self, items):
        """Transform variable pattern."""
        return VarPattern(name=str(items[0]))
    
    def wildcard_pattern(self, items):
        """Transform wildcard pattern."""
        return WildcardPattern()
    
    def option_pattern(self, items):
        """Transform option pattern."""
        variant = str(items[0]) if len(items) > 0 and isinstance(items[0], Token) else "None"
        inner = items[1] if len(items) > 1 else None
        return OptionPattern(variant=variant, inner=inner)
    
    def result_pattern(self, items):
        """Transform result pattern."""
        variant = str(items[0]) if len(items) > 0 and isinstance(items[0], Token) else "Ok"
        inner = items[1] if len(items) > 1 else None
        return ResultPattern(variant=variant, inner=inner)
    
    def list_pattern(self, items):
        """Transform list pattern."""
        patterns = items[0] if len(items) > 0 and isinstance(items[0], list) else []
        return ListPattern(patterns=patterns)
    
    def pattern_list(self, items):
        """Transform pattern list."""
        return list(items)
    
    # Loops
    def for_expr(self, items):
        """Transform for expression."""
        var = str(items[0])
        iterable = items[1]
        body = items[2] if isinstance(items[2], list) else [items[2]]
        return ForExpr(var=var, iterable=iterable, body=body)
    
    def while_expr(self, items):
        """Transform while expression."""
        condition = items[0]
        body = items[1] if isinstance(items[1], list) else [items[1]]
        return WhileExpr(condition=condition, body=body)
    
    # Error handling
    def attempt_expr(self, items):
        """Transform attempt expression."""
        body = items[0] if isinstance(items[0], list) else [items[0]]
        rescue = None
        finally_clause = None
        
        for item in items[1:]:
            if isinstance(item, RescueClause):
                rescue = item
            elif isinstance(item, FinallyClause):
                finally_clause = item
        
        return AttemptExpr(body=body, rescue=rescue, finally_clause=finally_clause)
    
    def rescue_clause(self, items):
        """Transform rescue clause."""
        var = str(items[0])
        block = items[1] if isinstance(items[1], list) else [items[1]]
        return RescueClause(var=var, block=block)
    
    def finally_clause(self, items):
        """Transform finally clause."""
        block = items[0] if isinstance(items[0], list) else [items[0]]
        return FinallyClause(block=block)
    
    # Function expressions
    def fn_expr(self, items):
        """Transform function expression."""
        params = []
        return_type = None
        body = []
        
        idx = 0
        if idx < len(items) and isinstance(items[idx], list) and all(isinstance(p, Param) for p in items[idx]):
            params = items[idx]
            idx += 1
        
        if idx < len(items) and isinstance(items[idx], TypeExpr):
            return_type = items[idx]
            idx += 1
        
        if idx < len(items):
            body = items[idx] if isinstance(items[idx], list) else [items[idx]]
        
        return FnExpr(params=params, return_type=return_type, body=body)
    
    # Async/concurrency
    def strand_expr(self, items):
        """Transform strand expression."""
        body = items[0] if isinstance(items[0], list) else [items[0]]
        return StrandExpr(body=body)
    
    def await_expr(self, items):
        """Transform await expression."""
        return AwaitExpr(expr=items[0])
    
    # Collections
    def list_expr(self, items):
        """Transform list expression."""
        elements = items[0] if len(items) > 0 and isinstance(items[0], list) else []
        return ListExpr(elements=elements)
    
    def expr_list(self, items):
        """Transform expression list."""
        return list(items)
    
    def map_expr(self, items):
        """Transform map expression."""
        entries = items[0] if len(items) > 0 and isinstance(items[0], list) else []
        return MapExpr(entries=entries)
    
    def map_entry_list(self, items):
        """Transform map entry list."""
        return list(items)
    
    def map_entry(self, items):
        """Transform map entry."""
        key = str(items[0])
        if key.startswith('"') or key.startswith("'"):
            key = key[1:-1]
        value = items[1]
        return (key, value)
    
    # Option and Result
    def option_some(self, items):
        """Transform Some option."""
        return OptionExpr(variant="Some", value=items[0])
    
    def option_none(self, items):
        """Transform None option."""
        return OptionExpr(variant="None", value=None)
    
    def result_ok(self, items):
        """Transform Ok result."""
        return ResultExpr(variant="Ok", value=items[0])
    
    def result_err(self, items):
        """Transform Err result."""
        return ResultExpr(variant="Err", value=items[0])


# Load grammar file
# Path is relative to this parser.py file: parser.py -> flo_lang -> FloLang1 -> grammar
grammar_path = Path(__file__).parent.parent.parent.parent / "grammar" / "flo.lark"

if not grammar_path.exists():
    raise FileNotFoundError(f"Grammar file not found: {grammar_path}")

with open(grammar_path, 'r') as f:
    grammar_content = f.read()

# Create parser
_parser = Lark(
    grammar_content,
    start='module',
    parser='lalr',
    transformer=FloTransformer()
)


def parse(source: str) -> Module:
    """Parse Flo source code and return AST.
    
    Args:
        source: Flo source code as string
    
    Returns:
        Parsed Module AST
    
    Raises:
        ParseError: If source code has syntax errors
    """
    try:
        ast = _parser.parse(source)
        return ast
    except UnexpectedInput as e:
        raise ParseError(
            f"Unexpected input: {e.get_context(source)}",
            line=e.line,
            column=e.column
        )
    except UnexpectedCharacters as e:
        raise ParseError(
            f"Unexpected character: {e.char}",
            line=e.line,
            column=e.column
        )
    except LarkError as e:
        raise ParseError(str(e))


def parse_file(path: str) -> Module:
    """Parse Flo source file and return AST.
    
    Args:
        path: Path to .flo file
    
    Returns:
        Parsed Module AST
    
    Raises:
        FileNotFoundError: If file doesn't exist
        ParseError: If source code has syntax errors
    """
    with open(path, 'r', encoding='utf-8') as f:
        source = f.read()
    
    try:
        return parse(source)
    except ParseError as e:
        # Add filename to error message
        raise ParseError(f"In file {path}: {e.message}", e.line, e.column)
