# Problem Bank — UI & graphics redesign (Phase U)

**Last updated:** 2026-08-24
**Status:** **U0–U5 shipped.** U7 in progress (U7.1–U7.3, U7.5). U6 (lesson unification), remaining U7, U8 (a11y/QA) remain.
**Audience:** The next AI agent / developer implementing this
**Companions:** `docs/MOBILE.md` (M0–M4 shipped), `docs/ARCHITECTURE.md`, `docs/ENGAGEMENT_VISUAL.md`

Phase U is a **visual and structural** redesign. It does not change grading, generators, APIs, or data models. It changes CSS, templates, a small amount of JS, and the SVG diagram vocabulary.

**Design target:** Duolingo / chess.com — tactile, confident, obviously a *product* rather than a school portal. Mobile first, desktop second.

---

## 0. Why

The site is functionally rich and mobile-*usable* (M0–M4), but it reads as a stack of identical grey-white rectangles. Three concrete causes:

1. **One card recipe for everything.** `.section-panel`, `.problem-card`, `.form-card`, `.topic-card`, `.profile-stat-card` are all `white + 1px border + 12px radius + soft shadow` (`base.html` 242–252, 763–777, 2555–2562). Nothing signals importance.
2. **Navigation is hidden.** Everything except Generator/Topics/About lives behind a hamburger. There is no bottom tab bar. On a phone the user cannot see what the app *does*.
3. **Nothing is rewarding.** A 30-day streak renders as the character `3` `0` in the same box as "Topics this week". Milestones are flat amber circles (592–602). The only progress bar is 8px tall (2540–2551). There are exactly **two** keyframe animations in the entire app.

Secondary: ~3,627 lines of CSS inline in `base.html` with no `static/css/` directory, token drift (`--radius-md` undefined at line 564; `--color-primary` resolves to teal `#01696f` at 2102 while `--primary` is blue `#1a6fa8`; `lesson_mcq_quiz.html` uses `#2563eb`), and 40 lesson templates that bypass the component system entirely with inline `style=""`.

---

## 1. Phases and order

| # | Phase | Size | Risk | Visible win | Depends on |
|---|---|---|---|---|---|
| **U0** | CSS extraction + token foundation — **shipped** | M | Medium | Low (invisible) | — |
| **U1** | Core components — buttons, cards, forms — **partly shipped** | M | Low | **High** | U0 |
| **U2** | Mobile app shell — bottom tab bar | S | Low | **Highest** | U1 |
| **U3** | Gamification layer — streak, XP, celebration | M | Low | **High** | U1 |
| **U4** | Page-by-page redesign | L | Medium | High | U1–U3 |
| **U4.2a** | Syllabus `order` in `topic_registry.py` | S | Medium | None (data) | — (own PR; **not** CSS) |
| **U5** | Graphics & diagram system — **shipped** | L | Medium | High | U0 |
| **U6** | Lesson template unification (40 files) | L | **High** | Medium | U1, U5 |
| **U7** | Motion, sound, delight | S | Low | Medium | U1–U4 |
| **U8** | Accessibility, performance, QA | M | Low | — | all |

**Recommended sequence:** U0 → U1 → U2 → U3 → U4.2a → U4 → U5 → U7 → U6 → U8.

U6 (lessons) is deliberately late: it is the largest mechanical change, it is the least visited surface per session, and doing it after U5 means the diagram kit already exists.

**U4.2a is not a CSS phase.** The skill-tree topic path (U4.2b) needs a syllabus order that `topic_registry.py` does not currently have. Adding `order` / prerequisite fields is the **only** part of Phase U that touches non-presentational code. Implement it as a **separate reviewed change** (own commit, own smoke coverage) *before* any path UI work — do not fold it into U0–U3, U4 chrome restyles, or a CSS PR. Full spec: §7.2.

**Ship gate between every phase:** `python scripts/run_smoke_tests.py` green, `CACHE_VERSION` bumped in `static/js/sw.js`, asset `?v=` query params bumped in `base.html`.

---

## 2. Design language

### 2.1 Principles

1. **Elevation over outlines.** Delete most `1px solid --border`. Depth comes from shadow, tint, and spacing. This single rule removes the "blocky" feel.
2. **Cards differ by job.** A question card, a stat card, and a list row should not share a skin.
3. **One primary action per screen**, and it should be unmistakable — big, saturated, bottom-anchored on mobile.
4. **Every correct answer is an event.** Motion, colour, and a number that goes up.
5. **Round and chunky.** Radii up (`12px` → `16/20px`), padding up, borders down, font weights up.
6. **Mobile is the design; desktop is the wide version of it.** Not the reverse.
7. **No third-party UI framework.** No Tailwind, no Bootstrap. Hand-rolled tokens + components, consistent with the existing codebase.

### 2.2 Palette

Keep blue as the brand anchor (it is already the PWA `theme-color` and the avatar/buddy accent), but saturate it and add an **energy** set. Current blues are muted to the point of being institutional.

