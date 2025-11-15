"""AST Node Definitions for Flo Language.

This module defines all AST node types used by the Flo parser and interpreter.
Uses dataclasses for clean, typed node definitions.
"""

from dataclasses import dataclass, field
from typing import Any, List, Optional, Union
from enum import Enum


class BinaryOp(Enum):
    """Binary operators."""
    ADD = "+"
    SUB = "-"
    MUL = "*"
    DIV = "/"
    MOD = "%"
    EQ = "=="
    NEQ = "!="
    LT = "<"
    GT = ">"
    LTE = "<="
    GTE = ">="
    AND = "&&"
    OR = "||"
    PIPELINE_FORWARD = "|>"
    PIPELINE_BACKWARD = "<|"


class UnaryOp(Enum):
    """Unary operators."""
    NOT = "!"
    NEG = "-"
    POS = "+"


# Base AST Node
class ASTNode:
    """Base class for all AST nodes."""
    def __init__(self):
        self.line: int = 0
        self.column: int = 0


# Module and Imports
@dataclass
class Module(ASTNode):
    """Root module node containing all statements."""
    statements: List['Statement'] = field(default_factory=list)


@dataclass
class Import(ASTNode):
    """Import statement: bind Name ::: path@version as Alias"""
    name: str
    path: str
    version: Optional[str] = None
    alias: Optional[str] = None


@dataclass
class CapabilityRequest(ASTNode):
    """Capability request: request cap name as Type"""
    capability: str
    type_name: str


# Type Annotations
@dataclass
class TypeExpr(ASTNode):
    """Base class for type expressions."""
    pass


@dataclass
class SimpleType(TypeExpr):
    """Simple type reference: int, string, etc."""
    name: str


@dataclass
class GenericType(TypeExpr):
    """Generic type: List[T], Map[K,V], etc."""
    name: str
    type_args: List[TypeExpr] = field(default_factory=list)


@dataclass
class FunctionType(TypeExpr):
    """Function type: fn(T1, T2) -> R"""
    param_types: List[TypeExpr] = field(default_factory=list)
    return_type: Optional[TypeExpr] = None


# Declarations
@dataclass
class Statement(ASTNode):
    """Base class for statements."""
    pass


@dataclass
class ConstDecl(Statement):
    """Constant declaration: const NAME !:= expr"""
    name: str
    value: 'Expr'
    type_annotation: Optional[TypeExpr] = None


@dataclass
class LetDecl(Statement):
    """Immutable variable declaration: let NAME := expr"""
    name: str
    value: 'Expr'
    type_annotation: Optional[TypeExpr] = None


@dataclass
class VarDecl(Statement):
    """Mutable variable declaration: var NAME := expr"""
    name: str
    value: 'Expr'
    type_annotation: Optional[TypeExpr] = None


@dataclass
class Param(ASTNode):
    """Function parameter."""
    name: str
    type_annotation: Optional[TypeExpr] = None


@dataclass
class FnDecl(Statement):
    """Function declaration: fn name(params) -> type do body end"""
    name: str
    params: List[Param] = field(default_factory=list)
    return_type: Optional[TypeExpr] = None
    body: List[Statement] = field(default_factory=list)


@dataclass
class ReturnStmt(Statement):
    """Return statement: return expr"""
    value: Optional['Expr'] = None


@dataclass
class ExprStmt(Statement):
    """Expression statement."""
    expr: 'Expr'


# Expressions
@dataclass
class Expr(ASTNode):
    """Base class for expressions."""
    pass


@dataclass
class IntLiteral(Expr):
    """Integer literal."""
    value: int


@dataclass
class FloatLiteral(Expr):
    """Float literal."""
    value: float


@dataclass
class StringLiteral(Expr):
    """String literal."""
    value: str


@dataclass
class BoolLiteral(Expr):
    """Boolean literal."""
    value: bool


@dataclass
class NilLiteral(Expr):
    """Nil literal."""
    pass


@dataclass
class VarRef(Expr):
    """Variable reference."""
    name: str


@dataclass
class BinaryExpr(Expr):
    """Binary expression: left op right"""
    left: Expr
    op: BinaryOp
    right: Expr


@dataclass
class UnaryExpr(Expr):
    """Unary expression: op expr"""
    op: UnaryOp
    expr: Expr


@dataclass
class Assignment(Expr):
    """Assignment: name = expr"""
    name: str
    value: Expr


@dataclass
class Call(Expr):
    """Function call: func(args)"""
    func: Expr
    args: List[Expr] = field(default_factory=list)


@dataclass
class Index(Expr):
    """Index expression: expr[index]"""
    expr: Expr
    index: Expr


@dataclass
class Attr(Expr):
    """Attribute access: expr.name"""
    expr: Expr
    name: str


@dataclass
class OptionalChain(Expr):
    """Optional chaining: expr?.name"""
    expr: Expr
    name: str


@dataclass
class ListExpr(Expr):
    """List literal: [expr, ...]"""
    elements: List[Expr] = field(default_factory=list)


@dataclass
class MapExpr(Expr):
    """Map literal: {key: value, ...}"""
    entries: List[tuple[str, Expr]] = field(default_factory=list)


# Control Flow
@dataclass
class IfExpr(Expr):
    """If expression: if cond do body elif ... else ... end"""
    condition: Expr
    then_block: List[Statement] = field(default_factory=list)
    elif_clauses: List['ElifClause'] = field(default_factory=list)
    else_block: Optional[List[Statement]] = None


