"""AST Evaluator for the Flo interpreter.

This module implements the core interpreter logic by walking the AST
and evaluating expressions and statements.
"""

import asyncio
from typing import Any, List, Optional, Dict, Callable

from flo_lang.ast.nodes import *
from flo_lang.interpreter.environment import Environment


class FloFunction:
    """Represents a Flo function."""
    
    def __init__(self, name: str, params: List[Param], body: List[Statement], closure: Environment):
        """Initialize function.
        
        Args:
            name: Function name
            params: Function parameters
            body: Function body
            closure: Closure environment
        """
        self.name = name
        self.params = params
        self.body = body
        self.closure = closure
    
    def __repr__(self):
        return f"<function {self.name}>"


class FloStrand:
    """Represents an async strand (task)."""
    
    def __init__(self, task: asyncio.Task):
        """Initialize strand.
        
        Args:
            task: Asyncio task
        """
        self.task = task
    
    async def wait(self):
        """Wait for strand to complete."""
        return await self.task
    
    def __repr__(self):
        return f"<strand {id(self)}>"


class ReturnValue(Exception):
    """Exception used for early returns from functions."""
    
    def __init__(self, value: Any):
        """Initialize return value.
        
        Args:
            value: Return value
        """
        self.value = value


class FloRuntimeError(Exception):
    """Runtime error in Flo code."""
    pass


