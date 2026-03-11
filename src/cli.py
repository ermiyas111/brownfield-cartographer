import typer
from src.orchestrator import main

app = typer.Typer()

@app.command()
def analyze(path: str):
    """Analyze a codebase and build the module graph."""
    main(path)

if __name__ == "__main__":
    app()