```css
/* Brand */
--brand-50:  #eff8ff;
--brand-100: #d8edfd;
--brand-200: #b4dcfb;
--brand-400: #3b9ee5;
--brand-500: #1a7fc4;   /* was --primary #1a6fa8 — same hue, more chroma */
--brand-600: #14649e;
--brand-700: #0e4e7a;   /* = existing --primary-dark, keep */

/* Energy — the "gamey" set */
--streak-500: #f59e0b;  /* flame / streak / XP amber */
--streak-600: #d97706;
--xp-500:     #8b5cf6;  /* levels, badges, rare unlocks */
--correct-500:#22c55e;  /* replaces ad-hoc #16a34a */
--correct-600:#16a34a;
--wrong-500:  #ef4444;  /* replaces ad-hoc #dc2626 */
--gold-500:   #eab308;  /* rank 1, top badges */

/* Surfaces — three levels, not one */
--surface:        #ffffff;   /* raised cards */
--surface-sunken: #f1f5f9;   /* page background wells, inset rows */
--surface-tint:   var(--brand-50); /* informational / selected */
```

**Semantic aliases** (`--success`, `--error`, `--warning`) map onto the above so the ~20 hardcoded hex values across MCQ, inputs, and proof steps can be swept in one pass.

**Dark mode:** out of scope for U0–U8, but *all* colours must be defined as tokens in one `:root` block so a later `@media (prefers-color-scheme: dark)` override is a single file change. Do not hardcode hex outside `tokens.css`.

### 2.3 Spacing and radius scale

Replace the current ad-hoc 4/6/8/10/12/14/16/18/20/22/24/28/32 with a strict 4px scale.

```css
--space-1: 4px;   --space-2: 8px;   --space-3: 12px;  --space-4: 16px;
--space-5: 20px;  --space-6: 24px;  --space-8: 32px;  --space-10: 40px;
--space-12: 48px; --space-16: 64px;

--radius-sm: 10px;  --radius:    16px;
--radius-lg: 20px;  --radius-xl: 28px;  --radius-pill: 999px;
```

Delete `--radius-md` usage at `base.html:564` or define it.

### 2.4 Elevation

```css
--elev-0: none;
--elev-1: 0 1px 2px rgba(15,23,42,.04), 0 1px 3px rgba(15,23,42,.06);
--elev-2: 0 4px 12px rgba(15,23,42,.07), 0 2px 4px rgba(15,23,42,.04);
--elev-3: 0 12px 28px rgba(20,100,158,.14), 0 4px 8px rgba(15,23,42,.05);
--elev-press: inset 0 2px 4px rgba(15,23,42,.10);
```

### 2.5 Typography

Keep **Work Sans** + **Source Serif 4** — the pairing is good and the serif is genuinely useful for maths prose. Change the *scale* and *weights*, not the faces.

| Token | Size | Weight | Use |
|---|---|---|---|
| `--text-xs` | 0.75rem | 600 | meta, timestamps, pills |
| `--text-sm` | 0.875rem | 500 | secondary body, list meta |
| `--text-base` | 1rem | 400 | body |
| `--text-lg` | 1.125rem | 600 | card titles |
| `--text-xl` | 1.375rem | 700 | section headings (h2) |
| `--text-2xl` | 1.75rem | 700 | page titles (h1) |
| `--text-3xl` | 2.5rem | 800 | **stat numbers only** |
| `--text-4xl` | 3.25rem | 800 | streak hero number |

Define `h1`–`h4` globally (currently only `h1`/`h2` exist, `base.html` 185–196). Raise heading weight from 600 → 700. Section titles move from `0.95rem` tinted bars to real `1.375rem/700` headings.

### 2.6 The signature button

This is the highest ratio of "gamey" to effort in the whole plan. Duolingo's button has a solid bottom edge that compresses on press.

```css
.btn {
  border-radius: var(--radius);
  padding: var(--space-3) var(--space-6);
  font-weight: 700;
  letter-spacing: .01em;
  border: none;
  box-shadow: 0 4px 0 var(--btn-edge);
  transition: transform 80ms var(--ease), box-shadow 80ms var(--ease);
}
.btn:active {
  transform: translateY(4px);
  box-shadow: 0 0 0 var(--btn-edge);
}
.btn-primary  { background: var(--brand-500);   --btn-edge: var(--brand-700); color:#fff; }
.btn-correct  { background: var(--correct-500); --btn-edge: var(--correct-600); color:#fff; }
.btn-ghost    { background: var(--surface); --btn-edge: var(--border); color: var(--brand-600); }
```

Uppercase is optional; recommend sentence case with `font-weight: 700` to stay UK-schoolwork-appropriate rather than shouty.

`prefers-reduced-motion`: keep the shadow change, drop the transform.

---

## 3. Phase U0 — CSS extraction and tokens — **SHIPPED**

**Outcome:** Everything after this becomes tractable.

The `base.html` `<style>` block (lines 31–3658, 3,626 lines) was split into nine
files at **contiguous, ascending** line ranges, so concatenating them in link
order reproduced the original byte-for-byte. A migration script verified that
round-trip before writing anything, which is why the split carried no cascade
risk despite touching every rule in the app.

| File | Was | Contents |
|---|---|---|
| `tokens.css` | 32–71 | Design tokens — the only file allowed raw colour values |
| `base.css` | 72–202 | Reset, document, page shell, header/nav, typography |
| `components.css` | 203–802 | Hero, panels, profile/social lists, avatars, stats, milestones, leaderboard, topic grid, lesson rail |
| `chrome.css` | 803–1551 | Form controls, toasts, notification/menu panels, search overlay, study buddy, PWA chrome |
| `practice.css` | 1552–2553 | Buttons, MCQ options, free-response answer widgets |
| `pages.css` | 2554–2884 | Problem card, MathJax, answer/hint reveals, topic page, errors, inline-styled lesson pages, print |
| `responsive.css` | 2885–3276 | Mobile media queries — **must stay after the rules it overrides** |
| `diagrams.css` | 3277–3482 | Instructional SVG, probability-tree inputs, quick-reference panels |
| `lesson-assist.css` | 3483–3657 | Lesson AI assistant panel |

