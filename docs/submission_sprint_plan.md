> **⚠️ This is Claude-generated content.**
> Author: Claude (Anthropic) — generated for the IBM BOB Devday Hackathon submission sprint.
> Date: 2026-05-03

# Submission Sprint — Prompt Pack (3-Hour Plan)

**Today is 2026-05-03. Deadline 10:00 AM ET (7:30 PM IST).**

Below is a time-boxed sequence. Each box has a copy-pasteable Bob prompt. **Do not deviate** — every minute spent on extras is risk.

---

## Decision Gate Before You Start (5 min)

Answer these honestly:

| Question | If YES | If NO |
|---|---|---|
| Does `npm run web` show a working app end-to-end? | Continue to Phase A | Skip deploy entirely. Go straight to Phase C (record local demo) |
| Can backend run on `python manage.py runserver`? | Continue | Fix this first or demo offline |
| Have you ever deployed Django + Expo Web before? | Try deployment (Phase B) | Skip deployment. Per the plan: *"DO NOT deploy if unfamiliar."* |

> **If any answer is NO, drop deployment.** A clean local demo video beats a broken live URL.

---

## Phase A — Stabilize the Build (T-180m → T-150m, 30 min)

### Prompt A1 — Smoke test + freeze

```
Working dir: Chatsift/ChatSift.
Mode: STABILIZE ONLY. No new features. No refactors.

Tasks:
1. cd backend && python manage.py migrate && python manage.py runserver
   Confirm /api/v1/auth/login/ returns 200 for a seeded user.
2. cd frontend/chatsift-frontend && npm run web -- --port 3000
   Walk the golden path: Register → Email verify (use console-printed link) →
   Login → Dashboard → Integrations (Telegram bot-token connect with a real
   test bot or skip Discord) → Settings → Logout.
3. Report a punch list of ANY broken step in <150 words.
4. For each broken step, propose the SMALLEST possible fix. Do not implement
   unless I approve.

Do not touch styling, animations, or "Coming Soon" screens.
```

### Prompt A2 — Apply only blocker fixes

```
From the punch list, fix ONLY items that block the golden path. Skip warnings,
console errors that don't break flow, and cosmetic issues. Time budget: 20 min.
If a fix takes longer, stub the broken screen with a graceful "Demo unavailable"
state instead. Stop and report when done.
```

---

## Phase B — Deployment (T-150m → T-105m, 45 min) — OPTIONAL

> **Skip this entire phase** if Phase A took longer than 30 min, or if you've never deployed Django before. A local demo video is fully acceptable per the rules.

### Prompt B1 — Frontend to Cloudflare Pages (fastest, ~15 min)

```
Working dir: Chatsift/ChatSift/frontend/chatsift-frontend.
Goal: Publish Expo web build as a static site.

Tasks:
1. Set API base URL via env: in src/api/client.ts, replace hardcoded
   'http://localhost:8000/api/v1' with
   `process.env.EXPO_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1'`.
2. Add `.env.production` with EXPO_PUBLIC_API_BASE_URL=<TBD — fill after backend deploy>.
3. Run `npx expo export --platform web` → produces dist/.
4. Tell me the exact `wrangler pages deploy dist --project-name chatsift`
   command to run, and the manual Cloudflare dashboard alternative.

Do not deploy yet — I'll set the backend URL first. Stop after the export
succeeds locally.
```

### Prompt B2 — Backend to Render (~20 min)

```
Working dir: Chatsift/ChatSift/backend.
Goal: Deploy Django + SQLite to Render free tier (NOT production-grade,
just judge-accessible per hackathon rules).

Tasks:
1. Add render.yaml with:
   - Web service: python build + gunicorn Infobyte.wsgi
   - Build command: pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
   - Env vars: SECRET_KEY, FIELD_ENCRYPTION_KEY, DEBUG=False
2. Patch Infobyte/settings.py:
   - ALLOWED_HOSTS = ['*'] (hackathon-only — flag this)
   - CORS_ALLOWED_ORIGINS += ['<frontend-url-tbd>']
   - Add whitenoise to MIDDLEWARE for static files.
3. Add gunicorn + whitenoise to requirements.txt.
4. Give me the exact git commands to push and the Render dashboard steps.

Do NOT switch to PostgreSQL — too risky in 20 min. SQLite ephemeral is fine
for a demo URL.
```

### Prompt B3 — Wire and verify

```
After Render gives me a URL like https://chatsift.onrender.com:
1. Update frontend .env.production with that URL + /api/v1.
2. Re-run expo export, redeploy to Cloudflare.
3. Update backend CORS_ALLOWED_ORIGINS with the Cloudflare Pages URL,
   redeploy backend.
4. Test live: register, login, list integrations.
5. Report the two URLs and confirm the golden path works on the live site.

If anything breaks, ROLLBACK to local-only demo. Do not debug past 15 min.
```

---

## Phase C — Demo Video (T-105m → T-60m, 45 min)

### Prompt C1 — Demo script

```
Source: AI_IMPLEMENTATION_PROMPT.md + README + Last 3 Hour Checklist §5.
Constraint: 3 minutes max, judge-readable.

