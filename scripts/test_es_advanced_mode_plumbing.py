"""Focused checks for EURSC advanced-mode normalization and filtering."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["PB_TESTING"] = "1"

from app import _generator_topic_options, _normalize_generator_mode, app  # noqa: E402
from generators.eursc.science_shared import bind_eursc_topic  # noqa: E402
from generators.shared.variant_utils import (  # noqa: E402
    MULTI_STEP_MODE,
    SITUATIONAL_MULTI_STEP_MODE,
    normalize_mode,
)
from topic_registry import (  # noqa: E402
    TOPIC_MODE_CAPABILITY_OVERRIDES,
    topic_mode_capabilities,
)


def _variant(name):
    def variant():
        return {"question": name}

    variant.__name__ = name
    return variant


def test_mode_aliases():
    assert normalize_mode("multi-step") == MULTI_STEP_MODE
    assert normalize_mode("multistep") == MULTI_STEP_MODE
    assert normalize_mode("situational") == SITUATIONAL_MULTI_STEP_MODE
    assert (
        normalize_mode("situational-multi-step")
        == SITUATIONAL_MULTI_STEP_MODE
    )


def test_bound_advanced_pools_are_isolated():
    lesson = _variant("lesson_item")
    standard = _variant("standard_item")
    multi = _variant("multi_item")
    situational = _variant("situational_item")
    generate, variants = bind_eursc_topic(
        "dummy",
        {"foundational": [lesson, standard]},
        {"foundational": ("standard_item",)},
        advanced_pools={
            MULTI_STEP_MODE: {"foundational": [multi]},
            SITUATIONAL_MULTI_STEP_MODE: {"foundational": [situational]},
        },
    )

    assert variants("foundational", "lesson") == [lesson, standard]
    assert variants("foundational", "standard") == [standard]
    assert variants("foundational", MULTI_STEP_MODE) == [multi]
    assert variants("foundational", SITUATIONAL_MULTI_STEP_MODE) == [situational]
    assert generate(
        "foundational", MULTI_STEP_MODE, variant_name="multi_item"
    ) == {"question": "multi_item"}
    try:
        generate(
            "foundational", MULTI_STEP_MODE, variant_name="standard_item"
        )
    except ValueError as exc:
        assert "Unknown multi_step variant" in str(exc)
    else:
        raise AssertionError("advanced mode leaked a standard variant")


def test_registry_and_app_filtering():
    key = ("eursc", "science", "healthy_living")
    assert topic_mode_capabilities(*key) == ("standard",)
    assert _normalize_generator_mode(*key, "mcq") == "standard"
    assert _normalize_generator_mode(*key, MULTI_STEP_MODE) == "standard"
    assert _normalize_generator_mode("gcse", "maths", "algebra", "mcq") == "mcq"
    assert (
        _normalize_generator_mode(
            "gcse", "maths", "algebra", SITUATIONAL_MULTI_STEP_MODE
        )
        == "standard"
    )

    TOPIC_MODE_CAPABILITY_OVERRIDES[key] = (
        "standard",
        MULTI_STEP_MODE,
        SITUATIONAL_MULTI_STEP_MODE,
    )
    try:
        assert _normalize_generator_mode(*key, MULTI_STEP_MODE) == MULTI_STEP_MODE
        assert (
            _normalize_generator_mode(*key, SITUATIONAL_MULTI_STEP_MODE)
            == SITUATIONAL_MULTI_STEP_MODE
        )
        row = next(
            item
            for item in _generator_topic_options()
            if (item["level"], item["subject"], item["slug"]) == key
        )
        assert row["modes"] == (
            "standard",
            MULTI_STEP_MODE,
            SITUATIONAL_MULTI_STEP_MODE,
        )
        with app.test_client() as client:
            html = client.get(
                "/?level=eursc&subject=science&topic=healthy_living"
                "&mode=multi_step"
            ).data.decode()
        assert 'data-modes="standard,multi_step,situational_multi_step"' in html
        assert 'option value="multi_step" selected' in html
    finally:
        TOPIC_MODE_CAPABILITY_OVERRIDES.pop(key, None)


def main():
    test_mode_aliases()
    test_bound_advanced_pools_are_isolated()
    test_registry_and_app_filtering()
    print("EURSC advanced-mode plumbing checks passed.")


if __name__ == "__main__":
    main()
