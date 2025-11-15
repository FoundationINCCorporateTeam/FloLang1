"""Flo CLI - Main command-line interface for running Flo programs."""

import sys
import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.syntax import Syntax

from flo_lang.parser.parser import parse, parse_file, ParseError
from flo_lang.interpreter.evaluator import Evaluator
from flo_lang.ast.nodes import pretty_print

app = typer.Typer(help="Flo programming language CLI")
console = Console()


@app.command()
def run(
    file: Path = typer.Argument(..., help="Flo source file to run"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug output"),
):
    """Run a Flo program."""
    if not file.exists():
        console.print(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)
    
    try:
        # Parse the file
        if debug:
            console.print(f"[blue]Parsing {file}...[/blue]")
        
        ast = parse_file(str(file))
        
        if debug:
            console.print("[blue]AST:[/blue]")
            console.print(pretty_print(ast))
        
        # Execute
        if debug:
            console.print("[blue]Executing...[/blue]")
        
        evaluator = Evaluator()
        result = asyncio.run(evaluator.eval(ast))
        
        if debug and result is not None:
            console.print(f"[green]Result:[/green] {result}")
    
    except ParseError as e:
        console.print(f"[red]Parse Error:[/red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Runtime Error:[/red] {e}")
        if debug:
            import traceback
            traceback.print_exc()
        raise typer.Exit(1)


@app.command()
def check(
    file: Path = typer.Argument(..., help="Flo source file to check"),
):
    """Check Flo source for syntax errors."""
    if not file.exists():
        console.print(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)
    
    try:
        parse_file(str(file))
        console.print(f"[green]✓[/green] {file} - No syntax errors")
    except ParseError as e:
        console.print(f"[red]✗[/red] {file}")
        console.print(f"[red]Parse Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def ast(
    file: Path = typer.Argument(..., help="Flo source file"),
):
    """Display the AST for a Flo program."""
    if not file.exists():
        console.print(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)
    
    try:
        ast = parse_file(str(file))
        console.print(pretty_print(ast))
    except ParseError as e:
        console.print(f"[red]Parse Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def test():
    """Run tests in the current project."""
    console.print("[yellow]Test command not yet implemented[/yellow]")
    console.print("Use: pytest tests/")


def main():
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
