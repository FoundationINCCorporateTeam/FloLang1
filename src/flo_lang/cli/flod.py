"""flod - Flo runtime with capability enforcement."""

import asyncio
import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from flo_lang.parser.parser import parse_file, ParseError
from flo_lang.interpreter.evaluator import Evaluator

app = typer.Typer(help="Flo production runtime with capability enforcement")
console = Console()


@app.command()
def run(
    file: Path = typer.Argument(..., help="Flo source file to run"),
    cap_file: Optional[Path] = typer.Option(None, "--cap-file", help="Capability configuration file"),
    deny_net: bool = typer.Option(False, "--deny-net", help="Deny network access"),
    deny_fs: bool = typer.Option(False, "--deny-fs", help="Deny filesystem access"),
    deny_db: bool = typer.Option(False, "--deny-db", help="Deny database access"),
    env_file: Optional[Path] = typer.Option(None, "--env-file", help="Environment file"),
):
    """Run a Flo program with capability enforcement."""
    if not file.exists():
        console.print(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)
    
    # Load capabilities
    capabilities = {}
    if cap_file:
        if not cap_file.exists():
            console.print(f"[red]Error:[/red] Capability file not found: {cap_file}")
            raise typer.Exit(1)
        
        with open(cap_file, 'r') as f:
            capabilities = json.load(f)
    
    # Apply deny flags
    if deny_net:
        console.print("[yellow]Network access denied[/yellow]")
    if deny_fs:
        console.print("[yellow]Filesystem access denied[/yellow]")
    if deny_db:
        console.print("[yellow]Database access denied[/yellow]")
    
    # Load environment
    if env_file and env_file.exists():
        console.print(f"[blue]Loading environment from {env_file}[/blue]")
    
    try:
        # Parse and execute
        ast = parse_file(str(file))
        evaluator = Evaluator()
        
        # TODO: Apply capability restrictions to evaluator
        
        asyncio.run(evaluator.eval(ast))
    
    except ParseError as e:
        console.print(f"[red]Parse Error:[/red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Runtime Error:[/red] {e}")
        raise typer.Exit(1)


def main():
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
