"""Pilot-exit verification for EURSC advanced Practice modes.

Covers same-variant pinning, grader + part scores, fail-closed unsupported
cells, QOTD/lesson-pool isolation, HTML a11y on the three advanced surfaces,
and safeguarding spot-checks for the operational pilot topics.
"""
import os
import random
import re
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ["PB_TESTING"] = "1"
os.environ["MAIL_PROVIDER"] = "console"
os.environ.setdefault("SECRET_KEY", "pb-testing")

from app import (  # noqa: E402
    _normalize_generator_mode,
    _quicktest_answer_from_form,
    app,
)
from generators.eursc.s1_science_lab import eursc_science_measurement  # noqa: E402
from generators.eursc.s1_sports import eursc_science_movement  # noqa: E402
from generators.eursc.s2_health import eursc_science_infectious_disease  # noqa: E402
from generators.eursc.s3_machines import eursc_science_energy  # noqa: E402
from generators.eursc.science_shared import SYLLABUS_MODULES  # noqa: E402
from generators.shared.answer_checkers import (  # noqa: E402
    _parse_proof_steps_raw,
    check_number_fields,
)
from generators.shared.lesson_quiz import build_lesson_quiz  # noqa: E402
from generators.shared.variant_utils import (  # noqa: E402
    ADVANCED_MODES,
    MULTI_STEP_MODE,
    SITUATIONAL_MULTI_STEP_MODE,
)
from models.class_assignments import grade_frozen_answer  # noqa: E402
from models.qotd import get_daily_question, list_mcq_topic_paths  # noqa: E402
from topic_registry import TOPICS, topic_mode_capabilities  # noqa: E402

SCIENCE = TOPICS["eursc"]["science"]
DIFFS = ("foundational", "intermediate", "difficult")

PILOT_ENABLED = {
    "measurement": (MULTI_STEP_MODE,),
    "movement": (MULTI_STEP_MODE,),
    "infectious_disease": (SITUATIONAL_MULTI_STEP_MODE,),
    "energy": (SITUATIONAL_MULTI_STEP_MODE,),
}

S1_UNIT11_ENABLED = {
    "what_is_science": (MULTI_STEP_MODE, SITUATIONAL_MULTI_STEP_MODE),
    "measurement": (MULTI_STEP_MODE, SITUATIONAL_MULTI_STEP_MODE),
    "science_lab": (MULTI_STEP_MODE, SITUATIONAL_MULTI_STEP_MODE),
}

S1_UNIT12_ENABLED = {
    "food_formulas": (MULTI_STEP_MODE, SITUATIONAL_MULTI_STEP_MODE),
    "water_substances": (MULTI_STEP_MODE, SITUATIONAL_MULTI_STEP_MODE),
    "cooking_heat": (MULTI_STEP_MODE, SITUATIONAL_MULTI_STEP_MODE),
    "cooking_acid": (MULTI_STEP_MODE, SITUATIONAL_MULTI_STEP_MODE),
    "cooking_salt": (MULTI_STEP_MODE, SITUATIONAL_MULTI_STEP_MODE),
    "cooking_fermentation": (MULTI_STEP_MODE, SITUATIONAL_MULTI_STEP_MODE),
    "nutrition": (MULTI_STEP_MODE, SITUATIONAL_MULTI_STEP_MODE),
    "healthy_meal_project": (MULTI_STEP_MODE, SITUATIONAL_MULTI_STEP_MODE),
}

S1_UNIT13_ENABLED = {
    "movement": (MULTI_STEP_MODE, SITUATIONAL_MULTI_STEP_MODE),
    "forces_sport": (MULTI_STEP_MODE, SITUATIONAL_MULTI_STEP_MODE),
    "breathing": (MULTI_STEP_MODE, SITUATIONAL_MULTI_STEP_MODE),
    "sport_health": (MULTI_STEP_MODE, SITUATIONAL_MULTI_STEP_MODE),
}

S1_UNIT14_ENABLED = {
    "puberty_maturity": (MULTI_STEP_MODE, SITUATIONAL_MULTI_STEP_MODE),
    "reproductive_anatomy": (MULTI_STEP_MODE,),
    "pregnancy_sexual_health": (MULTI_STEP_MODE, SITUATIONAL_MULTI_STEP_MODE),
}

