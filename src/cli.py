import typer
import os
import tempfile
import shutil
import re
import subprocess
from src.orchestrator import main

app = typer.Typer()

def is_github_url(path: str) -> bool:
    return bool(re.match(r"https://github.com/.+/.+", path))

@app.command()
def analyze(reference: str):
    """Analyze a codebase (local path or GitHub URL) and build the module graph."""
    repo_path = reference
    temp_dir = None
    if is_github_url(reference):
        temp_dir = tempfile.mkdtemp(prefix="meltano_repo_")
        print(f"Cloning {reference} to {temp_dir}...")
        subprocess.run(["git", "clone", reference, temp_dir], check=True)
        repo_path = temp_dir
    try:
        main(repo_path)
    finally:
        if temp_dir:
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    app()