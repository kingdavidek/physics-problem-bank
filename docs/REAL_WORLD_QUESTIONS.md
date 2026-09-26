# Problem Bank — Real-world question style (E4.1)

**Last updated:** 2026-08-15
**Status:** Planned — not implemented
**Audience:** The next AI agent implementing this
**Parent item:** `docs/POTENTIAL_FUTURE_FUNCTIONALITY.md` §3.0.1 (Phase E4 content depth)

---

## 1. What we are building

A third **question style** in the generator picker, next to *Standard question* and *Multiple Choice*:

```
Mode:  📝 Standard question | 🔘 Multiple Choice | 🛒 Real-world
```

Choosing **Real-world** gives the same maths, the same difficulty tiers, and the same graders — only the wording changes. Every stem is an everyday scenario (cooking, shopping, sport, travel, part-time work, phone bills).

Pilot scope is **three GCSE Maths topics**:

| Topic slug | Registry name | Generator file |
|---|---|---|
| `fdp` | Fractions, Decimals and Percentages | `generators/gcse/maths.py` + pools in `generators/gcse/maths_basic_topics_mcq.py` |
| `ratio_proportion` | Ratio and Proportion | `generators/gcse/maths_num_stats_prob_rat.py` |
| `compound_measures` | Compound Measures | `generators/gcse/maths_compound_measures.py` |

**Out of scope:** a second problem engine, new answer types, A/B testing, analytics dashboards, MCQ real-world banks, non-maths subjects. This is content work plus one new mode string.

---

## 2. What already exists (read before coding)

| Fact | Where |
|---|---|
| Mode dropdown is server-rendered with two options | `templates/index.html` (~line 116) |
| Mode string is normalised on every entry point | `normalize_mode()` in `generators/shared/variant_utils.py` — **unknown modes silently become `standard`** |
| Generator route reads/echoes the mode | `app.py` `index()` (~line 1644 onwards), `selected_mode=normalize_mode(raw_mode)` |
| Variant queues are built per (difficulty, mode) | `_get_problem_from_queue` / `_reroll_current_problem` in `app.py`, `variants_builder(difficulty, normalize_mode(mode))` (~line 1462) |
| Each topic exposes `variants_func(difficulty, mode)` | `topic_registry.py` `TOPICS[level][subject][slug]['variants_func']` |
| Practice variants are plain module-level functions returning a tuple | e.g. `_cm_f1_sdt_find_speed()` returns `(q, sol, hint, marks, answer)` |
| Named variants can be resolved globally by `__name__` | `lookup_variant_by_name()` in `variant_utils.py` — so variant functions **must** be module-level with unique names |
| Seven variants fill a queue tier | `TIER_VARIANT_COUNT = 7`, `select_tier_variants()` |
| Client-side dropdown filtering already exists | `initGeneratorForm()` / `setOptionVisibility()` in `static/js/site.js` (~line 60) |

Per-topic output shapes (match these exactly — the answer plumbing depends on them):

- **`compound_measures`** — variants return `(q, sol, hint, marks, answer)`; converted by `_cm_problem_from_output()`. Helpers `_cm_fields_answer`, `_cm_keyword_answer`, `_cm_algebraic_answer` produce multi-field / keyword / algebraic answers.
- **`ratio_proportion`** — variants return `(q, sol, hint, marks[, answer_payload])`; converted by `_ratio_problem_from_output()`, which also understands `problem_from_choice_output` payloads and `number_fields` dicts.
- **`fdp`** — variants live in `generators/gcse/maths.py` and return `(q, s, hint, marks, answer_or_payload)`; converted by `_fdp_problem_from_output()` via `_basic_maths_practice('fdp', …)`. Pools are declared in `_practice_pools()` in `generators/gcse/maths_basic_topics_mcq.py`.

---

## 3. Design decisions

1. **New mode string `real_world`**, not a flag on difficulty and not a new topic. It flows through the same session/queue/save/share plumbing as `standard`.
2. **`normalize_mode` must preserve it.** This is the single highest-risk line in the whole change: today anything unrecognised collapses to `standard`, which would silently disable the feature.
3. **Real-world questions are typed-answer (standard) questions.** No options, no `correct_answer`, no `generator_mcq_attempts` rows. Grading is untouched.
4. **Graceful fallback.** If a topic has no real-world pool for a difficulty, `variants_func` returns the normal practice pool. A user who deep-links `?mode=real_world` to an unsupported topic still gets a question.
5. **Capability flag in the registry** (`"real_world": True`) so the UI can show the option only where it is real, instead of hard-coding three slugs in a template.
6. **No new answer types.** If a scenario needs a type we do not have, rewrite the scenario, not the grader.

