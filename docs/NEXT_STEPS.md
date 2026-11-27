# Next steps: checklist for Claude Code

Copy one item at a time into Claude Code. Each item names the files it touches.

## A + B. Setup and small fixes: DONE (27 Nov 2026)

- [x] Moved to repo `greyyuri97/my-life-hub`; live at https://greyyuri97.github.io/my-life-hub/
- [x] Smoke test passes (reads APP_PIN from local .env)
- [x] Settings text now says data syncs to Google Sheet
- [x] "Coming soon" tab removed
- [x] Local `apps-script/Code.gs`: `setup()` no longer writes a default PIN (paste into Apps Script when convenient)
- [ ] Give the Apps Script deployment a description at the next redeploy
- [ ] Turn off Pages on the old repo `netflixhafiz97/life-hub` (log in as that account)

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
