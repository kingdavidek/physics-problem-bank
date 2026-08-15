# Engagement visual tokens (E2–E3)

**Last updated:** 2026-08-15  
**Status:** Light tokens only — not a character bible. **E1 shipped** without custom mascot art.  
**Companion:** `docs/AI_HANDOFF.md` §6

Use this page **before E2 (avatars) and E3 (alien buddy)**. Do **not** block E1 on illustrations.

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

## 3. Avatar v1 (E2) — no drawings

**Format:** emoji + background colour. **No image upload / CDN.**

Suggested picker (trim or swap later):

- Faces: 🙂 😎 🤓 😺 🦊 🐸 🐼 🌙
- Accessories (optional second field): none, 🎓, 🎧, ⭐
- Store as small JSON on the user (e.g. `{ "face": "🙂", "bg": "#eef6fc", "extra": "" }`)

Default for new users: 🙂 on `#eef6fc`. Render with Jinja-safe text, never raw HTML from the user.

## 4. Buddy v0 (E3) — placeholder first

Ship a **corner widget** (~48–64px) that can later swap art:

- v0: emoji 👾 or a flat CSS circle in `--primary`
- v1: optional SVG sprite in `static/icons/` once E1/E2 are in use

Must respect `prefers-reduced-motion` and a dismiss control. Must **not** block Check / generate if JS fails.

## 5. Safeguarding (already in E1)

- `@problem_bot` is reserved; cannot register or log in as the bot
- Profile copy: “A Problem Bank bot — not a person.”
- Friend-only leaderboards remain the E3 competition default (no global ranking of minors)

---

When E2 starts, extend this file with the chosen emoji list if it changes; regenerate `.docx` via `python scripts/md_to_docx.py docs/ENGAGEMENT_VISUAL.md`.
