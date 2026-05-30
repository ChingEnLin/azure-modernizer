from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture
def skills_dir(repo_root: Path) -> Path:
    return repo_root / "skills"


@pytest.fixture
def schema_path(repo_root: Path) -> Path:
    return repo_root / "schema" / "config.schema.json"


@pytest.fixture
def fixtures_dir() -> Path:
    return Path(__file__).parent / "fixtures"
