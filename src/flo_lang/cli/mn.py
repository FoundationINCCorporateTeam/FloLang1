"""mn - Flo package manager CLI."""

import typer
from rich.console import Console

app = typer.Typer(help="Flo package manager")
console = Console()


@app.command()
def init():
    """Initialize a new Flo project."""
    console.print("[yellow]mn init - Not yet implemented[/yellow]")
    console.print("This will create a new .mnproj file")


@app.command()
def add(package: str):
    """Add a dependency to the project.
    
    Args:
        package: Package name with version (e.g., std/http@^1.0)
    """
    console.print(f"[yellow]mn add {package} - Not yet implemented[/yellow]")


@app.command()
def install():
    """Install project dependencies."""
    console.print("[yellow]mn install - Not yet implemented[/yellow]")


@app.command()
def build():
    """Build the project."""
    console.print("[yellow]mn build - Not yet implemented[/yellow]")


@app.command()
def publish():
    """Publish package to registry."""
    console.print("[yellow]mn publish - Not yet implemented[/yellow]")


@app.command()
def mnstor():
    """Manage encrypted secrets storage."""
    console.print("[yellow]mn mnstor - Not yet implemented[/yellow]")
    console.print("Use for creating and managing .mnstor files")


def main():
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
