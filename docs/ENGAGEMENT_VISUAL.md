# Engagement visual tokens (E2–E5)

**Last updated:** 2026-08-16  
**Status:** Light tokens only — not a character bible. **E1–E3 shipped; E5.2 shipped; remaining E5 planned.**
**Companion:** `docs/AI_HANDOFF.md` §6, `docs/ENGAGEMENT_E5.md`

Avatar v1 emoji/colours below are the live picker list. Buddy v0 uses the 👾 placeholder.

---

## 1. Tone

Encouraging tutor, not childish and not corporate.

- Short, UK English. One hook line, then a clear action.
- E1 copy already shipped: “The Problem Bank bot challenges you!”
- Always label automated accounts as **bots / not a person**. No DMs. No extra PII.

## 2. Colour

Reuse `templates/base.html` tokens — do not invent a second palette.

| Token | Hex | Use |
|-------|-----|-----|
| `--primary` | `#1a6fa8` | Challenge card accent, buddy, avatar ring |
| `--primary-light` | `#eef6fc` | Badge / picker selected |
| `--primary-dark` | `#0e4e7a` | Hover / pressed |
| `--success` | `#2d7a3a` | Answered / streak-safe |
| `--hint-bg` / `--hint-border` | `#fffbf5` / `#ecd9a8` | Soft callouts |

Avatar backgrounds (E2 v1 — pick from these, check contrast with dark text `#1c2430`):

`#eef6fc` `#e8f4fd` `#eef7ee` `#fff8e6` `#fdf0f7` `#f4f6f9` `#dceaf4` `#edf7ef`

## 3. Avatar v1 (E2) — shipped, no drawings

**Format:** emoji + background colour. **No image upload / CDN.** Stored as `avatar_json` on `user_profile_settings`.

Suggested picker (trim or swap later):

- Faces: 🙂 😎 🤓 😺 🦊 🐸 🐼 🌙
- Accessories (optional second field): none, 🎓, 🎧, ⭐
- Store as small JSON on the user (e.g. `{ "face": "🙂", "bg": "#eef6fc", "extra": "" }`)

Default for new users: 🙂 on `#eef6fc`. Render with Jinja-safe text, never raw HTML from the user.

## 4. Buddy v0 (E3) — shipped placeholder

Corner widget (~56px) on logged-in pages:

- v0: emoji 👾 in a `--primary` circle (`static/js/buddy.js`)
- v1: optional SVG sprite in `static/icons/` later

Respects `prefers-reduced-motion`. Off-page **Not now** restores next UTC day; on a weak topic’s lesson page **Keep learning** hides only that card for the day. Does **not** block Check / generate if JS fails.

Message types today: `celebrate`, `streak_risk`, `weak_topic`, `nudge` (first match wins, one per page load).

## 4b. Buddy v0.5 faces (E5.1) — planned

One emoji per message type, sent by the API as `face` so the widget can change expression. Text emoji only — still no assets.

| Type | Face | Type | Face |
|------|------|------|------|
| `milestone` | 🎉 | `streak_risk` | 🔥 |
| `celebrate` | 😄 | `weak_topic` | 🤔 |
| `qotd_nudge` | ❓ | `friend_challenge` | 🤝 |
| `nudge` (fallback) | 👾 | | |

Avatar extras 🎓 / 🎧 / ⭐ become badge-gated in E5.5; locked options stay visible but disabled with an "earn X to unlock" caption. Full spec: `docs/ENGAGEMENT_E5.md`.

## 4c. Badge emoji (E5.2) — shipped

`MILESTONE_CATALOG` entries include an `emoji` field rendered on the profile milestone list (fallback ★). Buddy v0.5 (E5.1) can reuse the same glyph in the "New badge: …" line.

## 5. Safeguarding (already in E1)

- `@problem_bot` is reserved; cannot register or log in as the bot
- Profile copy: “A Problem Bank bot — not a person.”
- Friend-only leaderboards remain the E3 competition default (no global ranking of minors)

---

When changing buddy copy or avatar emoji, regenerate `.docx` via `python scripts/md_to_docx.py docs/ENGAGEMENT_VISUAL.md`.