class Evaluator:
    """AST evaluator for Flo language."""
    
    def __init__(self):
        """Initialize evaluator."""
        self.global_env = Environment()
        self.setup_builtins()
    
    def setup_builtins(self):
        """Setup built-in functions and constants."""
        # Built-in functions
        self.global_env.define("print", lambda *args: print(*args))
        self.global_env.define("range", lambda start, end: range(start, end))
        self.global_env.define("len", lambda x: len(x))
        self.global_env.define("str", lambda x: str(x))
        self.global_env.define("int", lambda x: int(x))
        self.global_env.define("float", lambda x: float(x))
    
    async def eval(self, node: ASTNode, env: Optional[Environment] = None) -> Any:
        """Evaluate an AST node.
        
        Args:
            node: AST node to evaluate
            env: Environment for evaluation
        
        Returns:
            Result of evaluation
        
        Raises:
            FloRuntimeError: On runtime errors
        """
        if env is None:
            env = self.global_env
        
        # Module
        if isinstance(node, Module):
            return await self.eval_module(node, env)
        
        # Statements
        elif isinstance(node, LetDecl):
            return await self.eval_let_decl(node, env)
        elif isinstance(node, VarDecl):
            return await self.eval_var_decl(node, env)
        elif isinstance(node, ConstDecl):
            return await self.eval_const_decl(node, env)
        elif isinstance(node, FnDecl):
            return await self.eval_fn_decl(node, env)
        elif isinstance(node, ReturnStmt):
            return await self.eval_return_stmt(node, env)
        elif isinstance(node, ExprStmt):
            return await self.eval(node.expr, env)
        elif isinstance(node, Import):
            # TODO: Implement module imports
            return None
        elif isinstance(node, CapabilityRequest):
            # TODO: Implement capability requests
            return None
        
        # Expressions
        elif isinstance(node, IntLiteral):
            return node.value
        elif isinstance(node, FloatLiteral):
            return node.value
        elif isinstance(node, StringLiteral):
            return node.value
        elif isinstance(node, BoolLiteral):
            return node.value
        elif isinstance(node, NilLiteral):
            return None
        elif isinstance(node, VarRef):
            return env.get(node.name)
        elif isinstance(node, BinaryExpr):
            return await self.eval_binary_expr(node, env)
        elif isinstance(node, UnaryExpr):
            return await self.eval_unary_expr(node, env)
        elif isinstance(node, Assignment):
            return await self.eval_assignment(node, env)
        elif isinstance(node, Call):
            return await self.eval_call(node, env)
        elif isinstance(node, ListExpr):
            return await self.eval_list_expr(node, env)
        elif isinstance(node, MapExpr):
            return await self.eval_map_expr(node, env)
        elif isinstance(node, Index):
            return await self.eval_index(node, env)
        elif isinstance(node, Attr):
            return await self.eval_attr(node, env)
        elif isinstance(node, IfExpr):
            return await self.eval_if_expr(node, env)
        elif isinstance(node, MatchExpr):
            return await self.eval_match_expr(node, env)
        elif isinstance(node, ForExpr):
            return await self.eval_for_expr(node, env)
        elif isinstance(node, WhileExpr):
            return await self.eval_while_expr(node, env)
        elif isinstance(node, AttemptExpr):
            return await self.eval_attempt_expr(node, env)
        elif isinstance(node, FnExpr):
            return await self.eval_fn_expr(node, env)
        elif isinstance(node, StrandExpr):
            return await self.eval_strand_expr(node, env)
        elif isinstance(node, AwaitExpr):
            return await self.eval_await_expr(node, env)
        elif isinstance(node, OptionExpr):
            return await self.eval_option_expr(node, env)
        elif isinstance(node, ResultExpr):
            return await self.eval_result_expr(node, env)
        
        else:
            raise FloRuntimeError(f"Unknown node type: {type(node).__name__}")
    
    async def eval_module(self, node: Module, env: Environment) -> Any:
        """Evaluate module."""
        result = None
        for stmt in node.statements:
            result = await self.eval(stmt, env)
        return result
    
    async def eval_let_decl(self, node: LetDecl, env: Environment) -> None:
        """Evaluate let declaration."""
        value = await self.eval(node.value, env)
        env.define(node.name, value, mutable=False)
    
    async def eval_var_decl(self, node: VarDecl, env: Environment) -> None:
        """Evaluate var declaration."""
        value = await self.eval(node.value, env)
        env.define(node.name, value, mutable=True)
    
    async def eval_const_decl(self, node: ConstDecl, env: Environment) -> None:
        """Evaluate const declaration."""
        value = await self.eval(node.value, env)
        env.define(node.name, value, mutable=False)
    
    async def eval_fn_decl(self, node: FnDecl, env: Environment) -> None:
        """Evaluate function declaration."""
        func = FloFunction(node.name, node.params, node.body, env)
        env.define(node.name, func, mutable=False)
    
    async def eval_return_stmt(self, node: ReturnStmt, env: Environment) -> None:
        """Evaluate return statement."""
        value = await self.eval(node.value, env) if node.value else None
        raise ReturnValue(value)
    
    async def eval_binary_expr(self, node: BinaryExpr, env: Environment) -> Any:
        """Evaluate binary expression."""
        left = await self.eval(node.left, env)
        right = await self.eval(node.right, env)
        
        if node.op == BinaryOp.ADD:
            return left + right
        elif node.op == BinaryOp.SUB:
            return left - right
        elif node.op == BinaryOp.MUL:
            return left * right
        elif node.op == BinaryOp.DIV:
            return left / right
        elif node.op == BinaryOp.MOD:
            return left % right
        elif node.op == BinaryOp.EQ:
            return left == right
        elif node.op == BinaryOp.NEQ:
            return left != right
        elif node.op == BinaryOp.LT:
            return left < right
        elif node.op == BinaryOp.GT:
            return left > right
        elif node.op == BinaryOp.LTE:
            return left <= right
        elif node.op == BinaryOp.GTE:
            return left >= right
        elif node.op == BinaryOp.AND:
            return left and right
        elif node.op == BinaryOp.OR:
            return left or right
        elif node.op == BinaryOp.PIPELINE_FORWARD:
            # left |> right means right(left)
            if callable(right):
                return await self.call_function(right, [left], env)
            raise FloRuntimeError("Right side of |> must be callable")
        elif node.op == BinaryOp.PIPELINE_BACKWARD:
            # left <| right means left(right)
            if callable(left):
                return await self.call_function(left, [right], env)
            raise FloRuntimeError("Left side of <| must be callable")
        else:
            raise FloRuntimeError(f"Unknown binary operator: {node.op}")
    
    async def eval_unary_expr(self, node: UnaryExpr, env: Environment) -> Any:
        """Evaluate unary expression."""
        expr = await self.eval(node.expr, env)
        
        if node.op == UnaryOp.NEG:
            return -expr
        elif node.op == UnaryOp.NOT:
            return not expr
        elif node.op == UnaryOp.POS:
            return +expr
        else:
            raise FloRuntimeError(f"Unknown unary operator: {node.op}")
    
    async def eval_assignment(self, node: Assignment, env: Environment) -> Any:
        """Evaluate assignment."""
        value = await self.eval(node.value, env)
        env.set(node.name, value)
        return value
    
    async def eval_call(self, node: Call, env: Environment) -> Any:
        """Evaluate function call."""
        func = await self.eval(node.func, env)
        args = [await self.eval(arg, env) for arg in node.args]
        return await self.call_function(func, args, env)
    
    async def call_function(self, func: Any, args: List[Any], env: Environment) -> Any:
        """Call a function with arguments."""
        if isinstance(func, FloFunction):
            # Create new environment for function
            func_env = Environment(parent=func.closure)
            
            # Bind parameters
            if len(args) != len(func.params):
                raise FloRuntimeError(
                    f"Function {func.name} expects {len(func.params)} arguments, got {len(args)}"
                )
            
            for param, arg in zip(func.params, args):
                func_env.define(param.name, arg, mutable=False)
            
            # Execute function body
            try:
                result = None
                for stmt in func.body:
                    result = await self.eval(stmt, func_env)
                return result
            except ReturnValue as ret:
                return ret.value
        
        elif callable(func):
            # Built-in Python function
            if asyncio.iscoroutinefunction(func):
                return await func(*args)
            return func(*args)
        
        else:
            raise FloRuntimeError(f"Not a function: {func}")
    
    async def eval_list_expr(self, node: ListExpr, env: Environment) -> List[Any]:
        """Evaluate list expression."""
        return [await self.eval(elem, env) for elem in node.elements]
    
    async def eval_map_expr(self, node: MapExpr, env: Environment) -> Dict[str, Any]:
        """Evaluate map expression."""
        result = {}
        for key, value_expr in node.entries:
            value = await self.eval(value_expr, env)
            result[key] = value
        return result
    
    async def eval_index(self, node: Index, env: Environment) -> Any:
        """Evaluate index expression."""
        obj = await self.eval(node.expr, env)
        index = await self.eval(node.index, env)
        return obj[index]
    
    async def eval_attr(self, node: Attr, env: Environment) -> Any:
        """Evaluate attribute access."""
        obj = await self.eval(node.expr, env)
        
        if isinstance(obj, dict):
            return obj.get(node.name)
        
        return getattr(obj, node.name)
    
    async def eval_if_expr(self, node: IfExpr, env: Environment) -> Any:
        """Evaluate if expression."""
        condition = await self.eval(node.condition, env)
        
        if condition:
            result = None
            for stmt in node.then_block:
                result = await self.eval(stmt, env)
            return result
        
        # Check elif clauses
        for elif_clause in node.elif_clauses:
            cond = await self.eval(elif_clause.condition, env)
            if cond:
                result = None
                for stmt in elif_clause.block:
                    result = await self.eval(stmt, env)
                return result
        
        # Else block
        if node.else_block:
            result = None
            for stmt in node.else_block:
                result = await self.eval(stmt, env)
            return result
        
        return None
    
    async def eval_match_expr(self, node: MatchExpr, env: Environment) -> Any:
        """Evaluate match expression."""
        value = await self.eval(node.expr, env)
        
        for arm in node.arms:
            if await self.match_pattern(arm.pattern, value, env):
                return await self.eval(arm.expr, env)
        
        raise FloRuntimeError(f"No match for value: {value}")
    
    async def match_pattern(self, pattern: Pattern, value: Any, env: Environment) -> bool:
        """Check if pattern matches value."""
        if isinstance(pattern, LiteralPattern):
            return pattern.value == value
        elif isinstance(pattern, VarPattern):
            env.define(pattern.name, value, mutable=False)
            return True
        elif isinstance(pattern, WildcardPattern):
            return True
        elif isinstance(pattern, OptionPattern):
            if pattern.variant == "None":
                return value is None
            elif pattern.variant == "Some":
                return value is not None
        elif isinstance(pattern, ResultPattern):
            # Simple implementation - can be enhanced
            return True
        else:
            return False
    
    async def eval_for_expr(self, node: ForExpr, env: Environment) -> Any:
        """Evaluate for expression."""
        iterable = await self.eval(node.iterable, env)
        
        result = None
        for item in iterable:
            # Create new environment for each iteration
            loop_env = Environment(parent=env)
            loop_env.define(node.var, item, mutable=False)
            
            for stmt in node.body:
                result = await self.eval(stmt, loop_env)
        
        return result
    
    async def eval_while_expr(self, node: WhileExpr, env: Environment) -> Any:
        """Evaluate while expression."""
        result = None
        
        while True:
            condition = await self.eval(node.condition, env)
            if not condition:
                break
            
            for stmt in node.body:
                result = await self.eval(stmt, env)
        
        return result
    
    async def eval_attempt_expr(self, node: AttemptExpr, env: Environment) -> Any:
        """Evaluate attempt expression."""
        try:
            result = None
            for stmt in node.body:
                result = await self.eval(stmt, env)
            return result
        except Exception as e:
            if node.rescue:
                rescue_env = Environment(parent=env)
                rescue_env.define(node.rescue.var, e, mutable=False)
                result = None
                for stmt in node.rescue.block:
                    result = await self.eval(stmt, rescue_env)
                return result
            raise
        finally:
            if node.finally_clause:
                for stmt in node.finally_clause.block:
                    await self.eval(stmt, env)
    
    async def eval_fn_expr(self, node: FnExpr, env: Environment) -> FloFunction:
        """Evaluate function expression."""
        return FloFunction("<lambda>", node.params, node.body, env)
    
    async def eval_strand_expr(self, node: StrandExpr, env: Environment) -> FloStrand:
        """Evaluate strand expression."""
        # Create new environment for strand to avoid conflicts
        strand_env = Environment(parent=env)
        
        async def strand_body():
            try:
                result = None
                for stmt in node.body:
                    result = await self.eval(stmt, strand_env)
                return result
            except ReturnValue as ret:
                # Handle return in strand like a function
                return ret.value
        
        task = asyncio.create_task(strand_body())
        return FloStrand(task)
    
    async def eval_await_expr(self, node: AwaitExpr, env: Environment) -> Any:
        """Evaluate await expression."""
        value = await self.eval(node.expr, env)
        
        if isinstance(value, FloStrand):
            return await value.wait()
        elif asyncio.iscoroutine(value) or asyncio.isfuture(value):
            return await value
        
        return value
    
    async def eval_option_expr(self, node: OptionExpr, env: Environment) -> Any:
        """Evaluate option expression."""
        if node.variant == "None":
            return None
        elif node.variant == "Some":
            return await self.eval(node.value, env)
    
    async def eval_result_expr(self, node: ResultExpr, env: Environment) -> Any:
        """Evaluate result expression."""
        # Simple implementation - returns tuple (ok, value)
        value = await self.eval(node.value, env)
        if node.variant == "Ok":
            return ("Ok", value)
        elif node.variant == "Err":
            return ("Err", value)


async def eval_module(source: str) -> Any:
    """Evaluate Flo source code.
    
    Args:
        source: Flo source code
    
    Returns:
        Result of evaluation
    """
    from flo_lang.parser.parser import parse
    
    ast = parse(source)
    evaluator = Evaluator()
    return await evaluator.eval(ast)


def run(source: str) -> Any:
    """Run Flo source code synchronously.
    
    Args:
        source: Flo source code
    
    Returns:
        Result of evaluation
    """
    return asyncio.run(eval_module(source))
