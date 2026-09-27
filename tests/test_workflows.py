from pathlib import Path

import yaml

WORKFLOWS = sorted((Path(__file__).resolve().parent.parent / ".github" / "workflows").glob("*.yml"))


def test_workflows_are_valid_yaml_with_steps():
    assert WORKFLOWS
    for path in WORKFLOWS:
        doc = yaml.safe_load(path.read_text())
        for job in doc["jobs"].values():
            assert job["steps"], path.name


def test_collect_workflows_checkout_latest_head_and_own_data_dir():
    for path in WORKFLOWS:
        if not path.name.startswith("collect_"):
            continue
        domain = path.stem.removeprefix("collect_")
        for job in yaml.safe_load(path.read_text())["jobs"].values():
            checkout = next(s for s in job["steps"] if s.get("uses", "").startswith("actions/checkout"))
            assert checkout["with"]["ref"] == "${{ github.ref_name }}"
            assert f"data/{domain}" in checkout["with"]["sparse-checkout"]
