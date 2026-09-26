from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv


def resolve_env_paths(base_dir: str | Path | None = None) -> list[Path]:
    """Return the env file locations to check, preferring the project folder and then its parent."""
    project_dir = Path(base_dir) if base_dir is not None else Path(__file__).resolve().parent.parent
    candidates = [project_dir / ".env"]
    parent_dir = project_dir.parent
    if parent_dir != project_dir:
        candidates.append(parent_dir / ".env")
    return list(dict.fromkeys(candidates))


def load_project_env(base_dir: str | Path | None = None) -> bool:
    """Load environment variables from the project .env and the shared parent .env if present."""
    loaded = False
    for env_path in resolve_env_paths(base_dir):
        if env_path.exists():
            loaded = load_dotenv(env_path, override=False) or loaded
    return loaded