S2_UNIT21_ENABLED = {
    "solar_system": (MULTI_STEP_MODE, SITUATIONAL_MULTI_STEP_MODE),
    "light_telescopes": (MULTI_STEP_MODE, SITUATIONAL_MULTI_STEP_MODE),
    "life_earth_elsewhere": (MULTI_STEP_MODE, SITUATIONAL_MULTI_STEP_MODE),
    "atoms_molecules": (MULTI_STEP_MODE, SITUATIONAL_MULTI_STEP_MODE),
}

ENABLED_ADVANCED = {
    **PILOT_ENABLED,
    **S1_UNIT11_ENABLED,
    **S1_UNIT12_ENABLED,
    **S1_UNIT13_ENABLED,
    **S1_UNIT14_ENABLED,
    **S2_UNIT21_ENABLED,
}

STANDARD_SNAPSHOT = {
    "measurement": {
        "foundational": (
            "meas_foundational_mcq_kilo",
            "meas_foundational_keyword_time_unit",
            "meas_foundational_number_estimate_ruler_4",
            "meas_foundational_order_convert_steps",
            "meas_foundational_pick_two_base",
        ),
        "intermediate": (
            "meas_intermediate_mcq_accuracy",
            "meas_intermediate_keyword_mass_word",
            "meas_intermediate_number_estimate_ruler_47",
            "meas_intermediate_order_convert_steps",
            "meas_intermediate_pick_random_sources",
        ),
        "difficult": (
            "meas_difficult_mcq_cm_to_m",
            "meas_difficult_keyword_temp_unit",
            "meas_difficult_number_estimate_ruler_63",
            "meas_difficult_order_calibrate_steps",
            "meas_difficult_pick_three_base",
        ),
    },
    "movement": {
        "foundational": (
            "movement_foundational_mcq_avg",
            "movement_foundational_keyword_speed_word",
            "movement_foundational_number_v0",
            "movement_foundational_order_calc",
            "movement_foundational_pick_graph_ok",
        ),
        "intermediate": (
            "movement_intermediate_mcq_num",
            "movement_intermediate_keyword_metre_word",
            "movement_intermediate_number_v1",
            "movement_intermediate_order_graph_read",
            "movement_intermediate_pick_not_method",
        ),
        "difficult": (
            "movement_difficult_mcq_avg_vs",
            "movement_difficult_keyword_average_word",
            "movement_difficult_number_v2",
            "movement_difficult_order_full",
            "movement_difficult_pick_graph_false",
        ),
    },
    "infectious_disease": {
        "foundational": (
            "infectious_disease_foundational_mcq_bact",
            "infectious_disease_foundational_keyword_virus_word",
            "infectious_disease_foundational_number_chain3",
            "infectious_disease_foundational_order_chain_ord",
            "infectious_disease_foundational_pick_path_ok",
        ),
        "intermediate": (
            "infectious_disease_intermediate_mcq_abx",
            "infectious_disease_intermediate_keyword_vax_word",
            "infectious_disease_intermediate_number_day3",
            "infectious_disease_intermediate_order_vax_ord",
            "infectious_disease_intermediate_pick_hyg_ok",
        ),
        "difficult": (
            "infectious_disease_difficult_mcq_bar_c",
            "infectious_disease_difficult_keyword_imm_word",
            "infectious_disease_difficult_number_abx0",
            "infectious_disease_difficult_order_full_chain",
            "infectious_disease_difficult_pick_path_not",
        ),
    },
    "energy": {
        "foundational": (
            "energy_foundational_mcq_alex_en",
            "energy_foundational_keyword_energy_word",
            "energy_foundational_number_useful60",
            "energy_foundational_order_forms_ord",
            "energy_foundational_pick_form_ok",
        ),
        "intermediate": (
            "energy_intermediate_mcq_conserve",
            "energy_intermediate_keyword_conserve_word",
            "energy_intermediate_number_waste25",
            "energy_intermediate_order_ttc",
            "energy_intermediate_pick_cons_ok",
        ),
        "difficult": (
            "energy_difficult_mcq_both",
            "energy_difficult_keyword_thermal_word",
            "energy_difficult_number_in90",
            "energy_difficult_order_tf2",
            "energy_difficult_pick_not_en",
        ),
    },
}

