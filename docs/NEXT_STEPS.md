# Next steps: checklist for Claude Code

Copy one item at a time into Claude Code. Each item names the files it touches.

## A. Setup on the new computer (do first)

- [ ] Clone the site repo: `git clone https://github.com/netflixhafiz97/life-hub.git` and copy this package (CLAUDE.md, docs/, tests/, apps-script/) into it. **Don't commit `apps-script/Code.gs`** if the repo stays public (it has a default PIN in `setup()`); add `apps-script/` to `.gitignore`, or keep it in a private repo.
- [ ] Check that the local `index.html` matches the live site: `sha256sum index.html` should start with `652c995f82d32779`.
- [ ] Fill in a local `.env` from `.env.example` (Sheet ID, Script ID, Deployment ID).
- [ ] Optional: set up clasp (`npm i -g @google/clasp`, `clasp login`, `apps-script/.clasp.json`), then run `clasp pull` to confirm the live Code.gs matches this copy.
- [ ] Run `python tests/smoke_test.py`. It should end with "ALL SMOKE TESTS PASSED".

## B. Small fixes (low risk)

- [ ] **Settings text:** in index.html, change "All data is stored in this device's browser (localStorage)…" to say the data syncs to Google Sheet, and that Export is an extra backup.
- [ ] **Coming soon tab:** remove it, or keep it updated with planned sections.
- [ ] **Code.gs `setup()`:** stop writing a default PIN. Throw a message asking the owner to set `Settings!pin` by hand instead.
- [ ] Give the Apps Script deployment a description (for example "v6 TASK DH") the next time it is redeployed.

## C. Possible improvements (confirm with the owner before building)

- [ ] Refactor: Personal, Resepi and TASK DH share almost the same code. Build a generic `makeTagNotesModule({id,label,icon,tags,…})` factory so a new tagged section takes one line.
- [ ] Search bars for Daily Tasks, Personal and Dars.
- [ ] Add a "Status" (pending/done) toggle to TASK DH, like Daily Tasks.
- [ ] Let the owner change the PIN from the app: a new `changePin` server action that updates `Settings!pin`, with a matching `PIN_HASH` update.
- [ ] Security: stop caching the full data set in localStorage, or encrypt the cache with a key derived from the PIN (Web Crypto, AES-GCM + PBKDF2). Remove `PIN_HASH`, or replace it with a slow PBKDF2 hash. (Trade-off: offline use.)
- [ ] Add a GitHub Action that runs `tests/smoke_test.py` on every push.

## D. Prompt to start Claude Code

> Read CLAUDE.md and docs/SCHEMA.md. Then run the smoke test and confirm the local index.html matches the live site hash in docs/NEXT_STEPS.md. Don't deploy anything until I say so. Next, do item B1 (Settings text) and show me the diff.

## Other apps (not in this package)

These apps live elsewhere and need their own packages if you move them:
- **My_Komitmen**: https://netflixhafiz97.github.io/my-komitmen/ (GitHub Pages + Apps Script, PIN to view)
- **Jualan Kitab Darul Hikmah**: https://ahbabdarulhikmah.github.io/jualan-kitab/
- **Library Bacaan Kami**: https://ahbabdarulhikmah.github.io/library-bacaan/
