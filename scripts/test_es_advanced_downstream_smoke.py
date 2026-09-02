"""Downstream class-work / save-share / quick-test support for structured number_fields."""
import json
import os
import re
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ["PB_TESTING"] = "1"
os.environ["MAIL_PROVIDER"] = "console"
os.environ.setdefault("SECRET_KEY", "pb-testing")

from app import app, format_readable_multipart_answer, get_db  # noqa: E402
from generators.eursc.s1_science_lab import eursc_science_measurement  # noqa: E402
from generators.eursc.s1_sports import eursc_science_movement  # noqa: E402
from generators.eursc.s2_health import eursc_science_infectious_disease  # noqa: E402
from generators.eursc.s3_machines import eursc_science_energy  # noqa: E402
from generators.shared.answer_checkers import (  # noqa: E402
    _parse_proof_steps_raw,
    check_number_fields,
)
from generators.shared.variant_utils import (  # noqa: E402
    MULTI_STEP_MODE,
    SITUATIONAL_MULTI_STEP_MODE,
)
from models.class_assignments import grade_frozen_answer, strip_problem_keys  # noqa: E402
from models.quicktest import QUICKTEST_LENGTH, load_quicktest_session  # noqa: E402


def bearer(token: str) -> dict:
    return {"Authorization": f"Bearer {token}", "Accept": "application/json"}