**Load order is load-bearing** and is asserted in `scripts/test_pwa_smoke.py`.
Naming is positional rather than perfectly semantic (`chrome.css` holds forms
*and* overlays because they were adjacent); that is deliberate, since renaming
would have meant reordering.

| Step | Status | Note |
|---|---|---|
| U0.1–U0.7 | Done | Nine files as above |
| U0.2 | Done | Three-layer token file: primitive ramps → semantic tokens → legacy aliases. Legacy names (`--primary`, `--shadow`, `--badge-*`, …) are remapped onto the new scales, so untouched CSS shifted palette for free. Delete each alias as its last consumer migrates. |
| U0.8 | Done | 134 hardcoded colour literals → 42. Collapsed 39 dead `var(--x, fallback)` pairs, several of which disagreed with the token (`--color-primary` fell back to teal `#01696f` while `--primary` was blue). Defined `--radius-md`. Remaining 42 are `#fff` and diagram/lesson colours, owned by U5/U6. |
| U0.9 | Done | `CACHE_VERSION` `pb-v26` → `pb-v27`; all nine files added to `PRECACHE_URLS`. **`isJsAsset` became `isVersionedAsset`** — the service worker was cache-first for non-JS static assets, which would have made `?v=` busts useless for CSS. |
| U0.10 | Done | `test_pwa_smoke.py` asserts each file serves 200, that link order matches, and that no `<style>` block remains inline |
| U0.11 | Done | `/styleguide`, gated on `PB_STYLEGUIDE=1` (or `PB_TESTING=1`), 404 otherwise |

**Latent bug found:** `test_avatar_smoke.py` asserted `'user-avatar' in` the
`/leaderboard/friends` HTML. The leaderboard is empty for a user with no
friends, so the assertion was passing against the `.user-avatar` rule in the
inline `<style>` block, not against markup. Repointed at `/profile`, which
always renders the viewer's own avatar.

**Known debt:** total shipped CSS is ~95KB uncompressed against the 60KB U8.6
budget. Expected — the dead-rule audit happens after U6.

---

## 4. Phase U1 — Core components — **PARTLY SHIPPED**

**Outcome:** Same pages, same structure, but they stop looking like a spreadsheet.

| Step | Task | Status |
|---|---|---|
| U1.1 | Buttons per §2.6 — `.btn-primary`, `.btn-secondary`/`.btn-outline`, `.btn-correct`, `.btn-danger`, `.btn-streak`, `.btn-sm`/`.btn-lg`/`.btn-block`, `min-height: var(--tap-min)` | **Done** |
| U1.2 | **Card variants.** Panels, problem card and topic cards de-bordered and re-elevated; topic cards got hover-lift + press | **Partly** — the named `.card` / `.card-raised` / `.card-tinted` vocabulary is not built yet; existing classes were restyled in place |
| U1.3 | **Kill the header strip.** `.section-panel-header` is now an in-flow `1.375rem/700` heading instead of a tinted bar | **Done** |
| U1.4 | `.profile-stat-card` — `--text-3xl/800` number, muted label, left accent bar with `--streak`/`--correct`/`--xp`/`--social` modifiers | **Done** (modifiers not yet wired into `profile.html` — that is U4.4) |
| U1.5 | Form controls — sunken fill instead of white+border, 2px brand focus ring, uppercase labels, 44px min height | **Done** |
| U1.6 | `.pill` unified — replaces `.hero-pill`, `.feed-filter-pill`, `.profile-reflection-filter`, `.badge-*` which are four near-identical implementations | Open (badges and hero pills restyled; not yet unified) |
| U1.7 | `.list-row` — replaces `.profile-list-item`; hover tint, no bottom border, chevron affordance when it links somewhere | Open |
| U1.8 | MCQ options — `--radius`, 2px border that becomes brand/green/red, press edge, tick/cross so colour is not the only signal | **Done** (letter chips A/B/C/D still open; needs markup changes in `site.js`) |
| U1.9 | Avatars — keep emoji, add `--elev-1` ring and size scale | Open |

**Also shipped:** `h1`–`h4` defined globally (only `h1`/`h2` existed before) and
moved to the sans face at heavier weights; serif retained for question prose. A
global `prefers-reduced-motion` block (U7.2, pulled forward) now gates every
transform and `scroll-behavior: smooth`, which was previously ungated.

**Token added during implementation:** `--edge` (`#c3d0de`). `--border` was too
light to read as a press affordance on neutral buttons and topic cards.

**Deliverable check:** `/styleguide` shows every component; `/topics` and `/profile` visibly improve with zero template changes beyond class renames.

---

## 5. Phase U2 — Mobile app shell

**Outcome:** The single biggest perceived change. The app stops being "a website with a hamburger".

### U2.1 Bottom tab bar

Fixed, 5 items, `64px` + `--safe-bottom`, `--elev-3` upward shadow, `--surface`.