LESSON_COUNT_SNAPSHOT = {
    "measurement": {"foundational": 12, "intermediate": 13, "difficult": 12},
    "movement": {"foundational": 11, "intermediate": 10, "difficult": 10},
    "infectious_disease": {"foundational": 10, "intermediate": 10, "difficult": 11},
    "energy": {"foundational": 10, "intermediate": 10, "difficult": 10},
}

PINNED_VARIANTS = (
    (
        "measurement",
        MULTI_STEP_MODE,
        "foundational",
        "measurement_foundational_ms_kilo_convert_compare",
        eursc_science_measurement,
    ),
    (
        "movement",
        MULTI_STEP_MODE,
        "foundational",
        "movement_foundational_ms_speed_extrapolate",
        eursc_science_movement,
    ),
    (
        "infectious_disease",
        SITUATIONAL_MULTI_STEP_MODE,
        "foundational",
        "infectious_disease_foundational_sms_token_double_safeguard",
        eursc_science_infectious_disease,
    ),
    (
        "energy",
        SITUATIONAL_MULTI_STEP_MODE,
        "foundational",
        "energy_foundational_sms_appliance_useful_public",
        eursc_science_energy,
    ),
)

DISCLOSE_RE = re.compile(
    r"\b(your diet|have you ever|tell us about your|describe your eating|"
    r"are you allergic|what are you allergic|your body|when did you|"
    r"have you started|are you attracted|your period|have you had sex|"
    r"do you use contraception|your partner|are you gay|your sexuality|"
    r"have you been pregnant|are you pregnant|describe your body|"
    r"do you smoke|have you smoked|do you vape|are you addicted|"
    r"what do you use|list your medication|are you depressed|"
    r"how many hours do you sleep|describe your mood|"
    r"who in your family is ill|have you been ill|"
    r"how do you feel|describe your hunger|are you dizzy|"
    r"map your body|your heartbeat|do you wear glasses)\b",
    re.I,
)
REQUEST_RE = re.compile(
    r"\b(rank your (home|household)|upload your bill|log your meals|"
    r"list who was ill|store vaccination status|who coughed in class)\b",
    re.I,
)
POWER_CALC_RE = re.compile(r"power in watts\?|P\s*=\s*W\s*/\s*t", re.I)
VIR_CALC_RE = re.compile(
    r"calculate resistance|what is the resistance|R\s*=\s*V\s*/\s*I", re.I
)


def _blob(problem):
    return " ".join(
        [
            str(problem.get("question") or ""),
            str(problem.get("solution") or ""),
            str(problem.get("hint") or ""),
        ]
    )


def _syllabus_slugs():
    return [
        module["slug"]
        for module in SYLLABUS_MODULES.values()
        if isinstance(module, dict) and module.get("slug")
    ]


def client_user_answer(problem):
    raw = str(problem.get("correct_answer_raw") or "")
    types = problem.get("answer_field_types") or []
    sep = "\x1e" if "\x1e" in raw else "|"
    parts = raw.split(sep)
    out = []
    for i, part in enumerate(parts):
        ft = types[i] if i < len(types) else "number"
        if ft in ("pick", "order"):
            parsed = _parse_proof_steps_raw(part)
            assert parsed, (ft, part)
            if parsed["mode"] == "pick":
                ids = parsed["correct_ids"][: parsed["pick_count"]]
            else:
                ids = parsed["expected_ids"]
            out.append("|".join(ids))
        else:
            out.append(part)
    return sep.join(out)


def csrf_from(html):
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match, "csrf token not found"
    return match.group(1)


def bearer(token):
    return {"Authorization": f"Bearer {token}", "Accept": "application/json"}


def register(client, email, handle):
    r = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "handle": handle,
            "password": "password123",
            "age_confirm": True,
        },
        headers={"Accept": "application/json"},
    )
    assert r.status_code == 201, r.data
    body = r.get_json()
    return body["token"], body["user"]["id"]


