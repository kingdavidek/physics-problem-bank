"""Lesson page AI explain assistant — validation, prompts, LLM calls."""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import Any

MIN_SELECTION_LEN = 8
MAX_SELECTION_LEN = 800
MAX_SURROUNDING_LEN = 1200
MAX_QUESTION_LEN = 200
MAX_QUIZ_QUESTION_LEN = 4000
MAX_QUIZ_EXPLANATION_LEN = 2000

_ANSWER_SEEKING = re.compile(
    r"\b("
    r"what\s+is\s+the\s+answer|"
    r"which\s+(option|one)\s+is\s+(correct|right)|"
    r"give\s+me\s+the\s+answer|"
    r"just\s+tell\s+me\s+[abcd]|"
    r"correct\s+answer\s+is"
    r")\b",
    re.IGNORECASE,
)

SYSTEM_PROMPT = """You are a friendly tutor embedded in a lesson page on Problem Bank.
- Explain at GCSE / A-Level level using short, clear sentences (UK English).
- Maximum 120 words unless the student asked for an example.
- Use **bold** sparingly for key terms only.
- Never quote or repeat the selected passage back — the student already sees it. Start straight with the explanation.
- Never state which MCQ option (A, B, C, or D) is correct.
- If the selection is a quiz question or option, teach the method only — do not pick an answer.
- If the student asks for the answer directly, explain the method instead.
- If unsure, say what you would check rather than guessing.
- Do not use LaTeX delimiters unless they appear in the selection.
- Do not mention being an AI unless asked."""


QUIZ_REVIEW_SYSTEM_PROMPT = """You are a friendly tutor on Problem Bank helping a student review a quiz they already completed.
- Explain at GCSE / A-Level level using short, clear sentences (UK English).
- Maximum 150 words unless the student asked for an example.
- Use **bold** sparingly for key terms only.
- The student can already see which option was correct and which they picked — explain **why** the correct answer works and, if they were wrong, where their choice went wrong.
- Teach the method step by step; do not just restate the question.
- If a model explanation is provided, build on it rather than repeating it verbatim.
- If unsure, say what you would check rather than guessing.
- Do not mention being an AI unless asked."""


def is_mock_mode() -> bool:
    return os.environ.get("LESSON_ASSIST_MOCK", "").strip().lower() in ("1", "true", "yes", "on")


def is_enabled() -> bool:
    flag = os.environ.get("LESSON_ASSIST_ENABLED", "").strip().lower()
    if flag in ("0", "false", "no", "off"):
        return False
    if is_mock_mode():
        return True
    if flag in ("1", "true", "yes", "on"):
        return True
    if os.environ.get("LESSON_ASSIST_API_KEY", "").strip():
        return True
    # No API key configured: stay on with mock responses (fine for local dev).
    return True


def uses_mock_responses() -> bool:
    if is_mock_mode():
        return True
    return not bool(os.environ.get("LESSON_ASSIST_API_KEY", "").strip())


def daily_limit_ip() -> int:
    return int(os.environ.get("LESSON_ASSIST_DAILY_LIMIT_IP", "20"))


def daily_limit_session() -> int:
    return int(os.environ.get("LESSON_ASSIST_DAILY_LIMIT_SESSION", "15"))


def provider() -> str:
    return os.environ.get("LESSON_ASSIST_PROVIDER", "openai").strip().lower()


def default_base_url() -> str:
    prov = provider()
    if prov == "deepseek":
        return "https://api.deepseek.com/v1"
    if prov == "anthropic":
        return ""
    return "https://api.openai.com/v1"


def _normalise_openai_base_url(base: str) -> str:
    """Ensure DeepSeek/OpenAI-compatible base URLs include /v1."""
    base = base.rstrip("/")
    prov = provider()
    if prov == "deepseek" and not base.endswith("/v1"):
        return f"{base}/v1"
    return base


def model_name() -> str:
    prov = provider()
    defaults = {
        "anthropic": "claude-3-5-haiku-20241022",
        "deepseek": "deepseek-chat",
        "openai": "gpt-4o-mini",
        "oai": "gpt-4o-mini",
    }
    return os.environ.get("LESSON_ASSIST_MODEL", defaults.get(prov, "gpt-4o-mini")).strip()


def _clean_question(text: str) -> str:
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text or "").strip()
    if len(text) > MAX_QUESTION_LEN:
        text = text[:MAX_QUESTION_LEN].rstrip()
    return text or "Explain this passage in simple terms."


