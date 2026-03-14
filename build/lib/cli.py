import typer
import os
import tempfile
import shutil
import re
import subprocess
from src.orchestrator import main

def is_github_url(path: str) -> bool:
    return bool(re.match(r"https://github.com/.+/.+", path))

def analyze(
    reference: str = typer.Argument(..., help="Path to local repo or GitHub URL")
):
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
            shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    typer.run(analyze)