| Tab | Icon | Route | Badge |
|---|---|---|---|
| Practice | lightning / pencil | `/` | — |
| Learn | book | `/topics` | — |
| Daily | calendar-star | `/qotd` | red dot if today unanswered |
| Compete | trophy | `/leaderboard/friends` | count of pending challenges |
| Profile | avatar emoji | `/profile` | streak flame if at risk |

- Authenticated only. Logged-out gets Practice / Learn / About / Log in.
- Active state: brand icon + label + a `3px` top indicator bar.
- Hide on scroll-down, reveal on scroll-up (respect `prefers-reduced-motion`: never hide).
- `.site-wrapper` bottom padding becomes `calc(64px + var(--safe-bottom) + var(--space-4))`.
- Study buddy FAB repositions above the bar.
- Desktop (`≥900px`): tab bar hidden, replaced by a **persistent horizontal nav** in the header — same five destinations, always visible. The hamburger keeps only secondary items (Settings, Suggestions, Feed, About, Log out).

New: `static/js/tab-bar.js` (~60 lines), markup in `base.html`, icons as inline SVG (see U5.6).

### U2.2 Header simplification

Mobile header keeps: title/logo, search, notifications. Everything else moves to the tab bar or the menu. Reduce height to `56px`.

### U2.3 Page transitions

Subtle `opacity` + `4px` translate on load via a `.page-enter` class. No SPA router — a CSS animation on `.page-shell` is enough and costs nothing.

---

## 6. Phase U3 — Gamification layer

### U3.1 Streak ring

Replace the streak number-in-a-box. SVG ring (`stroke-dasharray` progress toward the next milestone: 7 / 30 / 100), flame glyph centred, day count in `--text-4xl`, and **7 day-dots** underneath showing the last week (filled = studied, `❄️` = frozen, hollow = missed). This directly surfaces the E5.4 freeze feature, which currently only appears as a line of text.

Placement: top of `/profile`, compact variant in the header on mobile.

### U3.2 XP / effort points

The data already exists — `friend_effort_leaderboard` computes a `score`. Surface it as **XP**:
- XP number in the profile hero next to the streak.
- `+10 XP` floating toast on a correct answer, animating upward and fading.
- A level ring derived from cumulative XP (level = `floor(sqrt(xp/50))` or similar) — no schema change, computed from existing activity events.

*Decision needed:* whether "XP" is acceptable product language or whether it should be "effort points" to stay academically framed. Recommend **XP** — the audience is teenagers and the whole point is game feel.

### U3.3 Badge redesign

Milestones become **hexagonal or shield medallions** with tier colours (bronze / silver / gold / violet for rare), emoji centred, a subtle inner gradient, and locked badges shown as greyed silhouettes with the unlock condition. Grid, not a list. Earning one triggers U7 celebration.

### U3.4 Answer feedback

- **Correct:** option turns green, scale-pop `1 → 1.04 → 1`, checkmark path draws in, `+XP` toast, optional confetti burst for a streak of correct answers.
- **Wrong:** shake `4px` twice, red tint, the correct option gently highlights.
- Both gated on `prefers-reduced-motion` (colour still changes; motion does not).

### U3.5 Topic mastery rings

`.topic-card` on `/topics` gains a small progress ring (lesson steps completed + quiz accuracy). Turns the topic index from a link list into a map of progress. Data exists via `lesson_progress` and `quiz_attempts`.

---

## 7. Phase U4 — Page-by-page

Format: **problem → treatment**. Mobile layout described first.

### 7.1 `/` — Practice generator (`index.html`)

**Problem:** Hero, then a five-field form card, then maybe a question. The form dominates; the question is the point.

**Treatment**
- Hero shrinks to a one-line greeting + streak/XP chip row.
- Form collapses to a **single "What do you want to practise?" card** with the current selection shown as pills (`GCSE · Maths · Surds · Medium`). Tapping a pill opens a bottom-sheet picker rather than showing five selects at once. Keeps the existing cascade JS; changes the presentation.
- A prominent `.btn-primary btn-lg` **Start practising**.
- Once generated, the question becomes the hero: `.card-quiz`, full-bleed on mobile, difficulty pill top-right, actions in a sticky bottom bar (Check / Hint / Skip).
- "Recently practised" horizontal scroll strip of topic chips for one-tap repeat.

### 7.2 `/topics` — Topic index (`topics.html`)

**Problem:** Flat grid of identical text cards; no sense of progress or path.

**Treatment**
- Level/subject as a sticky segmented control (GCSE / A-Level / MYP).
- Subject sections with a coloured header and subject icon.
- `.topic-card` becomes: topic icon, name, mastery ring (U3.5), and a `Continue` / `Start` verb. Two-column on mobile ≥360px, three on tablet, four on desktop.
- Skill-tree / path layout is **in scope** (decision §14), split as follows:

#### U4.2a — Syllabus order in `topic_registry.py` (separate reviewed change)

**Do this first. Do not mix it into a CSS or template PR.**

`topic_registry.py` today is a nested dict of generators. Topics have no teaching order and no prerequisites, so a Duolingo-style path cannot be drawn without inventing sequence in the template.

| Field | Purpose |
|---|---|
| `order` | Integer within a `(level, subject)` group — the vertical position on the path |
| `prereqs` (optional) | List of topic slugs that should be suggested first; UI-only in v1, not a hard lock |