def login_web(client, email):
    html = client.get("/login").data.decode()
    client.post(
        "/login",
        data={
            "csrf_token": csrf_from(html),
            "email": email,
            "password": "password123",
        },
        follow_redirects=True,
    )


def logout(client):
    html = client.get("/").data.decode()
    client.post("/logout", data={"csrf_token": csrf_from(html)}, follow_redirects=True)


def test_same_variant_is_deterministic():
    for slug, mode, difficulty, variant_name, generate in PINNED_VARIANTS:
        random.seed(7)
        first = generate(difficulty, mode, variant_name=variant_name)
        random.seed(7)
        second = generate(difficulty, mode, variant_name=variant_name)
        assert first["question"] == second["question"], slug
        assert first["correct_answer_raw"] == second["correct_answer_raw"], slug
        assert first.get("answer_field_types") == second.get("answer_field_types"), slug
        labels = first.get("answer_labels") or []
        types = first.get("answer_field_types") or []
        assert 2 <= len(types) <= 4, (slug, types)
        assert len(labels) == len(types), (slug, labels, types)
        assert int(first.get("marks") or 0) == len(types), slug
        user = client_user_answer(first)
        result = check_number_fields(
            first["correct_answer_raw"],
            user,
            field_types=types,
        )
        assert result["correct"] is True, slug
        assert result["score"] == result["score_total"] == len(types), slug


def test_grader_partial_credit_and_class_work_binary():
    problem = eursc_science_energy(
        "difficult",
        SITUATIONAL_MULTI_STEP_MODE,
        variant_name="energy_difficult_sms_two_device_gap",
    )
    types = problem.get("answer_field_types") or []
    assert types == ["number", "number", "mcq"]
    user = client_user_answer(problem)
    sep = "\x1e" if "\x1e" in user else "|"
    parts = user.split(sep)
    parts[-1] = "Z"
    partial = sep.join(parts)
    result = check_number_fields(
        problem["correct_answer_raw"],
        partial,
        field_types=types,
    )
    assert result["correct"] is False
    assert result["score"] == 2
    assert result["score_total"] == 3
    stored, ok = grade_frozen_answer(problem, partial)
    assert stored == partial.strip()
    assert ok is False
    captured = _quicktest_answer_from_form(
        problem,
        {
            "qt_user_answer": partial,
            "qt_checked": "1",
        },
    )
    assert captured["checked"] is True
    assert captured["correct"] is False
    assert captured["score"] == 2
    assert captured["score_total"] == 3


def test_unavailable_cells_fail_closed():
    slugs = _syllabus_slugs()
    assert len(slugs) == 46
    assert len(set(slugs)) == 46
    science_slugs = {slug for slug in SCIENCE if slug != "es0_fixture"}
    assert science_slugs == set(slugs)

    for slug in slugs:
        key = ("eursc", "science", slug)
        capabilities = topic_mode_capabilities(*key)
        expected_advanced = ENABLED_ADVANCED.get(slug, ())
        assert capabilities[0] == "standard", slug
        assert tuple(mode for mode in capabilities if mode in ADVANCED_MODES) == expected_advanced, (
            slug,
            capabilities,
        )
        vf = SCIENCE[slug]["variants_func"]
        generate = SCIENCE[slug]["func"]
        for mode in ADVANCED_MODES:
            if mode in expected_advanced:
                continue
            assert _normalize_generator_mode(*key, mode) == "standard", (slug, mode)
            for difficulty in DIFFS:
                assert vf(difficulty, mode) == [], (slug, difficulty, mode)
                try:
                    generate(difficulty, mode)
                except ValueError as exc:
                    assert f"No {mode} variants" in str(exc), (slug, mode, exc)
                else:
                    raise AssertionError(f"{slug} leaked {mode} into generate")

    with app.test_client() as client:
        cases = (
            ("healthy_living", MULTI_STEP_MODE),
            ("energy", MULTI_STEP_MODE),
            ("infectious_disease", MULTI_STEP_MODE),
            ("smell", MULTI_STEP_MODE),
            ("reproductive_anatomy", SITUATIONAL_MULTI_STEP_MODE),
            ("interoception", MULTI_STEP_MODE),
        )
        for topic, requested in cases:
            response = client.post(
                "/api/v1/problems/generate",
                json={
                    "level": "eursc",
                    "subject": "science",
                    "topic": topic,
                    "mode": requested,
                    "difficulty": "foundational",
                    "action": "start",
                },
                headers={"Accept": "application/json"},
            )
            assert response.status_code == 200, (topic, requested, response.data[:300])
            payload = response.get_json()
            problem = payload["problem"]
            assert problem["mode"] == "standard", (topic, requested, problem["mode"])
            variant = (payload.get("selection") or {}).get("variant_name") or ""
            assert "_ms_" not in variant and "_sms_" not in variant, (topic, variant)


