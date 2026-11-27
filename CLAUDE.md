# CLAUDE.md — My Life Hub

Read this first. It tells you what this project is, how it is built, the rules for changing it, and where it stands.

## 1. Project summary

**My Life Hub** is a personal, single-user life-tracking web app (English UI, Pokémon Gen 3 / Hoenn theme).

- **Live site:** https://greyyuri97.github.io/my-life-hub/ (GitHub Pages, repo `greyyuri97/my-life-hub`). Old site netflixhafiz97.github.io/life-hub is retired.
- **Owner:** one user who opens it on a phone and a laptop. Data must be the same on every device.
- **Access:** a PIN lock screen appears every time the app opens. The app re-locks after 20 minutes without activity. The PIN is kept server-side; it is **not** written in this file.

### Sections (modules)

| Tab | Module id | What it holds |
|---|---|---|
| 📋 Daily Tasks | `tasks` | Date, Item, Remark (multi-line), status: pending / done / unsuccessful |
| 📖 Quran Daily | `quran` | Date, Page, Remark |
| 🎓 Dars Syeikhuna | `dars` | Date (with day), Event, Catatan (note) |
| 🕌 Qadha Prayer | `qadha` | Remaining count per prayer (subuh, zohor, asar, maghrib, isyak), −1/+1, edit, undo |
| 📝 Personal | `personal` | Date, Note (multi-line). Not grouped by month |
| 🍳 Resepi | `recipes` | Search, Date, Recipe text (multi-line), tag: #ayam #daging #ikan #dessert #lain-lain |
| 🗂️ TASK DH | `dh` | Search, Date, Task text (multi-line), tag: #PODCAST #MAKTABAH #SHOPEE_DH #HIKAMULHIKMAH |

The header shows the "partner team" sprites: Blaziken 257, Altaria 334, Metagross 376, Gyarados 130, Gardevoir 282, Luxray 405. Wynaut (360) is the empty-state sprite. There are no Pokémon on the prayer cards.

## 2. Architecture

```
 Phone / laptop browser
 ┌───────────────────────────────┐
 │ index.html  (GitHub Pages)    │  single file: HTML + CSS + vanilla JS
 │  - lock screen (PIN)          │
 │  - modules render from state  │
 │  - localStorage cache         │
 │  - Sync: diff → push queue →  │
 │    pull every 15 s            │
 └──────────────┬────────────────┘
                │ fetch() POST text/plain JSON, credentials:'omit'
                ▼
 ┌───────────────────────────────┐
 │ Apps Script web app (Code.gs) │  "My Life Hub API", bound to the Sheet
 │  doGet: rev                   │  Execute as: owner · Access: Anyone
 │  doPost: auth / getAll / push │
 └──────────────┬────────────────┘
                ▼
 ┌───────────────────────────────┐
 │ Google Sheet "My Life Hub"    │  one tab per table (see docs/SCHEMA.md)
 └───────────────────────────────┘
```

**How sync works**

1. Open the app → lock screen → `POST {action:'auth', pin}`. The server returns a token (30 min TTL, kept in `sessionStorage`).
2. `POST {action:'getAll', token}` → the full data set plus `rev`.
3. On every local change, `Sync.capture()` diffs the state against the last synced base and queues ops. `flush()` sends `POST {action:'push', token, ops}`.
4. Every 15 s: `GET ?action=rev`. When the rev has changed, `getAll` runs again and the result is merged in.
5. Conflicts: per row, **last `updatedAt` wins**. Deletes are soft (`deleted=1`).
6. **Offline:** the app works from the localStorage cache and flushes the queue when it is back online. Offline unlock compares SHA-256(PIN) with `PIN_HASH` in index.html.

**Why `credentials:'omit'` + `text/plain`:** this avoids the CORS preflight and the "multiple Google accounts" error you get with `/exec` links. Don't change it.

## 3. Tech stack

- **Front end:** one `index.html`. Vanilla JS (ES2020), CSS custom properties, light and dark theme. **No framework, no bundler, no npm.**
- **Font:** Plus Jakarta Sans (Google Fonts).
- **Sprites:** PokeAPI sprites from raw.githubusercontent.com, with a fallback sprite and then a coloured initial.
- **Back end:** Google Apps Script (V8). Uses `SpreadsheetApp`, `LockService`, `CacheService` (tokens, PIN fail counter) and `PropertiesService` (rev).
- **Database:** a Google Sheet. Every cell is stored as text (`'` prefix / `@` number format).
- **Hosting:** GitHub Pages from the `main` branch root.
- **Tests:** Python + Playwright smoke test against a mock API (`tests/smoke_test.py`).

## 4. Commands

There is no install step and no build for the app itself.