Rules:
- Data-only: `topic_registry.py` plus any helper that already reads `TOPICS`. No CSS, no new tables, no generator changes.
- Own commit, own review. Smoke: every registered topic has an `order`; orders are unique per `(level, subject)`; existing generate / topic-page / quiz routes still resolve.
- Existing consumers (`app.py`, `models/buddy.py`, `models/qotd.py`, `models/lesson_search.py`) must keep working if `order` is absent — treat it as optional until U4.2b ships, then require it.

#### U4.2b — Path UI (after U4.2a)

Vertically connected nodes on `/topics`, grouped by subject, using the registry `order`. Blocked on U4.2a. Can ship after the rest of U4 chrome.

### 7.3 `/topic/...` — Lesson page

**Problem:** 40 bespoke templates with inline styles; gradient hero; long accordion stack.

**Treatment (U4 scope — chrome only; content unification is U6)**
- Sticky top progress bar showing % of sections completed (the vertical rail at `base.html` 644–728 is hidden below 960px, so mobile currently has *no* progress indicator).
- Accordion sections become `.card` with a number chip, title, and a completion tick.
- Sticky bottom CTA: **Take the quiz** with the question count.
- On completion of all sections: a celebration and an XP award.

### 7.4 `/profile` — Dashboard (`profile.html`)

**Problem:** The worst offender — **18 stacked sections**. Nothing is findable.

**Treatment**
- **Hero:** avatar, handle, streak ring (U3.1), XP/level, badges earned count.
- **Tabs** (client-side, no route change): **Overview · Progress · Social · History**.

| Tab | Contains |
|---|---|
| Overview | Streak ring, this-week stats, Due today, study buddy, pending invites |
| Progress | Topics to revisit, revision plan, skill patterns, mastery grid, reflections |
| Social | Buddy, challenges, suggestions, friend leaderboard snippet |
| History | Saved questions, lesson bookmarks, practice history, quiz history |

- Each tab is a `<section>` toggled by an ARIA tablist; deep links via `#overview` etc. so existing anchors (`#milestones`, `#revision-plan`, `#study-buddy`, `#reflections`) still resolve — **required**, the buddy widget and notifications link to these.
- History lists get virtualised-feel treatment: show 5, "Show more" reveals the rest.

### 7.5 `/u/<handle>` — Public profile

- Hero with large avatar, handle, and a **badge shelf** (top 5 medallions).
- Stats as three `.stat-card`s (streak / topics / accuracy) respecting the existing privacy settings.
- Action row: Follow / Challenge / Study buddy as `.btn-lg` full-width on mobile.
- Progress and recent quizzes as compact `.list-row`s.

### 7.6 `/qotd` — Question of the day

**Problem:** Looks like every other page. It should feel like a daily event.

**Treatment**
- Distinct **daily card** with date, a countdown to reset, and a stronger accent (violet/gold rather than brand blue).
- Answered state shows a large tick/cross, the solution, and the friend board immediately.
- Today/Week toggle as a segmented control.
- Leaderboard rows: rank medallion (gold/silver/bronze for 1–3), avatar, handle, correct-days as filled dots.
- A 7-day strip of your own results at the top.

### 7.7 `/leaderboard/friends`

- Podium treatment for the top 3 (raised centre, medallions), list for 4+.
- Viewer row pinned and highlighted.
- Effort/Accuracy as a segmented control.
- Empty state with a **Find friends** CTA — currently a bare list.

### 7.8 `/challenges`, `/challenges/new`, `/challenges/<id>`

- Challenge cards show both avatars facing each other with a `VS` divider, status pill, and score when complete.
- Pending-your-move challenges float to the top with an amber accent.
- `challenge_detail` gets a quiz-runner layout matching the lesson quiz (U4.9) plus a head-to-head result screen with per-question comparison.

### 7.9 `/lesson-quiz/...` and `/quicktest`

- **Full-screen quiz mode:** hide the tab bar, show a top bar with a segmented progress indicator (one segment per question, filled green/red as answered), question counter, and an exit `×`.
- One question per screen, large MCQ options, bottom-anchored Check.
- Results screen: score ring, accuracy, XP earned, per-question review list, **Retry wrong ones** CTA.
- This fixes the `#2563eb` colour drift in `lesson_mcq_quiz.html`.

### 7.10 `/feed`

- Feed cards get an actor avatar, a coloured type icon, and relative time.
- Bot/QOTD card visually distinct (violet accent).
- Filter pills become a segmented control.
- Empty state: **Follow someone to see activity**.

### 7.11 `/saved-problems`, `/suggestions`, `/search`, `/u/.../followers`

Shared treatment: `.list-row` with avatar/icon, two-line content, right-aligned meta, swipe-free but with an explicit action button. Real empty states with an illustration (U5.7) and a CTA.

### 7.12 `/login`, `/register`

- Centred single card, large inputs, brand gradient background panel.
- Register: inline validation, a password strength meter, and the age confirmation as a clear checkbox row.
- These are the first thing a new user sees and currently look the most generic.

### 7.13 `/profile/settings`

- Group into `.card` sections with clear headings: Account, Avatar, Privacy, Sharing, Email, API tokens.
- Avatar picker becomes a proper grid with locked extras shown as greyed with unlock captions (E5.5 already does the logic).
- Toggles become real switch controls, not bare checkboxes.

### 7.14 `/about`, `/offline`, `/email/unsubscribe`, error pages

- `/about`: feature cards with icons, a short "how it works" 3-step strip.
- `/offline`: friendly illustration + retry button.
- Add styled `404`/`500` templates if none exist.