def test_qotd_and_lesson_pools_unchanged():
    assert all(level != "eursc" for level, *_rest in list_mcq_topic_paths())
    for day in ("2026-01-01", "2026-06-15", "2026-09-02"):
        qotd = get_daily_question(day_key=day)
        assert qotd["level"] != "eursc", qotd

    for slug, expected in STANDARD_SNAPSHOT.items():
        vf = SCIENCE[slug]["variants_func"]
        for difficulty in DIFFS:
            standard_names = tuple(fn.__name__ for fn in vf(difficulty, "standard"))
            assert standard_names == expected[difficulty], (slug, difficulty, standard_names)
            lesson = vf(difficulty, "lesson")
            lesson_names = [fn.__name__ for fn in lesson]
            assert len(lesson_names) == LESSON_COUNT_SNAPSHOT[slug][difficulty], (
                slug,
                difficulty,
                len(lesson_names),
            )
            assert all("_ms_" not in name and "_sms_" not in name for name in lesson_names), (
                slug,
                difficulty,
            )
            advanced = []
            for mode in ENABLED_ADVANCED[slug]:
                advanced.extend(fn.__name__ for fn in vf(difficulty, mode))
            assert set(standard_names).isdisjoint(advanced), (slug, difficulty)
            assert set(lesson_names).isdisjoint(advanced), (slug, difficulty)
        quiz = build_lesson_quiz("eursc", "science", slug, SCIENCE[slug], seed=17)
        assert len(quiz) == 10, slug
        quiz_blob = " ".join(str(item.get("variant_name") or "") for item in quiz)
        assert "_ms_" not in quiz_blob and "_sms_" not in quiz_blob, slug


def test_safeguarding_pilot_stems():
    generators = (
        (eursc_science_measurement, MULTI_STEP_MODE),
        (eursc_science_movement, MULTI_STEP_MODE),
        (eursc_science_infectious_disease, SITUATIONAL_MULTI_STEP_MODE),
        (eursc_science_energy, SITUATIONAL_MULTI_STEP_MODE),
    )
    for generate, mode in generators:
        for difficulty in DIFFS:
            problem = generate(difficulty, mode)
            blob = _blob(problem)
            assert not DISCLOSE_RE.search(blob), (generate.__name__, difficulty, blob[:220])
            assert not REQUEST_RE.search(blob), (generate.__name__, difficulty, blob[:220])
            assert not POWER_CALC_RE.search(blob), generate.__name__
            assert not VIR_CALC_RE.search(blob), generate.__name__
            assert "fictional" in blob.lower(), generate.__name__
    energy = eursc_science_energy(
        "difficult",
        SITUATIONAL_MULTI_STEP_MODE,
        variant_name="energy_difficult_sms_two_device_gap",
    )
    energy_blob = _blob(energy).lower()
    assert "public" in energy_blob
    assert not REQUEST_RE.search(energy_blob)
    infectious = eursc_science_infectious_disease(
        "foundational",
        SITUATIONAL_MULTI_STEP_MODE,
        variant_name="infectious_disease_foundational_sms_canteen_chain_break",
    )
    infectious_blob = _blob(infectious).lower()
    assert "fictional" in infectious_blob
    assert "have you been ill" not in infectious_blob
    assert "who coughed" not in infectious_blob


