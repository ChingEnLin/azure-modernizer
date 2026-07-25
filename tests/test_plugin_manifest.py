import json
import pytest


@pytest.fixture
def manifest(repo_root):
    return json.loads((repo_root / "plugin.json").read_text())


def test_manifest_has_name_and_version(manifest):
    assert manifest["name"] == "azure-modernizer"
    assert "version" in manifest


def test_manifest_lists_subagent(manifest):
    agents = manifest.get("agents", [])
    names = {a.get("name") for a in agents}
    assert "azure-modernizer" in names


def test_manifest_skills_match_skill_dirs(manifest, repo_root):
    names = {s.get("name") for s in manifest.get("skills", [])}
    dirs = {p.parent.name for p in (repo_root / "skills").glob("*/SKILL.md")}
    assert names == dirs


def test_manifest_commands_match_command_files(manifest, repo_root):
    names = {c.get("name") for c in manifest.get("commands", [])}
    files = {p.stem for p in (repo_root / "commands").glob("*.md")}
    assert names == files


def test_manifest_declares_prerequisite(manifest):
    prereqs = manifest.get("prerequisites", [])
    plugin_names = {p.get("plugin") for p in prereqs}
    assert "microsoft/azure-skills" in plugin_names