---

## 8. Phase U5 — Graphics and diagrams

### 8.1 The problem

~130 hand-written inline SVGs across 36 lesson templates plus 17 generator modules emitting SVG, with no shared palette, stroke weight, label typography, or accessibility convention. Fixed `width="520"` in some places, `100%` in others. Many lack `role="img"`/`<title>`.

The user's specific example — the **cylinder and circle** in `gcse_maths_mensuration_lesson.html` (241–280, 87–91) — is representative: the cylinder is a rectangle with two flat ellipses and no shading, so it reads as a flat lozenge rather than a solid.

### 8.2 `svg_kit` — a shared diagram library

Create **`models/svg_kit.py`** (importable by both generators and a Jinja global) exposing:

```python
PALETTE = {...}            # maps to the CSS tokens
def svg(width, height, *, title, body): ...       # wrapper: viewBox, role="img", <title>, <desc>
def cylinder(r_label, h_label, *, shaded=True): ...
def cone(...); def sphere(...); def cuboid(...); def prism(...)
def circle_with_radius(...); def sector(angle, ...); def annulus(...)
def right_triangle(...); def number_line(...); def pie_chart(parts)
def bar_chart(...); def box_plot(...); def venn2(...); def prob_tree(...)
```

Rules for every primitive:
- Always `viewBox`, never a fixed pixel `width` — sizing is CSS (`width:100%; max-width:<n>px`).
- Stroke `2px` for outlines, `1.5px` for measurement lines, `1px` dashed for hidden edges.
- Labels: `font-size: 14`, `font-weight: 600`, `text-anchor` explicit, measurement labels in the red accent, shape labels in ink.
- `role="img"` + `<title>` + `<desc>` mandatory. Decorative-only elements get `aria-hidden`.
- One `<defs>` block of gradients reused across primitives.

Then **replace call sites**: `generators/gcse/maths_mensuration.py` (`_rect_svg`, `_triangle_svg`, `_circle_svg`, `_cuboid_svg`, `_sector_svg`, lines 116–185), `maths_num_stats_prob_rat.py`, `maths.py`, `geometry_angles.py`, `maths_circle_theorems.py`, `maths_bearings.py`, `maths_pythagoras.py`, `maths_compound_measures.py`, and the A-level physics modules.

### 8.3 Fixing the tube specifically

A convincing textbook cylinder needs four things the current one lacks:

1. **A body gradient** — `linearGradient` left-to-right: `#c8e4f8 → #eaf6ff → #b8dcf5`, which is what makes a rectangle read as curved.
2. **A dashed hidden back edge** — the rear half of the bottom ellipse drawn dashed. This is the standard convention and is *pedagogically* correct, not just prettier.
3. **A lighter top ellipse** with a thin highlight arc.
4. **Consistent labelling** — `r` on the top radius with an arrowed measurement line, `h` on a vertical dimension line outside the solid with tick serifs.

The same treatment applies to the cone, sphere, and the composite silo (423–453), and to `_cuboid_svg` in the generator.

**Also add a cylinder to the generator.** Today the lesson shows a cylinder but `maths_mensuration.py` emits no cylinder diagram at all, so practice questions are text-only — the biggest lesson↔practice mismatch found in the audit.

### 8.4 Missing visuals worth adding

| Gap | Add |
|---|---|
| Pie charts discussed but never drawn (statistics lesson; `_stats_pie_angle` generator) | **Done** — `pie_chart()` + `_stats_pie_angle` |
| Fractions have no part-of-whole visual | **Done** — `fraction_bar()` + `fraction_pie()` (FDP lesson + styleguide) |
| No progress charts anywhere | **Done** — see 8.5 (U5.9) |
| No topic icons | **Done** — see 8.6 |

### 8.5 Progress visualisation (new)

Pure SVG, no charting library (consistent with `docs/POTENTIAL_FUTURE_FUNCTIONALITY.md` deferring Chart.js).

- **Streak calendar** — 7×N dot grid, filled/frozen/missed, on `/profile` → Progress.
- **Accuracy sparkline** — last 10 quizzes, on profile and quiz results.
- **Mastery ring** — reusable, powers U3.5 topic cards and the level ring.
- **Weekly effort bars** — 7 bars for the current week, on the profile Overview.

### 8.6 Icon system

Currently there are 4 inline nav SVGs and everything else is emoji. Emoji are fine for avatars/buddy/badges (they carry personality and cost nothing), but UI chrome needs a real set.

- Build `templates/partials/icon.html` — a Jinja macro `icon('book', size=24)` reading from a single inline `<symbol>` sprite injected once in `base.html`.
- ~24 icons: tab bar (5), nav (search, bell, menu, close, chevrons), actions (save, share, retry, hint, check, cross), status (flame, trophy, target, lock, star).
- Stroke-based, `2px`, `currentColor`, `24×24` grid. Hand-draw or adapt an MIT/ISC-licensed set — **record the licence in the file header**.
- Add one **topic/subject icon** per subject (maths, physics, CS, chemistry) for `/topics`.

### 8.7 Brand assets