def csrf_from(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match, "csrf token not found"
    return match.group(1)


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
    return body["token"], body["user"]["id"], body["user"]["handle"]


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


def enable_and_create(client, headers, name):
    r = client.post("/api/v1/me/teacher/enable", headers=headers)
    assert r.status_code == 200, r.data
    r = client.post("/api/v1/teacher/classes", json={"name": name}, headers=headers)
    assert r.status_code == 201, r.data
    klass = r.get_json()["class"]
    return klass["id"], klass["join_code"]


def join(client, headers, code):
    r = client.post(
        "/api/v1/me/classes/join",
        json={"code": code, "disclosed": True},
        headers=headers,
    )
    assert r.status_code == 201, r.data


def stored_problems(assignment_id):
    with get_db() as conn:
        row = conn.execute(
            "SELECT problems_json FROM class_assignments WHERE id = ?",
            (assignment_id,),
        ).fetchone()
    assert row, assignment_id
    return json.loads(row["problems_json"])


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


def assert_no_keys(payload):
    dump = json.dumps(payload)
    assert "correct_answer_raw" not in dump
    assert "solution_html" not in dump


def test_grade_frozen_mixed_number_fields():
    measurement = eursc_science_measurement("foundational", MULTI_STEP_MODE)
    energy = eursc_science_energy("foundational", SITUATIONAL_MULTI_STEP_MODE)
    infectious = eursc_science_infectious_disease(
        "foundational", SITUATIONAL_MULTI_STEP_MODE
    )

    for problem in (measurement, energy, infectious):
        assert problem.get("answer_type") == "number_fields"
        user = client_user_answer(problem)
        stored, ok = grade_frozen_answer(problem, user)
        assert ok is True, problem.get("variant_name")
        assert stored == user.strip()
        _, wrong = grade_frozen_answer(problem, "nope")
        assert wrong is False

    stripped = strip_problem_keys(infectious, reveal=False)
    assert "correct_answer_raw" not in stripped
    assert stripped.get("answer_field_types")
    assert stripped.get("answer_field_options")
    assert stripped.get("answer_labels")


def test_teacher_set_work_lists_advanced_modes():
    with app.test_client() as client:
        suffix = uuid.uuid4().hex[:8]
        token, _uid, _handle = register(
            client, f"esadvt_{suffix}@example.com", f"esadvt_{suffix}"
        )
        headers = bearer(token)
        class_id, _code = enable_and_create(client, headers, "Advanced set-work")
        login_web(client, f"esadvt_{suffix}@example.com")
        html = client.get(f"/teacher/classes/{class_id}/assignments").data.decode()
        assert 'id="set-work-mode"' in html
        assert 'value="multi_step"' in html
        assert 'value="situational_multi_step"' in html
        assert "data-modes=" in html
        assert "standard,multi_step" in html
        assert "standard,situational_multi_step" in html


def _assign_and_answer(client, headers_teacher, headers_student, student_id, scope):
    r = client.post(
        f"/api/v1/teacher/classes/{scope['class_id']}/assignments",
        json={
            "level": scope["level"],
            "subject": scope["subject"],
            "topic": scope["topic"],
            "mode": scope["mode"],
            "difficulty": scope["difficulty"],
            "count": 1,
            "student_ids": [student_id],
        },
        headers=headers_teacher,
    )
    assert r.status_code == 201, r.data
    aid = r.get_json()["assignment"]["id"]
    assert r.get_json()["assignment"]["mode"] == scope["mode"]

    r = client.get(f"/api/v1/me/class-work/{aid}", headers=headers_student)
    assert r.status_code == 200, r.data
    work = r.get_json()["class_work"]
    assert_no_keys(work)
    problem = work["problems"][0]
    assert problem.get("answer_type") == "number_fields"
    assert problem.get("answer_field_types")
    assert "correct_answer_raw" not in problem

    stored = stored_problems(aid)[0]
    user = client_user_answer(stored)
    r = client.post(
        f"/api/v1/me/class-work/{aid}/answer",
        json={"index": 0, "user_answer": user},
        headers=headers_student,
    )
    assert r.status_code == 200, r.data
    done = r.get_json()["class_work"]
    assert done["problems"][0]["answered"] is True
    assert done["problems"][0]["correct"] is True
    assert done["problems"][0].get("correct_answer_raw")
    return aid, stored, user


def test_class_work_grades_structured_parts():
    with app.test_client() as client:
        suffix = uuid.uuid4().hex[:8]
        token_t, _uid_t, _h_t = register(
            client, f"esadvct_{suffix}@example.com", f"esadvct_{suffix}"
        )
        token_s, uid_s, _h_s = register(
            client, f"esadvcs_{suffix}@example.com", f"esadvcs_{suffix}"
        )
        headers_t = bearer(token_t)
        headers_s = bearer(token_s)
        class_id, code = enable_and_create(client, headers_t, "EURSC advanced work")
        join(client, headers_s, code)

        cases = (
            {
                "topic": "movement",
                "mode": MULTI_STEP_MODE,
            },
            {
                "topic": "measurement",
                "mode": MULTI_STEP_MODE,
            },
            {
                "topic": "infectious_disease",
                "mode": SITUATIONAL_MULTI_STEP_MODE,
            },
            {
                "topic": "energy",
                "mode": SITUATIONAL_MULTI_STEP_MODE,
            },
        )
        first_aid = None
        for case in cases:
            aid, stored, _user = _assign_and_answer(
                client,
                headers_t,
                headers_s,
                uid_s,
                {
                    "class_id": class_id,
                    "level": "eursc",
                    "subject": "science",
                    "topic": case["topic"],
                    "mode": case["mode"],
                    "difficulty": "foundational",
                },
            )
            if first_aid is None:
                first_aid = aid
            assert stored.get("answer_field_types")

        r = client.post(
            f"/api/v1/teacher/classes/{class_id}/assignments",
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
        assert r.status_code == 201, r.data
        open_aid = r.get_json()["assignment"]["id"]

        login_web(client, f"esadvcs_{suffix}@example.com")
        html = client.get(f"/class-work/{first_aid}").data.decode()
        assert "Correct" in html
        unanswered = client.get(f"/class-work/{open_aid}").data.decode()
        assert "data-collect-only" in unanswered
        assert "free-response-field-row" in unanswered
        assert "correct_answer_raw" not in unanswered or 'data-correct-raw=""' in unanswered
        assert "class-work-answer-form" in unanswered


def test_quicktest_and_save_share_render_structured_fields():
    infectious = eursc_science_infectious_disease(
        "foundational", SITUATIONAL_MULTI_STEP_MODE
    )
    movement = eursc_science_movement("foundational", MULTI_STEP_MODE)
    assert infectious.get("answer_field_types")
    assert movement.get("answer_field_types")

    with app.test_client() as client:
        suffix = uuid.uuid4().hex[:8]
        token, _uid, _handle = register(
            client, f"esadvq_{suffix}@example.com", f"esadvq_{suffix}"
        )
        login_web(client, f"esadvq_{suffix}@example.com")

        r = client.post(
            "/quicktest/start",
            data={
                "level": "eursc",
                "subject": "science",
                "topic": "movement",
                "mode": MULTI_STEP_MODE,
                "difficulty": "foundational",
            },
            follow_redirects=True,
        )
        assert r.status_code == 200, r.data
        body = r.data.decode()
        assert "free-response-inline" in body
        assert "free-response-field-row" in body
        assert "data-field-types" in body

        r = client.post(
            "/api/v1/problems/generate",
            json={
                "level": "eursc",
                "subject": "science",
                "topic": "infectious_disease",
                "mode": SITUATIONAL_MULTI_STEP_MODE,
                "difficulty": "foundational",
                "action": "start",
            },
            headers={"Accept": "application/json"},
        )
        assert r.status_code == 200, r.data
        problem = r.get_json()["problem"]
        assert problem.get("answer_type") == "number_fields"
        assert problem.get("answer_field_options")

        html = client.get("/").data.decode()
        r = client.post(
            "/saved-problems/save",
            data={"csrf_token": csrf_from(html)},
            follow_redirects=False,
        )
        assert r.status_code in (302, 303, 200), r.data

        r = client.post(
            "/api/v1/shared-questions",
            json={"visibility": "public"},
            headers=bearer(token),
        )
        assert r.status_code == 200, r.data
        share_url = r.get_json()["share_url"]
        shared = client.get(share_url).data.decode()
        assert "free-response-inline" in shared
        assert "free-response-field-row" in shared
        assert "free-response-proof-bank" in shared or "free-response-field-mcq" in shared


def test_whole_payload_check_uses_field_types():
    problem = eursc_science_energy("difficult", SITUATIONAL_MULTI_STEP_MODE)
    user = client_user_answer(problem)
    result = check_number_fields(
        problem["correct_answer_raw"],
        user,
        field_types=problem.get("answer_field_types"),
    )
    assert result["correct"] is True
    assert result["score_total"] == len(problem["answer_field_types"])
    assert result["score"] == result["score_total"]


def _problem_has_pick_and_order(problem):
    types = problem.get("answer_field_types") or []
    return "pick" in types and "order" in types


def test_readable_multipart_answer_resolves_pick_order_labels():
    problem = None
    for _ in range(12):
        candidate = eursc_science_infectious_disease(
            "foundational", SITUATIONAL_MULTI_STEP_MODE
        )
        if _problem_has_pick_and_order(candidate):
            problem = candidate
            break
    assert problem, "expected a foundational infectious SMS item with pick and order"
    user = client_user_answer(problem)
    readable = format_readable_multipart_answer(user, problem)
    assert "\x1e" not in readable
    assert "s1|" not in readable
    labels = readable.lower()
    assert "source" in labels or "route" in labels or "host" in labels
    assert "public" in labels or "contact" in labels or "wash" in labels


def test_class_work_pick_order_banks_and_answered_display():
    with app.test_client() as client:
        suffix = uuid.uuid4().hex[:8]
        token_t, _uid_t, _h_t = register(
            client, f"esadvpk_{suffix}@example.com", f"esadvpk_{suffix}"
        )
        token_s, uid_s, _h_s = register(
            client, f"esadvps_{suffix}@example.com", f"esadvps_{suffix}"
        )
        headers_t = bearer(token_t)
        headers_s = bearer(token_s)
        class_id, code = enable_and_create(client, headers_t, "Pick order class work")
        join(client, headers_s, code)

        stored = None
        aid = None
        for _ in range(16):
            r = client.post(
                f"/api/v1/teacher/classes/{class_id}/assignments",
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
            assert r.status_code == 201, r.data
            aid = r.get_json()["assignment"]["id"]
            stored = stored_problems(aid)[0]
            if _problem_has_pick_and_order(stored):
                break
        else:
            raise AssertionError("could not sample a pick/order class-work item")

        login_web(client, f"esadvps_{suffix}@example.com")
        unanswered = client.get(f"/class-work/{aid}").data.decode()
        assert "data-collect-only" in unanswered
        assert "is-collect-only" in unanswered
        assert "free-response-field-row--order" in unanswered
        assert "free-response-field-row--pick" in unanswered
        assert "free-response-proof-bank" in unanswered
        assert unanswered.count("data-step-id=") >= 4
        assert "class-work-fields-feedback" in unanswered
        assert "Complete every part" not in unanswered
        assert "correct_answer_raw" not in unanswered or 'data-correct-raw=""' in unanswered
        order_counts = re.findall(
            r'free-response-field-row--order"[^>]*data-pick-count="(\d+)"',
            unanswered,
        )
        if not order_counts:
            order_counts = re.findall(
                r'data-pick-count="(\d+)"[^>]*free-response-field-row--order',
                unanswered,
            )
        assert order_counts, unanswered[unanswered.find("field-row--order") : unanswered.find("field-row--order") + 400]
        assert int(order_counts[0]) >= 2

        r = client.post(
            f"/class-work/{aid}",
            data={
                "csrf_token": csrf_from(unanswered),
                "index": "0",
                "user_answer": "",
            },
            follow_redirects=True,
        )
        assert r.status_code == 200, r.data
        empty_html = r.data.decode()
        assert "Enter an answer first." in empty_html
        assert "Correct" not in empty_html or "Your answer:" not in empty_html

        user = client_user_answer(stored)
        r = client.post(
            f"/class-work/{aid}",
            data={
                "csrf_token": csrf_from(empty_html),
                "index": "0",
                "user_answer": user,
            },
            follow_redirects=True,
        )
        assert r.status_code == 200, r.data
        answered = r.data.decode()
        assert "Your answer:" in answered
        assert "Correct" in answered
        readable = format_readable_multipart_answer(user, stored)
        for chunk in readable.split(" · "):
            snippet = chunk.strip()[:24]
            if snippet:
                assert snippet in answered, snippet
        assert "solution" in answered.lower() or "Source" in answered
        assert "class-work-answer-form" not in answered

        r = client.get(f"/api/v1/me/class-work/{aid}", headers=headers_s)
        work = r.get_json()["class_work"]
        assert work["problems"][0]["answered"] is True
        assert work["problems"][0]["correct"] is True


def test_quicktest_full_run_persists_multipart_scores():
    with app.test_client() as client:
        suffix = uuid.uuid4().hex[:8]
        register(client, f"esadvqt_{suffix}@example.com", f"esadvqt_{suffix}")
        login_web(client, f"esadvqt_{suffix}@example.com")
        r = client.post(
            "/quicktest/start",
            data={
                "level": "eursc",
                "subject": "science",
                "topic": "infectious_disease",
                "mode": SITUATIONAL_MULTI_STEP_MODE,
                "difficulty": "foundational",
            },
            follow_redirects=True,
        )
        assert r.status_code == 200, r.data
        body = r.data.decode()
        assert "free-response-inline" in body
        assert "quicktest-next-form" in body

        with client.session_transaction() as sess:
            qt_id = sess.get("qt_id")
        assert qt_id

        for i in range(QUICKTEST_LENGTH):
            with get_db() as conn:
                data = load_quicktest_session(conn, qt_id)
            assert data, qt_id
            idx = int(data.get("index") or 0)
            problems = data.get("problems") or []
            assert idx == i, (idx, i)
            assert len(problems) == QUICKTEST_LENGTH
            problem = problems[idx]
            assert problem.get("answer_type") == "number_fields"
            html = body
            r = client.post(
                "/quicktest/next",
                data={
                    "csrf_token": csrf_from(html),
                    "qt_user_answer": client_user_answer(problem),
                    "qt_checked": "1",
                },
                follow_redirects=True,
            )
            assert r.status_code == 200, r.data
            body = r.data.decode()

        assert "Solutions" in body
        assert "Typed answers checked:" in body
        assert "Your answer:" in body
        with get_db() as conn:
            finished = load_quicktest_session(conn, qt_id)
        answers = finished.get("answers") or []
        assert len(answers) == QUICKTEST_LENGTH
        for item in answers:
            assert item.get("user_answer")
            assert item.get("checked") is True
            assert item.get("correct") is True
            assert int(item.get("score_total") or 0) >= 2
            assert item.get("score") == item.get("score_total")
        total_parts = sum(int(item["score_total"]) for item in answers)
        assert f"{total_parts} / {total_parts}" in body


def main():
    test_grade_frozen_mixed_number_fields()
    test_teacher_set_work_lists_advanced_modes()
    test_class_work_grades_structured_parts()
    test_quicktest_and_save_share_render_structured_fields()
    test_whole_payload_check_uses_field_types()
    test_readable_multipart_answer_resolves_pick_order_labels()
    test_class_work_pick_order_banks_and_answered_display()
    test_quicktest_full_run_persists_multipart_scores()
    print("EURSC advanced downstream checks passed.")


if __name__ == "__main__":
    main()
