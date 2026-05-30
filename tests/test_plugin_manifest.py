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


def test_manifest_lists_four_skills(manifest):
    skills = manifest.get("skills", [])
    names = {s.get("name") for s in skills}
    assert names == {
        "azure-inventory",
        "azure-design",
        "azure-iac-author",
        "azure-migrate-runbook",
    }


def test_manifest_lists_four_commands(manifest):
    commands = manifest.get("commands", [])
    names = {c.get("name") for c in commands}
    assert names == {
        "azure-inventory",
        "azure-design",
        "azure-iac",
        "azure-runbook",
    }


def test_manifest_declares_prerequisite(manifest):
    prereqs = manifest.get("prerequisites", [])
    plugin_names = {p.get("plugin") for p in prereqs}
    assert "microsoft/azure-skills" in plugin_names