```bash
# Run locally (any static server; file:// also works)
python3 -m http.server 8000        # then open http://localhost:8000/

# Smoke test (mock API, never touches real data)
pip install playwright && python -m playwright install chromium
python tests/smoke_test.py

# Quick JS syntax check of the inline script
python3 -c "import re;s=open('index.html').read();open('/tmp/app.js','w').write('\n'.join(re.findall(r'<script>(.*?)</script>',s,re.S)))" && node --check /tmp/app.js

# Deploy front end
git add index.html && git commit -m "..." && git push   # GitHub Pages updates in ~1 min

# Deploy back end (optional: clasp)
npm i -g @google/clasp && clasp login
cd apps-script && cp .clasp.json.example .clasp.json   # fill in scriptId
clasp push
# Then in the Apps Script UI: Deploy → Manage deployments → Edit (pencil)
#   → Version: "New version" → Deploy.   This keeps the SAME /exec URL.
```

## 5. Coding conventions and rules

**Do**
- Keep the app as **one self-contained `index.html`**. Inline CSS and JS.
- Add a section by creating a module object `{ id, label, icon, mount(el), update() }` and adding it to `MODULES`. For a new data table, also update all of these:
  1. `defaultState()`, adding `name: []`
  2. `normalize()`, adding an `if (Array.isArray(raw.name))` block
  3. `Sync`: `dataOf`, the two `['tasks','quran',…]` lists (in `capture` and in `merge`), `hasData`, and the "Sync this device's data?" text
  4. `EDIT_ACTIONS`, plus the `case` lines in the click handler
  5. the import check (`!Array.isArray(raw.name)`)
  6. **Code.gs:** `TABLES`, `KNOWN`, `readAll_()`
- **Deploy order for a new table:** the server first (new Apps Script version), then the front end. Otherwise new clients would push into a table the server does not know.
- Long text fields are `<textarea>` with `white-space:pre-wrap` on display. Enter makes a new line and must never submit the form.
- Escape all user text with `esc()` before putting it into HTML.
- Every edit, add and delete goes through `requirePin(...)`. Deletes use `confirmDialog` and offer Undo in a toast.
- UI text is in **English** (section names may be Malay, e.g. "Resepi", "Dars Syeikhuna").
- Test against the mock API (`tests/smoke_test.py`) before you deploy.
- After a GitHub commit, verify it by checking the SHA-256 of the file from `api.github.com/repos/.../contents/index.html`. raw.githubusercontent.com is cached, so don't use it for this.

**Don't**
- Don't add frameworks, build steps, npm packages or external JS libraries.
- Don't store data only in localStorage. **Every feature must sync through the Sheet** (the owner's standing rule for every app).
- Don't put the real PIN in client code, docs or commits. The client has only `PIN_HASH`.
- Don't make `getAll` public again. Data needs a valid token.
- Don't create a new Apps Script deployment for an update (that changes the URL). Edit the existing one and choose a new version.
- Don't remove or rename existing Sheet columns. Add new columns at the end.
- Don't put a test entry into real data. If one gets in, delete it.

**Owner's working preferences**
- Make sure every app syncs across devices and accounts.
- When unsure, confirm with the owner first. Tell them about limitations up front.
- The owner writes in Malay and English. Reply in the language they use.

## 6. Project status (27 Nov 2026)

**Done**
- PIN lock on open, 20-minute idle re-lock, lock button, server-side token auth (`getAll`, `push`)
- Cloud sync (15 s polling), offline queue, last-write-wins merge, upload of device-only data on first sync
- Daily Tasks with a multi-line remark; Quran Daily; Dars Syeikhuna; Qadha Prayer with undo history
- Personal notes, Resepi (search, tags, filter chips), TASK DH (search, tags, filter chips)
- Dark mode; Export/Import JSON

**WIP:** nothing is in progress. Everything above is deployed.

**Known issues and limitations**
1. The localStorage cache holds the full data set on each device. The lock screen hides it, but someone with the device and DevTools can read it.
2. Offline unlock uses `PIN_HASH`. A 4-digit PIN hash can be brute-forced by anyone who reads the source. The online path is rate-limited by the server (5 tries, then a 5-minute lock).
3. `Code.gs` in the live Apps Script may still have the old `setup()` that writes a default PIN; the local copy is fixed. Paste it in when convenient.
4. The Apps Script deployment description shows "Untitled". This is cosmetic.
5. There is no CI. Tests are run by hand.

## 7. File map

| Path | Purpose |
|---|---|
| `index.html` | The whole front end (deployed to GitHub Pages) |
| `apps-script/Code.gs` | Back end API (paste into, or `clasp push` to, the bound Apps Script project) |
| `apps-script/appsscript.json` | Apps Script manifest (web app: execute as owner, anyone can access) |
| `apps-script/.clasp.json` | clasp config with the real scriptId |
| `apps-script/.clasp.json.example` | Template for clasp |
| `.env` | **Real** IDs, URLs and PIN (git-ignored; never commit) |
| `.env.example` | Same keys with placeholders |
| `MASTER_PROMPT.md` | First prompt to paste into Claude Code |
| `docs/SCHEMA.md` | Sheet tabs, columns, API contract |
| `docs/NEXT_STEPS.md` | Checklist of tasks to give Claude Code |
| `tests/smoke_test.py` | Playwright smoke test with a mock API |