@dataclass
class ElifClause(ASTNode):
    """Elif clause: elif cond do body"""
    condition: Expr
    block: List[Statement] = field(default_factory=list)


@dataclass
class Pattern(ASTNode):
    """Base class for patterns in match expressions."""
    pass


@dataclass
class LiteralPattern(Pattern):
    """Literal pattern in match."""
    value: Union[int, float, str, bool, None]


@dataclass
class VarPattern(Pattern):
    """Variable pattern in match."""
    name: str


@dataclass
class WildcardPattern(Pattern):
    """Wildcard pattern: _"""
    pass


@dataclass
class OptionPattern(Pattern):
    """Option pattern: Some(pattern) or None"""
    variant: str  # "Some" or "None"
    inner: Optional[Pattern] = None


@dataclass
class ResultPattern(Pattern):
    """Result pattern: Ok(pattern) or Err(pattern)"""
    variant: str  # "Ok" or "Err"
    inner: Optional[Pattern] = None


@dataclass
class ListPattern(Pattern):
    """List pattern: [pattern, ...]"""
    patterns: List[Pattern] = field(default_factory=list)


@dataclass
class MatchArm(ASTNode):
    """Match arm: pattern => expr"""
    pattern: Pattern
    expr: Expr


@dataclass
class MatchExpr(Expr):
    """Match expression: match expr do arms end"""
    expr: Expr
    arms: List[MatchArm] = field(default_factory=list)


@dataclass
class ForExpr(Expr):
    """For loop: for var in iterable do body end"""
    var: str
    iterable: Expr
    body: List[Statement] = field(default_factory=list)


@dataclass
class WhileExpr(Expr):
    """While loop: while cond do body end"""
    condition: Expr
    body: List[Statement] = field(default_factory=list)


@dataclass
class RescueClause(ASTNode):
    """Rescue clause: rescue err do body"""
    var: str
    block: List[Statement] = field(default_factory=list)


@dataclass
class FinallyClause(ASTNode):
    """Finally clause: finally do body"""
    block: List[Statement] = field(default_factory=list)


@dataclass
class AttemptExpr(Expr):
    """Attempt expression: attempt do body rescue ... finally ... end"""
    body: List[Statement] = field(default_factory=list)
    rescue: Optional[RescueClause] = None
    finally_clause: Optional[FinallyClause] = None


# Function Expressions
@dataclass
class FnExpr(Expr):
    """Anonymous function: fn(params) -> type do body end"""
    params: List[Param] = field(default_factory=list)
    return_type: Optional[TypeExpr] = None
    body: List[Statement] = field(default_factory=list)


# Async/Concurrency
@dataclass
class StrandExpr(Expr):
    """Strand expression: strand do body end"""
    body: List[Statement] = field(default_factory=list)


@dataclass
class AwaitExpr(Expr):
    """Await expression: await expr"""
    expr: Expr


# Option and Result
@dataclass
class OptionExpr(Expr):
    """Option expression: Some(expr) or None"""
    variant: str  # "Some" or "None"
    value: Optional[Expr] = None


@dataclass
class ResultExpr(Expr):
    """Result expression: Ok(expr) or Err(expr)"""
    variant: str  # "Ok" or "Err"
    value: Expr


# Type aliases for convenience
Statement = Union[
    Import,
    CapabilityRequest,
    ConstDecl,
    LetDecl,
    VarDecl,
    FnDecl,
    ReturnStmt,
    ExprStmt,
]


def pretty_print(node: ASTNode, indent: int = 0) -> str:
    """Pretty print an AST node for debugging."""
    prefix = "  " * indent
    
    if isinstance(node, Module):
        result = f"{prefix}Module:\n"
        for stmt in node.statements:
            result += pretty_print(stmt, indent + 1)
        return result
    
    elif isinstance(node, LetDecl):
        type_str = f": {node.type_annotation.name}" if node.type_annotation else ""
        result = f"{prefix}LetDecl({node.name}{type_str}):\n"
        result += pretty_print(node.value, indent + 1)
        return result
    
    elif isinstance(node, FnDecl):
        params_str = ", ".join(p.name for p in node.params)
        result = f"{prefix}FnDecl({node.name}({params_str})):\n"
        for stmt in node.body:
            result += pretty_print(stmt, indent + 1)
        return result
    
    elif isinstance(node, IntLiteral):
        return f"{prefix}IntLiteral({node.value})\n"
    
    elif isinstance(node, StringLiteral):
        return f"{prefix}StringLiteral(\"{node.value}\")\n"
    
    elif isinstance(node, BinaryExpr):
        result = f"{prefix}BinaryExpr({node.op.value}):\n"
        result += pretty_print(node.left, indent + 1)
        result += pretty_print(node.right, indent + 1)
        return result
    
    elif isinstance(node, Call):
        result = f"{prefix}Call:\n"
        result += pretty_print(node.func, indent + 1)
        for arg in node.args:
            result += pretty_print(arg, indent + 1)
        return result
    
    elif isinstance(node, VarRef):
        return f"{prefix}VarRef({node.name})\n"
    
    elif isinstance(node, ExprStmt):
        result = f"{prefix}ExprStmt:\n"
        result += pretty_print(node.expr, indent + 1)
        return result
    
    else:
        return f"{prefix}{node.__class__.__name__}\n"