- A proper wordmark/logo lock-up to replace the plain text `.site-title`.
- Redraw the 3 PWA icons from it (`icon-192`, `icon-512`, `icon-maskable-512`) — currently the only raster art in the repo.
- A `favicon.ico` / `favicon.svg` (none exists).
- 2–4 simple spot illustrations for empty states (no results, no friends, offline, all caught up). Flat, two-tone, brand palette, SVG.
- **Mascot:** **Done (U5.8)** — custom SVG buddy with seven faces matching `BUDDY_FACES`, swapped via `data-buddy-face`.

**U5 shipped 2026-08-24:** `models/svg_kit.py` (U5.1–U5.5, U5.9), icon sprite (U5.6), brand lock-up / PWA / empty-state spots (U5.7), mascot (U5.8). Lesson inline SVGs stay on U6.

---

## 9. Phase U6 — Lesson template unification

**Outcome:** 40 lesson templates stop being 40 different websites.

**Why it is risky:** these files contain the actual teaching content, heavy inline styles, `<details>` structures that `lesson-progress.js` depends on, and inline MCQs that `site.js` wires up. A careless rewrite breaks lessons *and* progress tracking.

**Approach**

| Step | Task |
|---|---|
| U6.1 | **Shipped.** Lesson component vocabulary in `pages.css`: `.lesson-hero`, `.lesson-section`, `.lesson-subsection`, `.lesson-callout--{note,warning,exam,formula}`, `.lesson-example`, `.lesson-quickcheck`, `.lesson-quickref`. Remaining lessons still inline-styled. |
| U6.2 | **Shipped.** Converted `gcse_maths_mensuration_lesson.html` by hand (`.lesson-shell`, no inline `style="`). Progress / Quick Check / quiz CTA contracts kept. Smoke: `scripts/test_lesson_unify_smoke.py`. |
| U6.3 | **Shipped.** `scripts/migrate_lesson_styles.py` — idempotent, **dry-run by default**. Maps known inline-style signatures onto the U6 classes and prints leftovers. Radioactivity is a converted lesson (U6.6), not a migrator skip. Smoke: `scripts/test_migrate_lesson_styles_smoke.py`. |
| U6.4 | **Shipped.** Applied migrator to 38 lessons (mensuration already clean; radioactivity skipped). Teaching copy / `.mcq-inline` / `data-correct` / `<details>` counts unchanged vs pre-apply. Leftover unmatched `style=""` remain (constructions/loci, A-level, a few one-offs) — do not strip those by hand in U6.5. Attribute-selector compensation stays until U6.5. |
| U6.5 | **Shipped.** Removed `div[style*="max-width:860px"]` compensation from `pages.css` / `responsive.css` (the spec’s old `base.html` line numbers — those rules had already been extracted). Nested CS `.lesson-inner` is styled under `.lesson-shell`. Progress JS finds `.lesson-shell` then `.page-shell` only. Cache: `pb-v56`. |
| U6.6 | **Shipped.** `gcse_physics_radioactivity_lesson.html` extends `base.html`, uses `.lesson-shell` / U6 classes (no standalone `:root` or page CSS). Route and lesson API pass `p1`–`p3` via `_lesson_render_spec`. Cache: `pb-v57`. |
| U6.7 | Delete the 5 legacy unrouted stubs (`gcse_maths_surds.html`, `gcse_maths_fdp.html`, `gcse_maths_decimals.html`, `gcse_maths_bidmas.html`, `gcse_combined_physics_radioactivity.html`) after confirming no route reaches them |
| U6.8 | Move the two stray `.py` files out of `templates/` |

**Guard:** add a smoke test that loads every lesson route, asserts HTTP 200, asserts the expected number of `<details data-lesson-section>` elements, and asserts no inline `style="` remains in migrated files.

---

## 10. Phase U7 — Motion and delight

| Step | Task |
|---|---|
| U7.1 | Motion tokens: `--dur-fast 120ms`, `--dur 200ms`, `--dur-slow 400ms`, `--ease-out`, `--ease-spring` | **Done** (in `tokens.css`) |
| U7.2 | A global `@media (prefers-reduced-motion: reduce)` block that disables transforms/animations and `scroll-behavior: smooth` | **Done** (`base.css`; JS `scrollIntoView` gated in `u4.js` / `lesson-progress.js`) |
| U7.3 | Correct-answer celebration: scale-pop + checkmark draw + `+XP` float | **Done** (MCQ + generator check; `celebrate.js`) |
| U7.4 | Confetti on milestone/badge/streak-round-number — CSS particles, no library, ~40 elements, self-cleaning | **Done** (buddy `milestone` prompt; streak 7/30/100 on nav + profile ring; once per key via localStorage) |
| U7.5 | Streak ring fill animation on profile load | **Done** |
| U7.6 | Skeleton loaders for feed, notifications, and leaderboards instead of "Loading…" text | **Done** |
| U7.7 | Toast redesign — icon + message + optional action, slide + fade, stacking | **Done** (`.app-toast` stack; flash messages hydrate via `pb-flash-data`) |
| U7.8 | Buddy: idle bob, reaction on refetch | **Done** (CSS bob on `.buddy-mascot`; `.is-reacting` hop after `pb-buddy-refetch`) |
| U7.9 | **Optional sound** — short correct/incorrect/celebrate clips, default **off**, toggle in settings, `<audio>` preloaded. Recommend shipping muted-by-default; a school-context app that makes noise unprompted is a problem. | Open |

---

## 11. Phase U8 — Accessibility, performance, QA