---

## 4. Implementation steps

### R1 — Mode plumbing (`generators/shared/variant_utils.py`)

```python
REAL_WORLD_MODE = "real_world"
REAL_WORLD_ALIASES = frozenset({"real_world", "real-world", "realworld"})

def normalize_mode(mode):
    if not mode:
        return "standard"
    m = str(mode).strip().lower()
    if m in REAL_WORLD_ALIASES:
        return REAL_WORLD_MODE
    if m in STANDARD_MODE_ALIASES:
        return "standard"
    if m == "mcq":
        return "mcq"
    if m == "lesson":
        return "lesson"
    return "standard"
```

Also update `apply_practice_variants_return()` so `real_world` is not treated as MCQ (it currently only special-cases `"mcq"`, so it already behaves; add an explicit comment rather than new logic).

**Audit every `normalize_mode` call site in `app.py`** (index, quicktest, saved problems, shared questions, challenges, worksheet export, reroll — roughly 20 call sites). None should compare `mode == 'standard'` to decide *typed vs MCQ*; the correct test is `mode == 'mcq'` or `problem.get('options')`. Fix any that assume two modes.

### R2 — Registry capability flag (`topic_registry.py`)

Add `"real_world": True` to the three topic dicts, and a helper next to the existing registry helpers:

```python
def topic_supports_real_world(cfg):
    return bool(cfg.get("real_world"))
```

### R3 — Content: real-world variant pools

For each of the three topics, add module-level variant functions with a clear prefix and register them in difficulty pools.

| Topic | Function prefix | Pool constants |
|---|---|---|
| `compound_measures` | `_cm_rw_f*` / `_cm_rw_i*` / `_cm_rw_d*` | `_CM_RW_FOUND`, `_CM_RW_INTER`, `_CM_RW_DIFF` |
| `ratio_proportion` | `_ratio_rw_f*` / `_ratio_rw_i*` / `_ratio_rw_d*` | `_RATIO_RW_FOUND`, `_RATIO_RW_INTER`, `_RATIO_RW_DIFF` |
| `fdp` | `gcse_fdp_rw_*` (public, lives in `maths.py`) | new `"real_world"` block inside `_practice_pools("fdp")` |

**Target counts:** at least **8 variants per difficulty per topic** (7 fill a queue tier; 8+ means the tier is not always the same set). That is 3 topics × 3 tiers × 8 = **72 new variants** minimum. Ship a topic at a time.

Then branch in each `*_variants` function, e.g. compound measures:

```python
def gcse_compound_measures_variants(difficulty, mode='practice'):
    if mode == 'mcq':
        return mcq_variants_from_bank_with_procedural(...)
    if mode == REAL_WORLD_MODE:
        rw = _CM_RW_POOLS.get(difficulty)
        if rw:
            return select_tier_variants(rw)
        # fall through to standard practice pool
    ...
```

Ratio and FDP get the same shape. For FDP also add a `real_world` branch to the no-`variant_name` fallback inside `gcse_maths_fdp()` (it currently hard-codes three random pools and ignores mode).

### R4 — UI (`templates/index.html`, `static/js/site.js`)

Template — one new option carrying the supported slugs:

```html
<option value="real_world"
        data-topics="{{ real_world_topics | join(',') }}"
        {% if selected_mode == 'real_world' %}selected{% endif %}>🛒 Real-world</option>
```

`app.py` `index()` passes `real_world_topics=` (slugs derived from the registry flag, not hard-coded).

`site.js` — extend `initGeneratorForm()`: on topic change, hide the real-world option when the selected topic is not in `data-topics`, then call the existing `ensureValidSelection()` so the mode falls back to `standard`. Reuse `setOptionVisibility`; do not write a second filtering mechanism.

Add a `Real-world` badge next to the existing difficulty/marks badges in the problem card when `selected_mode == 'real_world'`.

### R5 — Downstream surfaces

`mode` is persisted in `session['last_problem_payload']`, `saved_problems`, quicktest sessions, shared questions and challenges. These are free-text columns, so `real_world` needs no migration — but check:

- `models/quicktest.py` `build_quicktest_problems()` — already mode-agnostic; confirm a real-world quicktest builds 5 typed questions.
- Worksheet / PDF export and "Practise again" links in `templates/profile.html` — they round-trip `item.mode`, so they will restore real-world automatically.
- `_track_question_generated` does not record mode; leave it (no analytics in scope).

### R6 — Tests (`scripts/test_real_world_smoke.py`, new)

Register it in `scripts/run_smoke_tests.py`. Assert:

1. `normalize_mode('real_world') == 'real_world'` and legacy aliases still map correctly.
2. For each of the 3 topics × 3 difficulties: `variants_func(difficulty, 'real_world')` returns 7 callables, all names unique per tier, and each callable runs 20 times without raising.
3. Each generated problem has a non-empty `question`, a usable `correct_answer_raw`, **no** `options`, and a `solution`/`hint`.
4. Every real-world stem contains at least one everyday keyword (maintain a small allowlist: `£`, `recipe`, `shop`, `train`, `phone`, `gym`, …) — cheap guard against a standard variant being pasted into the wrong pool.
5. Route test: `POST /` with `mode=real_world` returns 200 and renders a question; an unsupported topic with `mode=real_world` still returns 200 (fallback).
6. Reroll: `POST /` with `action=reroll` keeps the same variant name and mode.
7. A real-world attempt writes **no** row to `generator_mcq_attempts`.

### R7 — Cache and docs

- Bump `CACHE_VERSION` in `static/js/sw.js` and the `?v=` query on `site.js` in `templates/base.html`; update the expected version in `scripts/test_pwa_smoke.py`.
- On ship: move §3.0.1 out of `docs/POTENTIAL_FUTURE_FUNCTIONALITY.md`, describe the mode in `docs/ARCHITECTURE.md`, and mark E4.1 shipped in `docs/AI_HANDOFF.md`.

---

## 5. Content authoring rules

These keep the pilot coherent and safe to grade.

1. **Same maths as the tier it sits in.** A real-world foundational ratio question is still one-step sharing; only the story changes.
2. **UK context.** £ and pence, km/miles as appropriate, metric cooking units, GCSE-realistic numbers (bus fares, not yacht prices).
3. **Answers stay clean.** Randomise from curated tuples (the existing `random.choice([...])` combo-list style) so answers land on sensible decimals — never `random.uniform` into a 2-dp rounding trap.
4. **One scenario family per variant function**, so a reroll gives a genuinely different question rather than the same sentence with new digits.
5. **Solutions show the everyday reasoning**, then the formula — e.g. "Cost per 100 g tells you which pack is better value" before "Unit price = price ÷ mass".
6. **Hints follow the existing `<strong>Key idea:</strong> …` house style.**
7. **Marks** match the equivalent standard variant (2 for one-step, 3 for multi-step).
8. **No names, brands, or scenarios that could embarrass a pupil** (no body weight, no family income, no gambling). Use neutral names or none at all.

Suggested scenario map (fills 8 per tier comfortably):

| Topic | Foundational | Intermediate | Difficult |
|---|---|---|---|
| `fdp` | Sale discounts, tips, VAT on a receipt | Percentage change on match attendance, reverse percentage on a sale price | Compound interest on savings, profit margin on a school fundraiser, best-value multi-pack |
| `ratio_proportion` | Scaling a recipe, mixing squash, sharing prize money | Map scale on a hike, paint mixing, staff-to-pupil ratios on a trip | Combining two ratios for a smoothie order, inverse proportion on shift work, currency plus commission |
| `compound_measures` | Average speed on a bus journey, density of a cake tin fill, pressure under a shoe | Two-leg cycle ride, filling a paddling pool, tyre pressure conversion | Meeting/overtaking on a motorway, fuel economy across mixed driving, flow rate with two taps |

---

## 6. Risks

| Risk | Mitigation |
|---|---|
| `normalize_mode` regression silently disables the mode | Smoke assertion #1; add a comment in the function |
| Wordy stems break MathJax/HTML rendering | Reuse existing `rf"…"` patterns; smoke asserts each variant renders and no `<` is unescaped |
| Reroll/queue confusion from duplicate function names | Unique `_rw_` prefixes; smoke asserts unique names per tier |
| Scope creep into MCQ real-world banks | Explicitly out of scope for the pilot |
| Longer questions on mobile | Keep stems ≤ 2 sentences before the ask; check on a 360 px viewport |

---

## 7. Definition of done

- [ ] `real_world` survives `normalize_mode` and all `app.py` call sites
- [ ] Three topics flagged in `topic_registry.py`, ≥ 8 variants per difficulty each
- [ ] Mode option appears only for supported topics; falls back cleanly otherwise
- [ ] `scripts/test_real_world_smoke.py` green and registered in the runner
- [ ] Full suite green: `python scripts/run_smoke_tests.py` with `PB_TESTING=1`
- [ ] Service worker cache version bumped
- [ ] `ARCHITECTURE.md`, `AI_HANDOFF.md`, `POTENTIAL_FUTURE_FUNCTIONALITY.md` updated