def _clean_selection(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def _clean_selection(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def _strip_html(text: str) -> str:
    cleaned = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", cleaned).strip()


def _validate_quiz_review(payload: dict[str, Any]) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    context = payload.get("context") or {}
    quiz = payload.get("quiz") or {}
    if not isinstance(context, dict) or not isinstance(quiz, dict):
        return None, {"code": "invalid_request", "message": "Invalid quiz review payload."}

    level = str(context.get("level", "")).strip()
    subject = str(context.get("subject", "")).strip()
    topic = str(context.get("topic", "")).strip()
    if not level or not subject or not topic:
        return None, {"code": "invalid_context", "message": "Missing lesson context."}

    question = str(quiz.get("question", "")).strip()
    if len(_strip_html(question)) < MIN_SELECTION_LEN:
        return None, {
            "code": "invalid_quiz",
            "message": "Quiz question text is missing or too short.",
        }
    if len(question) > MAX_QUIZ_QUESTION_LEN:
        question = question[:MAX_QUIZ_QUESTION_LEN].rstrip()

    options = quiz.get("options") or []
    if not isinstance(options, list) or not options:
        return None, {"code": "invalid_quiz", "message": "Quiz options are missing."}
    clean_options = [re.sub(r"\s+", " ", str(opt)).strip() for opt in options[:8]]
    clean_options = [opt for opt in clean_options if opt]

    user_answer = str(quiz.get("userAnswer", "")).strip().upper()[:1]
    correct_answer = str(quiz.get("correctAnswer", "")).strip().upper()[:1]
    model_explanation = _strip_html(str(quiz.get("modelExplanation", "")).strip())
    if len(model_explanation) > MAX_QUIZ_EXPLANATION_LEN:
        model_explanation = model_explanation[:MAX_QUIZ_EXPLANATION_LEN].rstrip()

    question_number = quiz.get("questionNumber")
    try:
        question_number = int(question_number)
    except (TypeError, ValueError):
        question_number = None

    normalized = {
        "mode": "quiz_review",
        "selection": {
            "text": _strip_html(question)[:MAX_SELECTION_LEN],
            "surrounding": "",
            "charCount": len(_strip_html(question)),
        },
        "context": {
            "level": level,
            "subject": subject,
            "topic": topic,
            "topicTitle": str(context.get("topicTitle", topic)).strip() or topic,
            "sectionTitle": "",
            "pageUrl": str(context.get("pageUrl", "")).strip(),
            "nearMcq": True,
            "quizReview": True,
        },
        "quiz": {
            "question": question,
            "options": clean_options,
            "userAnswer": user_answer,
            "correctAnswer": correct_answer,
            "modelExplanation": model_explanation,
            "questionNumber": question_number,
            "wasCorrect": bool(quiz.get("wasCorrect")),
        },
        "question": _clean_question(payload.get("question", "")),
        "locale": str(payload.get("locale", "en-GB")).strip() or "en-GB",
    }
    return normalized, None


def validate_payload(payload: dict[str, Any] | None) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    """Return (normalized_payload, error_dict) where error_dict is {code, message}."""
    if not payload or not isinstance(payload, dict):
        return None, {"code": "invalid_request", "message": "Request body must be JSON."}

    if payload.get("mode") == "quiz_review":
        return _validate_quiz_review(payload)

    selection = payload.get("selection") or {}
    context = payload.get("context") or {}
    if not isinstance(selection, dict) or not isinstance(context, dict):
        return None, {"code": "invalid_request", "message": "Invalid selection or context."}

    text = _clean_selection(selection.get("text", ""))
    if len(text) < MIN_SELECTION_LEN:
        return None, {
            "code": "invalid_selection",
            "message": f"Please select at least {MIN_SELECTION_LEN} characters.",
        }
    if len(text) > MAX_SELECTION_LEN:
        return None, {
            "code": "invalid_selection",
            "message": f"Selection is too long (max {MAX_SELECTION_LEN} characters).",
        }

    level = str(context.get("level", "")).strip()
    subject = str(context.get("subject", "")).strip()
    topic = str(context.get("topic", "")).strip()
    if not level or not subject or not topic:
        return None, {"code": "invalid_context", "message": "Missing lesson context."}

    surrounding = _clean_selection(selection.get("surrounding", ""))
    if len(surrounding) > MAX_SURROUNDING_LEN:
        surrounding = surrounding[:MAX_SURROUNDING_LEN].rstrip()

    question = _clean_question(payload.get("question", ""))
    near_mcq = bool(context.get("nearMcq") or payload.get("nearMcq"))

    normalized = {
        "selection": {
            "text": text,
            "surrounding": surrounding,
            "charCount": len(text),
        },
        "context": {
            "level": level,
            "subject": subject,
            "topic": topic,
            "topicTitle": str(context.get("topicTitle", topic)).strip() or topic,
            "sectionTitle": str(context.get("sectionTitle", "")).strip(),
            "pageUrl": str(context.get("pageUrl", "")).strip(),
            "nearMcq": near_mcq,
        },
        "question": question,
        "locale": str(payload.get("locale", "en-GB")).strip() or "en-GB",
    }
    return normalized, None


def build_user_message(data: dict[str, Any]) -> str:
    ctx = data["context"]
    sel = data["selection"]
    lines = [
        f"Topic: {ctx['topicTitle']} ({ctx['level']} {ctx['subject']})",
    ]
    if ctx.get("sectionTitle"):
        lines.append(f"Section: {ctx['sectionTitle']}")
    lines.extend(
        [
            "",
            "Selected text:",
            f"\"\"\"{sel['text']}\"\"\"",
        ]
    )
    if sel.get("surrounding"):
        lines.extend(
            [
                "",
                "Surrounding context:",
                f"\"\"\"{sel['surrounding']}\"\"\"",
            ]
        )
    lines.extend(
        [
            "",
            f"Student question: {data['question']}",
            f"Near MCQ block: {'yes' if ctx.get('nearMcq') else 'no'}",
            "",
            "Reply without quoting the selected text back to the student.",
        ]
    )
    return "\n".join(lines)


def build_quiz_review_user_message(data: dict[str, Any]) -> str:
    ctx = data["context"]
    quiz = data["quiz"]
    lines = [
        f"Topic: {ctx['topicTitle']} ({ctx['level']} {ctx['subject']})",
        "Quiz review — the student has already submitted this question.",
    ]
    if quiz.get("questionNumber"):
        lines.append(f"Question number: {quiz['questionNumber']}")
    lines.extend(["", "Question:", quiz["question"], "", "Options:"])
    for opt in quiz["options"]:
        lines.append(f"- {opt}")
    lines.extend(
        [
            "",
            f"Student's answer: {quiz.get('userAnswer') or 'not answered'}",
            f"Correct answer: {quiz.get('correctAnswer') or 'unknown'}",
        ]
    )
    if quiz.get("modelExplanation"):
        lines.extend(["", "Explanation already shown on the page:", quiz["modelExplanation"]])
    lines.extend(
        [
            "",
            f"Student question: {data['question']}",
            "",
            "Help the student understand the reasoning behind the correct answer.",
        ]
    )
    return "\n".join(lines)


def wants_answer_only(question: str) -> bool:
    return bool(_ANSWER_SEEKING.search(question))


def _post_json(url: str, headers: dict[str, str], payload: dict[str, Any]) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"API HTTP {exc.code}: {detail}") from exc


def _call_openai(system: str, user: str) -> tuple[str, int]:
    api_key = os.environ.get("LESSON_ASSIST_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("LESSON_ASSIST_API_KEY is not set")

    base = _normalise_openai_base_url(
        os.environ.get("LESSON_ASSIST_BASE_URL", default_base_url())
    )
    if not base:
        raise RuntimeError("LESSON_ASSIST_BASE_URL is required for this provider")
    url = f"{base}/chat/completions"
    payload = {
        "model": model_name(),
        "temperature": 0.3,
        "max_tokens": 350,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    data = _post_json(url, headers, payload)
    content = data["choices"][0]["message"]["content"].strip()
    tokens = int(data.get("usage", {}).get("total_tokens", 0))
    return content, tokens


def _call_anthropic(system: str, user: str) -> tuple[str, int]:
    api_key = os.environ.get("LESSON_ASSIST_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("LESSON_ASSIST_API_KEY is not set")

    url = "https://api.anthropic.com/v1/messages"
    payload = {
        "model": model_name(),
        "max_tokens": 350,
        "temperature": 0.3,
        "system": system,
        "messages": [{"role": "user", "content": user}],
    }
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }
    data = _post_json(url, headers, payload)
    parts = data.get("content") or []
    text = ""
    for part in parts:
        if part.get("type") == "text":
            text += part.get("text", "")
    tokens = int(data.get("usage", {}).get("input_tokens", 0)) + int(
        data.get("usage", {}).get("output_tokens", 0)
    )
    return text.strip(), tokens


def _mock_body_for_question(question: str, topic: str) -> str:
    q = (question or "").lower()
    if "year 7" in q or "simpler" in q or "simple terms" in q:
        return (
            "Think of it like money: **5 − (−3)** means start at 5, then undo a move of 3 left — "
            "that's the same as adding 3, so you get **8**. Same idea whenever you see two negatives together."
        )
    if "example" in q or "worked" in q:
        return (
            "**Try this:** (+4) × (−2) = **−8** because different signs give a negative. "
            "(−4) × (−2) = **+8** because same signs give a positive. "
            "Plug in your own small numbers to check the rule you highlighted."
        )
    if "gcse" in q or "important" in q or "exam" in q or "matter" in q:
        return (
            f"In **{topic}**, exam questions often bury this rule inside a longer calculation — "
            "get it wrong here and the final answer is usually wrong too. "
            "Mark where the rule applies before you calculate."
        )
    return (
        f"Focus on the **idea behind this rule** in {topic}. "
        "Break it into a short example with small numbers, then check your steps match the lesson."
    )


def _mock_body_for_quiz(data: dict[str, Any]) -> str:
    quiz = data.get("quiz") or {}
    topic = data["context"]["topicTitle"]
    user = quiz.get("userAnswer") or "none"
    correct = quiz.get("correctAnswer") or "?"
    if quiz.get("wasCorrect"):
        return (
            f"You got this one right in **{topic}**. The key is to write the method in clear steps, "
            "then check each step matches the rule you used in the lesson."
        )
    if user and user != correct:
        return (
            f"You chose **{user}**, but **{correct}** is correct here. Compare how each option applies the rule — "
            "work through the method from the lesson with the numbers in the question, one step at a time."
        )
    return (
        f"Focus on the method for this **{topic}** question. Identify the rule, substitute carefully, "
        "then check whether your result matches the correct option."
    )


def _mock_explanation(data: dict[str, Any], *, demo: bool = False) -> dict[str, Any]:
    topic = data["context"]["topicTitle"]
    question = data.get("question", "")
    if demo:
        lead = "**Demo mode** — live AI is paused (no API credits). "
    else:
        lead = "**Demo mode** — set `LESSON_ASSIST_MOCK=0` and add credits for live AI. "
    if data.get("mode") == "quiz_review" or data["context"].get("quizReview"):
        explanation = f"{lead}\n\n{_mock_body_for_quiz(data)}"
    else:
        explanation = f"{lead}\n\n{_mock_body_for_question(question, topic)}"
    meta: dict[str, Any] = {
        "model": "mock",
        "tokensUsed": 0,
        "cached": False,
        "demo": demo,
    }
    if data["context"].get("quizReview"):
        meta["quizReview"] = True
    elif data["context"].get("nearMcq") or wants_answer_only(question):
        meta["refusal"] = "mcq_answer"
    return {"explanation": explanation, "meta": meta}


def _should_fallback_to_mock(exc: Exception) -> bool:
    if os.environ.get("LESSON_ASSIST_STRICT", "").strip().lower() in ("1", "true", "yes", "on"):
        return False
    msg = str(exc).lower()
    return any(
        token in msg
        for token in ("http 401", "http 402", "http 403", "insufficient balance", "authentication")
    )


def generate_explanation(data: dict[str, Any]) -> dict[str, Any]:
    """Call the configured LLM and return explanation metadata."""
    quiz_review = data.get("mode") == "quiz_review" or data["context"].get("quizReview")
    if quiz_review:
        user_msg = build_quiz_review_user_message(data)
        system_prompt = QUIZ_REVIEW_SYSTEM_PROMPT
    else:
        user_msg = build_user_message(data)
        system_prompt = SYSTEM_PROMPT
        if data["context"].get("nearMcq") or wants_answer_only(data["question"]):
            user_msg += (
                "\n\nImportant: The student may be looking at a quiz. "
                "Explain the underlying idea and method only — do not reveal A/B/C/D."
            )

    if uses_mock_responses():
        return _mock_explanation(data)

    prov = provider()
    try:
        if prov == "anthropic":
            explanation, tokens = _call_anthropic(system_prompt, user_msg)
        elif prov in ("openai", "oai", "deepseek"):
            explanation, tokens = _call_openai(system_prompt, user_msg)
        else:
            raise ValueError(f"Unsupported LESSON_ASSIST_PROVIDER: {prov}")
    except (RuntimeError, urllib.error.URLError, TimeoutError, ValueError) as exc:
        if _should_fallback_to_mock(exc):
            return _mock_explanation(data, demo=True)
        raise

    meta: dict[str, Any] = {
        "model": model_name(),
        "tokensUsed": tokens,
        "cached": False,
    }
    if quiz_review:
        meta["quizReview"] = True
    elif data["context"].get("nearMcq") or wants_answer_only(data["question"]):
        meta["refusal"] = "mcq_answer"

    return {"explanation": explanation, "meta": meta}


def user_facing_error(exc: Exception) -> str:
    msg = str(exc).lower()
    if "http 401" in msg or "http 403" in msg or "authentication" in msg:
        return "Invalid API key — check LESSON_ASSIST_API_KEY in your .env file."
    if "http 402" in msg or "insufficient balance" in msg or "quota" in msg:
        return "Your API account has no credits — add balance at your provider."
    if "http 404" in msg:
        return "API URL misconfigured — for DeepSeek use LESSON_ASSIST_BASE_URL=https://api.deepseek.com/v1"
    return "The explanation service is temporarily unavailable. Try again in a moment."
