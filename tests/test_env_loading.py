from pathlib import Path

from utils.env_loader import resolve_env_paths


def test_resolve_env_paths_includes_parent_and_project_dirs(tmp_path):
    project_dir = tmp_path / "code-reviewr-agent"
    project_dir.mkdir()
    parent_env = tmp_path / ".env"
    parent_env.write_text("OPENAI_API_KEY=parent-key\n", encoding="utf-8")

    env_paths = resolve_env_paths(project_dir)

    assert parent_env in env_paths
    assert project_dir / ".env" in env_paths
