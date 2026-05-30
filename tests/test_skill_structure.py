import re
from pathlib import Path
import pytest
import yaml


REQUIRED_FRONTMATTER_KEYS = {"name", "description"}
REQUIRED_SKILL_SECTIONS = ["Trigger", "Inputs", "MCPs", "Procedure", "Outputs"]
REQUIRED_AGENT_SECTIONS = ["Identity", "Scope", "Ground rules", "Output emission"]


def _split_frontmatter(text: str):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    assert m, "missing YAML frontmatter delimited by ---"
    return yaml.safe_load(m.group(1)), m.group(2)


def _section_headers(body: str) -> list[str]:
    return [line.lstrip("# ").strip() for line in body.splitlines() if line.startswith("## ")]


def _check_markdown_file(path: Path, required_sections: list[str]):
    text = path.read_text()
    frontmatter, body = _split_frontmatter(text)
    missing_fm = REQUIRED_FRONTMATTER_KEYS - frontmatter.keys()
    assert not missing_fm, f"{path}: missing frontmatter keys: {missing_fm}"
    headers = _section_headers(body)
    missing = [s for s in required_sections if s not in headers]
    assert not missing, f"{path}: missing sections: {missing}"


def test_subagent_structure(repo_root):
    _check_markdown_file(
        repo_root / "agents" / "azure-modernizer.md",
        REQUIRED_AGENT_SECTIONS,
    )


@pytest.mark.parametrize(
    "skill_name",
    ["azure-inventory", "azure-design", "azure-iac-author", "azure-migrate-runbook"],
)
def test_skill_structure(repo_root, skill_name):
    _check_markdown_file(
        repo_root / "skills" / skill_name / "SKILL.md",
        REQUIRED_SKILL_SECTIONS,
    )
