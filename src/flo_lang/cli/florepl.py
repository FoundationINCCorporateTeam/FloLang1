"""Flo REPL - Interactive Read-Eval-Print Loop."""

import asyncio
import sys
from typing import Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from rich.console import Console

from flo_lang.parser.parser import parse, ParseError
from flo_lang.interpreter.evaluator import Evaluator
from flo_lang.ast.nodes import pretty_print


console = Console()


class FloREPL:
    """Interactive REPL for Flo language."""
    
    def __init__(self, history_file: Optional[str] = None):
        """Initialize REPL.
        
        Args:
            history_file: Path to history file
        """
        self.evaluator = Evaluator()
        self.history_file = history_file or "~/.flo_history"
        self.session = PromptSession(
            history=FileHistory(self.history_file),
            auto_suggest=AutoSuggestFromHistory(),
        )
    
    async def eval_input(self, source: str) -> Optional[str]:
        """Evaluate user input.
        
        Args:
            source: Source code to evaluate
        
        Returns:
            Result string or None
        """
        try:
            # Try to parse as expression first
            ast = parse(source)
            result = await self.evaluator.eval(ast)
            
            if result is not None:
                return str(result)
            
            return None
        
        except ParseError as e:
            return f"Parse Error: {e}"
        except Exception as e:
            return f"Error: {e}"
    
    def handle_command(self, cmd: str) -> bool:
        """Handle REPL command.
        
        Args:
            cmd: Command string
        
        Returns:
            True if should continue, False to exit
        """
        if cmd == ":quit" or cmd == ":q":
            return False
        
        elif cmd == ":help" or cmd == ":h":
            console.print("""
[bold]Flo REPL Commands:[/bold]
  :help, :h         Show this help
  :quit, :q         Exit REPL
  :load <file>      Load and execute a file
  :ast <expr>       Show AST for expression
  :clear            Clear screen
            """)
        
        elif cmd == ":clear":
            console.clear()
        
        elif cmd.startswith(":load "):
            filename = cmd[6:].strip()
            try:
                with open(filename, 'r') as f:
                    source = f.read()
                result = asyncio.run(self.eval_input(source))
                if result:
                    console.print(result)
                console.print(f"[green]Loaded {filename}[/green]")
            except FileNotFoundError:
                console.print(f"[red]File not found: {filename}[/red]")
            except Exception as e:
                console.print(f"[red]Error loading file: {e}[/red]")
        
        elif cmd.startswith(":ast "):
            expr = cmd[5:].strip()
            try:
                ast = parse(expr)
                console.print(pretty_print(ast))
            except ParseError as e:
                console.print(f"[red]Parse Error: {e}[/red]")
        
        else:
            console.print(f"[yellow]Unknown command: {cmd}[/yellow]")
            console.print("Type :help for available commands")
        
        return True
    
    async def run(self):
        """Run the REPL."""
        console.print("[bold cyan]Flo REPL v0.1.0[/bold cyan]")
        console.print("Type :help for help, :quit to exit\n")
        
        while True:
            try:
                # Get input
                user_input = await asyncio.get_event_loop().run_in_executor(
                    None, 
                    lambda: self.session.prompt(">>> ")
                )
                
                # Skip empty input
                if not user_input.strip():
                    continue
                
                # Handle commands
                if user_input.startswith(":"):
                    if not self.handle_command(user_input):
                        break
                    continue
                
                # Evaluate expression
                result = await self.eval_input(user_input)
                if result:
                    console.print(result)
            
            except KeyboardInterrupt:
                console.print("\n[yellow]Use :quit to exit[/yellow]")
                continue
            
            except EOFError:
                break
            
            except Exception as e:
                console.print(f"[red]Unexpected error: {e}[/red]")


def main(history_file: Optional[str] = None):
    """Main entry point for REPL.
    
    Args:
        history_file: Path to history file
    """
    repl = FloREPL(history_file=history_file)
    
    try:
        asyncio.run(repl.run())
    except KeyboardInterrupt:
        pass
    
    console.print("\n[cyan]Goodbye![/cyan]")


if __name__ == "__main__":
    main()