| Step | Task |
|---|---|
| U8.1 | Contrast audit — every text/background pair ≥ 4.5:1 (the new saturated accents need checking, especially amber on white) |
| U8.2 | Focus-visible rings on every interactive element; tab order verified on the new tab bar and profile tabs |
| U8.3 | Profile tabs as a proper ARIA tablist; bottom tab bar as `<nav>` with `aria-current="page"` |
| U8.4 | Every diagram has `role="img"` + `<title>`; decorative SVG `aria-hidden="true"` |
| U8.5 | Colour is never the sole signal — correct/wrong also carry an icon |
| U8.6 | CSS budget: total shipped CSS < 60KB uncompressed; audit for dead rules after U6 |
| U8.7 | `content-visibility: auto` on long profile/lesson sections |
| U8.8 | Re-run the `docs/MOBILE.md` device QA matrix at 360/390/430px and 768/1280/1920px |
| U8.9 | Update `docs/ARCHITECTURE.md`, `docs/ENGAGEMENT_VISUAL.md` (it currently pins the old palette), and `docs/AI_HANDOFF.md` |
| U8.10 | Full smoke suite green; `CACHE_VERSION` bumped |

---

## 12. Risks and mitigations

| Risk | Mitigation |
|---|---|
| CSS extraction (U0) silently changes cascade order | Split in load order; before/after screenshots at two widths; U0 must be visually a no-op |
| Service worker serves stale CSS | Bump `CACHE_VERSION` **and** `?v=` every phase; add CSS to `PRECACHE_URLS`; U0.10 smoke check |
| Profile tabs break existing anchor links | `#milestones`, `#revision-plan`, `#study-buddy`, `#reflections` must auto-open their tab — the buddy widget and notification links depend on them |
| Lesson migration (U6) breaks progress tracking | Convert one by hand first; keep `data-lesson-section` contracts; add a per-lesson smoke test |
| Redesign drifts into behaviour changes | Phase U touches CSS/templates/presentational JS only. No generator, grading, API, or schema changes. If a phase needs one, stop and spec it separately. |
| Saturated palette hurts contrast | U8.1 gate before ship |
| Scope explosion | Each phase ships independently and leaves the app in a coherent state |

---

## 13. Definition of done

- [x] `static/css/` exists; `base.html` `<style>` block removed; no hex values outside `tokens.css` *(diagram/lesson hex remains until U6)*
- [x] `/styleguide` renders every component and diagram primitive
- [x] Bottom tab bar on mobile; persistent nav on desktop
- [x] Streak ring, XP, badge medallions, answer celebration shipped *(U5.9 rings/charts; U7.3 celebration; U7.5 ring fill)*
- [x] U4.2a shipped as its own commit (`order` on every `TOPICS` entry); U4.2b path UI only after that
- [x] Every page in §7 redesigned
- [x] `models/svg_kit.py` exists; mensuration solids (incl. the cylinder) redrawn; generator cylinder added
- [x] Icon sprite + topic icons + empty-state illustrations
- [ ] All 40 lesson templates on the component system; no inline `style="` in lesson content *(U6)*
- [x] `prefers-reduced-motion` respected globally *(U7.2)*
- [ ] Contrast audit passed; smoke suite green; `CACHE_VERSION` bumped *(U8)*
- [x] `docs/ARCHITECTURE.md`, `docs/ENGAGEMENT_VISUAL.md`, `docs/AI_HANDOFF.md` updated *(U5 close-out 2026-08-24)*

---

## 14. Decisions (settled 2026-08-20)

| # | Decision | Call | Affects |
|---|---|---|---|
| 1 | Game language | **"XP" and levels** — teenage audience, game feel is the point | U3.2 |
| 2 | Palette | **Keep blue as brand, saturate it, add energy accents** (amber streak, green correct, violet XP). No brand-colour rethink. | §2.2, U0.2 |
| 3 | Mascot | **Custom SVG mascot** replaces the emoji buddy, with expressions matching `BUDDY_FACES` | U5.7 |
| 4 | Topic path | **Skill-tree / path layout is in scope.** Split: **U4.2a** = `order` (and optional `prereqs`) on `topic_registry.py` as a **separate reviewed, non-CSS change**; **U4.2b** = path UI, blocked on U4.2a. | U4.2a then U4.2b |
| 5 | Sound | **In scope, default off**, toggle in settings | U7.9 |
| 6 | Dark mode | Out of scope for Phase U, but tokens must make it a single-file addition later | U0.2 |
| 7 | Starting point | **U0 + U1** | — |

### Consequences

- **U4.2a is a separate reviewed change, not part of any CSS phase.** The skill tree needs a syllabus order that `topic_registry.py` does not have. Spec: §7.2. Sequence: U4.2a (data, own commit) → rest of U4 chrome → U4.2b (path UI). Do not fold registry edits into U0–U3 or a stylesheet PR. This is the only Phase U item that is allowed to touch non-presentational code.
- **U5.7 is promoted from stretch to committed.** The mascot needs 6 expressions (`milestone`, `celebrate`, `qotd_nudge`, `streak_risk`, `weak_topic`, `friend_challenge`) plus the `nudge` default, delivered as a single inline SVG sprite with swappable face paths so the existing `data-buddy-face` API in `static/js/buddy.js` keeps working.
- **U7.9 needs an asset decision and a settings field.** Three short clips (correct / incorrect / celebrate), CC0 or self-generated, plus a `sound_enabled` boolean on `user_profile_settings`.
