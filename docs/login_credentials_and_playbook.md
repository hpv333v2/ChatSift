# ChatSift — Credentials + Self-Test Playbook

**Created:** 2026-05-03 — for the IBM Bob Devday submission crunch.

---

## 🔑 Login credentials (ALL VERIFIED, READY TO USE)

### Admin user (Django admin + API)
| Field | Value |
|---|---|
| Email | `admin@chatsift.app` |
| Username | `admin` |
| Password | `AdminPass123!` |
| Role | superuser, staff, email_verified ✅ |
| Django admin URL | http://localhost:8000/admin/ |

### Demo user (for the actual demo flow)
| Field | Value |
|---|---|
| Email | `sift1@example.com` |
| Username | `sift1` |
| Password | `TestPass123!` |
| First / Last | Sift / One |
| Email verified | ✅ (so integrations are unlocked) |

> Use **sift1** for the recorded demo. Use **admin** if you need to inspect data via Django admin.

---

## 🟢 Backend status
- Server running at http://localhost:8000 (started by Claude in this session — leave the terminal open).
- All migrations applied.
- 10/12 endpoints PASS. Only `/api/v1/auth/email/verify/send/` is broken (500, email backend not configured) — but **you don't need it** because both users are already pre-verified above.

---

## 🧪 Your self-test (no Claude budget, ~10 min total)

Open the frontend in a browser:

```bash
cd Chatsift/ChatSift/frontend/chatsift-frontend
npm start
# press w
```

Then walk through this order:

1. **Login as `sift1@example.com` / `TestPass123!`** → expect Dashboard.
2. **Open every nav item** (Dashboard, Integrations, Monitoring, Summaries, Settings) — note any that crash.
3. **Integrations page** — should NOT show "verify email first" (sift1 is already verified). Try Connect Discord/Telegram (OAuth may not be configured — that's OK, document it as a known limit).
4. **Settings** — try editing profile, save.
5. **Logout** → expect redirect to Login.
6. **Try reaching Dashboard URL directly while logged out** → expect redirect back to Login.

For each step, write one line in a notepad: ✅ works / ⚠️ partial / ❌ broken + one-sentence error.

If anything crashes you can't fix in 5 min: **document it as a known limitation** and move on. Do not get stuck.

---

## 🎬 After self-test passes — record demo

3-minute video, this order:
- 0:00–0:20 problem
- 0:20–0:40 solution
- 0:40–2:20 live demo: login as sift1 → navigate → show main flow → show result
- 2:20–2:45 how IBM Bob helped
- 2:45–3:00 impact + closing

Use **OBS** or **Windows Game Bar (Win+G)** or **Loom**. Test the recorded file plays in another browser before uploading.

---

## 🤖 When + how to prompt IBM Bob (saves my Claude budget)

> Use Bob inside the ChatSift workspace for the writing tasks. Don't burn Claude on copywriting.

### Order to run prompts in Bob (top → bottom, ~30 min total):

**Prompt 1 — POC status sanity check (1 min, do this FIRST)**
```
Read the ChatSift repo. Tell me in under 150 words: (a) does the main user flow work end-to-end right now, (b) is the backend reachable from the frontend, (c) what is the single most demo-breaking bug, (d) what is the smallest fix for a clean 3-minute demo. No new features.
```

**Prompt 2 — Three written statements (5 min)**
```
Using the ChatSift codebase as ground truth, draft three short submission statements: (1) Problem — what, who, why. (2) Solution — what we built, how it solves it, main user flow, final result. (3) How we used IBM Bob — concrete examples (frontend planning, code generation, debugging, API integration, test scaffolding). 4–6 sentences each. Plain language, no marketing fluff.
```

**Prompt 3 — README rewrite (5 min)**
```
Rewrite ChatSift's README so a judge can understand and run it in 60 seconds. Sections: Title, Problem, Solution, Features, Tech Stack, How to Run (backend + frontend, copy-pasteable), Demo Flow (numbered steps from the video), How IBM Bob Was Used, Known Limitations, Team. Be terse and specific.
```

**Prompt 4 — 3-minute video script (5 min)**
```
Write a 3-minute demo script for ChatSift, timed. Format: timestamp range | on-screen action | narration. Cover: 0:00–0:20 problem, 0:20–0:40 solution, 0:40–2:20 live POC demo of main flow + final result, 2:20–2:45 how IBM Bob helped (specific examples), 2:45–3:00 impact + closing. Narration must be readable aloud at normal pace within each segment.
```

**Prompt 5 — Pre-record checklist (2 min)**
```
Generate a step-by-step pre-record checklist for ChatSift's demo: prereqs (servers running, seed data — note demo user is sift1@example.com / TestPass123!), exact click sequence for the main flow, the on-screen result to highlight, audio/video sanity, and a post-record "open in incognito" verification pass.
```

**Prompt 6 — Submission preflight (2 min, run RIGHT BEFORE submitting)**
```
Generate a final pre-submit checklist for the Bob Devday portal entry. One checkbox per line. Cover: video link works in incognito, video ≤ 3:00, repo link public, README present, Bob PDF attached, problem/solution/Bob statements pasted, team list correct, deployment URL only if tested, no secrets in repo. End: "If any box is unchecked, do not submit yet."
```

> **Skip these** unless time permits: Bob deploy decision, PUNCH_LIST triage, FE→BE error tracing. Submission > polish.

---

## 🆘 When to come back to ME (Claude) — only if blocked

- App crashes with an error you can't read/fix → paste the error here, ONE message.
- Frontend can't reach backend (CORS / 404 / network error) → paste the browser console error.
- Backend dies → paste the last 30 lines of the Django terminal.

**Don't** ask me to write copy/scripts/READMEs — that's Bob's job.

---

## 📋 Final 3-hour countdown

| Time left | Do this |
|---|---|
| **Now → −2h** | Self-test (10 min) → Bob Prompts 1-3 (statements + README) (15 min) → fix any P0 bug from prompt 1 (30 min) |
| **−2h → −1h** | Bob Prompts 4-5 (script + checklist) → record demo → re-record if bad |
| **−1h → −30m** | Upload video, verify public access, attach Bob PDF, paste statements into form |
| **−30m → 0** | Bob Prompt 6 (preflight) → submit → screenshot confirmation |

---

## 🚫 Decisions already made (don't revisit)

- **Don't deploy.** Local POC + recorded video + repo + statements is the safer submission. (Per saved memory.)
- **Don't fix the email/verify/send 500 bug.** Both users are pre-verified — you don't need it for the demo.
- **Don't add new features.** Freeze.
