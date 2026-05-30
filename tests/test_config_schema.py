import json
import yaml
import pytest
from jsonschema import Draft202012Validator, ValidationError


@pytest.fixture
def validator(schema_path):
    schema = json.loads(schema_path.read_text())
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def _load_yaml(path):
    return yaml.safe_load(path.read_text())


def test_valid_config_passes(validator, fixtures_dir):
    config = _load_yaml(fixtures_dir / "config.valid.yaml")
    validator.validate(config)


def test_missing_subscription_id_fails(validator, fixtures_dir):
    config = _load_yaml(fixtures_dir / "config.missing-sub.yaml")
    with pytest.raises(ValidationError, match="subscription_id"):
        validator.validate(config)


def test_work_tracker_optional(validator, fixtures_dir):
    config = _load_yaml(fixtures_dir / "config.no-work-tracker.yaml")
    validator.validate(config)


def test_work_tracker_type_enum(validator):
    config = {
        "subscription_id": "00000000-0000-0000-0000-000000000000",
        "tenant_id": "00000000-0000-0000-0000-000000000000",
        "primary_region": "westeurope",
        "docs": {"spec_dir": "./infra", "decision_record_dir": "./infra/adr"},
        "work_tracker": {
            "type": "not_a_real_tracker",
            "project": "X",
            "epic_id": 1,
        },
    }
    with pytest.raises(ValidationError, match="not_a_real_tracker"):
        validator.validate(config)


def test_work_tracker_requires_project_when_set(validator):
    config = {
        "subscription_id": "00000000-0000-0000-0000-000000000000",
        "tenant_id": "00000000-0000-0000-0000-000000000000",
        "primary_region": "westeurope",
        "docs": {"spec_dir": "./infra", "decision_record_dir": "./infra/adr"},
        "work_tracker": {"type": "azure_devops"},
    }
    with pytest.raises(ValidationError, match="project"):
        validator.validate(config)
