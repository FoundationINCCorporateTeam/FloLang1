"""Environment and scoping for the Flo interpreter."""

from typing import Any, Dict, Optional


class Environment:
    """Variable environment with lexical scoping."""
    
    def __init__(self, parent: Optional['Environment'] = None):
        """Initialize environment.
        
        Args:
            parent: Parent environment for scoping
        """
        self.parent = parent
        self.bindings: Dict[str, Any] = {}
        self.mutable: Dict[str, bool] = {}  # Track which vars are mutable
    
    def define(self, name: str, value: Any, mutable: bool = False) -> None:
        """Define a new variable in this environment.
        
        Args:
            name: Variable name
            value: Variable value
            mutable: Whether variable can be reassigned
        
        Raises:
            RuntimeError: If variable already defined in this scope
        """
        if name in self.bindings:
            raise RuntimeError(f"Variable '{name}' already defined in this scope")
        
        self.bindings[name] = value
        self.mutable[name] = mutable
    
    def get(self, name: str) -> Any:
        """Get variable value.
        
        Args:
            name: Variable name
        
        Returns:
            Variable value
        
        Raises:
            RuntimeError: If variable not found
        """
        if name in self.bindings:
            return self.bindings[name]
        
        if self.parent:
            return self.parent.get(name)
        
        raise RuntimeError(f"Undefined variable '{name}'")
    
    def set(self, name: str, value: Any) -> None:
        """Set variable value (for mutable vars).
        
        Args:
            name: Variable name
            value: New value
        
        Raises:
            RuntimeError: If variable not found or not mutable
        """
        if name in self.bindings:
            if not self.mutable[name]:
                raise RuntimeError(f"Cannot reassign immutable variable '{name}'")
            self.bindings[name] = value
            return
        
        if self.parent:
            self.parent.set(name, value)
            return
        
        raise RuntimeError(f"Undefined variable '{name}'")
    
    def has(self, name: str) -> bool:
        """Check if variable exists.
        
        Args:
            name: Variable name
        
        Returns:
            True if variable exists
        """
        if name in self.bindings:
            return True
        
        if self.parent:
            return self.parent.has(name)
        
        return False