def test_mobile_a11y_surfaces():
    css = (ROOT / "static" / "css" / "practice.css").read_text(encoding="utf-8")
    assert ".free-response-inline.is-collect-only .free-response-field-check-btn" in css
    assert "display: none" in css.split(".free-response-inline.is-collect-only", 1)[1][:400]

    with app.test_client() as client:
        home = client.get("/").data.decode()
        assert 'name="viewport"' in home
        assert "width=device-width" in home
        assert 'for="mode-select"' in home
        assert 'id="mode-select"' in home
        assert 'value="multi_step"' in home
        assert 'value="situational_multi_step"' in home
        assert 'data-modes="standard,multi_step,situational_multi_step"' in home
        assert 'data-modes="standard,situational_multi_step"' in home

        suffix = uuid.uuid4().hex[:8]
        token_t, _uid_t = register(
            client, f"esexitt_{suffix}@example.com", f"esexitt_{suffix}"
        )
        token_s, uid_s = register(
            client, f"exits_{suffix}@example.com", f"exits_{suffix}"
        )
        headers_t = bearer(token_t)
        headers_s = bearer(token_s)
        assert client.post("/api/v1/me/teacher/enable", headers=headers_t).status_code == 200
        created = client.post(
            "/api/v1/teacher/classes",
            json={"name": "Pilot exit a11y"},
            headers=headers_t,
        )
        assert created.status_code == 201, created.data
        klass = created.get_json()["class"]
        assert client.post(
            "/api/v1/me/classes/join",
            json={"code": klass["join_code"], "disclosed": True},
            headers=headers_s,
        ).status_code == 201
        login_web(client, f"esexitt_{suffix}@example.com")
        set_work = client.get(
            f"/teacher/classes/{klass['id']}/assignments"
        ).data.decode()
        assert 'for="set-work-mode"' in set_work
        assert 'id="set-work-mode"' in set_work
        assert "data-modes=" in set_work
        assert "standard,multi_step" in set_work
        assert "standard,situational_multi_step" in set_work

        assigned = client.post(
            f"/api/v1/teacher/classes/{klass['id']}/assignments",
            json={
                "level": "eursc",
                "subject": "science",
                "topic": "infectious_disease",
                "mode": SITUATIONAL_MULTI_STEP_MODE,
                "difficulty": "foundational",
                "count": 1,
                "student_ids": [uid_s],
            },
            headers=headers_t,
        )
        assert assigned.status_code == 201, assigned.data
        aid = assigned.get_json()["assignment"]["id"]
        logout(client)
        login_web(client, f"exits_{suffix}@example.com")
        class_work = client.get(f"/class-work/{aid}").data.decode()
        assert "data-collect-only" in class_work
        assert 'aria-live="polite"' in class_work
        assert 'aria-label="Answer options"' in class_work or 'aria-label="Step bank"' in class_work
        assert "free-response-proof-bank" in class_work
        assert "class-work-fields-feedback" in class_work
        assert 'type="button"' in class_work
        assert "viewport-fit=cover" in class_work or "width=device-width" in class_work

        qt = client.post(
            "/quicktest/start",
            data={
                "level": "eursc",
                "subject": "science",
                "topic": "measurement",
                "mode": MULTI_STEP_MODE,
                "difficulty": "foundational",
            },
            follow_redirects=True,
        )
        assert qt.status_code == 200, qt.data
        qt_html = qt.data.decode()
        assert "free-response-field-row" in qt_html
        assert 'id="quiz-runner-check"' in qt_html
        assert "free-response-field-check-btn" in qt_html
        assert 'aria-live="polite"' in qt_html
        assert "data-collect-only" not in qt_html
        assert "width=device-width" in qt_html


def main():
    test_same_variant_is_deterministic()
    test_grader_partial_credit_and_class_work_binary()
    test_unavailable_cells_fail_closed()
    test_qotd_and_lesson_pools_unchanged()
    test_safeguarding_pilot_stems()
    test_mobile_a11y_surfaces()
    print("EURSC advanced pilot-exit checks passed.")


if __name__ == "__main__":
    main()