Write a tightly-timed script with on-screen actions and voiceover lines:
- 0:00–0:20  PROBLEM: information overload in Discord/Telegram groups.
- 0:20–0:40  SOLUTION: ChatSift = AI daily digests, selective monitoring.
- 0:40–2:20  DEMO walking through: Login → Connect Telegram → Dashboard
             → Integration detail (channels) → Settings. Narrate what each screen does.
- 2:20–2:45  IBM BOB USAGE: planning (FRONTEND_MASTER_PLAN.md), API contract
             extraction from backend, multi-phase code generation, prompt rewriting.
- 2:45–3:00  IMPACT + close.

Output: a numbered shot list with timestamps, voiceover lines (≤2 sentences each),
and on-screen action notes. No filler.
```

### Recording tooling (do this yourself, not via Bob)

- **Loom** ([loom.com](https://loom.com)) → free, instant public URL, no editing. **Best choice.**
- **Backup:** OBS → upload to YouTube as Unlisted.
- Test the URL in incognito before moving on.

---

## Phase D — Written Deliverables (T-60m → T-30m, 30 min)

### Prompt D1 — All written statements + README in one shot

```
Working dir: Chatsift/ChatSift.
Source: README.md, AI_IMPLEMENTATION_PROMPT.md, FRONTEND_MASTER_PLAN.md,
backend/BACKEND_ARCHITECTURE.md, AGENTS.md, the Last 3 Hour Checklist §6.

Generate ALL of the following as separate files, in one turn:

1. SUBMISSION/problem.md — Problem statement using the template:
   "Our project addresses [problem] for [target users]. Today, users struggle
   with [pain point]. This matters because [impact]." 100–150 words.

2. SUBMISSION/solution.md — Solution statement using the template:
   "We built ChatSift to allow users to [main action]. The user can [step 1],
   [step 2], and receive [result]." 100–150 words.

3. SUBMISSION/bob_usage.md — "How we used IBM Bob": 5 bullet points naming
   specific uses (frontend planning, API contract extraction, multi-phase
   code generation, prompt engineering, debugging). Each bullet cites a
   concrete artifact (e.g., FRONTEND_MASTER_PLAN.md, the backend URL bug
   we caught). 200 words max.

4. README.md — REPLACE existing. Sections required:
   - Title + tagline
   - Problem / Solution (1 paragraph each)
   - Tech Stack (concrete versions)
   - How to Run (backend + frontend, 6–8 commands total)
   - Demo Flow (numbered, matches the video)
   - IBM Bob Usage (link to bob_usage.md)
   - Known Limitations (cite §9 from AI_IMPLEMENTATION_PROMPT.md:
     monitoring/summaries are Coming Soon stubs, no real email backend,
     SQLite for demo)
   - Team Members (placeholder — I will fill names)
   - Live URLs (frontend + backend, or "local-only demo — see video")
   - License

Tone: professional, no emoji, no marketing fluff. Cite real files and
real limitations — judges score on honesty + completeness.

Stop after writing these 4 files.
```

### Action D2 — Export Bob session report (manual)

In your IDE (where Bob runs), find **"Export task session"** → save as PDF.
Place at `SUBMISSION/bob_session_report.pdf`.

---

## Phase E — Final Upload + Submit (T-30m → 0, 30 min)

**Manual checklist (no prompts — do this yourself)**

1. Verify video URL in incognito + on phone. Audio audible. Text legible.
2. Verify repo URL: push everything to GitHub public; open the link in incognito.
3. Verify live URLs (if deployed): open in incognito, walk golden path one more time.
4. Open IBM Watsonx Challenge submission portal.
5. Fill the form:
   - Video URL
   - Problem statement → paste from `SUBMISSION/problem.md`
   - Solution statement → paste from `SUBMISSION/solution.md`
   - IBM Bob usage → paste from `SUBMISSION/bob_usage.md`
   - Code repo → GitHub link
   - Bob session report → upload `SUBMISSION/bob_session_report.pdf`
   - Live URL (optional) → paste if Phase B succeeded
6. Submit.
7. **Screenshot the confirmation page. Save it.**

---

## Time-Pressure Decision Matrix

| If at T-90m... | Do this |
|---|---|
| Phase A still broken | Stub broken screens, skip deploy, demo only the working flow |
| Phase B failing | Cut deployment, take 5 min to clean up, move to Phase C |
| Video re-record needed | Cut intro/outro to 10s each, keep demo segment full |
| README not done by T-45m | Use Prompt D1 with reduced scope: README + bob_usage only |

---

## Anti-Patterns to Avoid

- **Don't refactor.** Working ugly > broken pretty.
- **Don't switch databases.** SQLite to PostgreSQL on Render WILL break.
- **Don't add features in the last 90 min.** Even "tiny" ones.
- **Don't trust auto-deploys without testing in incognito.** Cookies/tokens lie.
- **Don't skip the screenshot.** Submission portals occasionally drop entries.

---

**Total time-budgeted: 180 min. Buffer: 0. Start now.**

---

*— End of Claude-generated content —*
