# Data schema and API: My Life Hub

The database is one Google Sheet, "My Life Hub". Every value is stored as **text**. The server writes it with the `@` number format or a leading `'`, so dates and long numbers keep their exact form.

`setup()` in Code.gs creates every tab, and running it again does no harm. A table tab that is missing is created automatically on the first write.

## Table tabs (synced row by row)

Common columns:

| Column | Type | Notes |
|---|---|---|
| `id` | string | Created on the client by `uid()`; unique |
| `createdAt` | ms epoch | Set by the client |
| `updatedAt` | ms epoch | Set when the change is captured; **last write wins** |
| `deleted` | `''` or `'1'` | Soft delete; `readAll_()` skips these rows |

| Tab | Key in API | Columns (in order) |
|---|---|---|
| `Tasks` | `tasks` | id, date (YYYY-MM-DD), item, remark (multi-line, ≤3000), status (`pending`/`done`/`unsuccessful`), createdAt, updatedAt, deleted |
| `Quran` | `quran` | id, date, page, remark, createdAt, updatedAt, deleted |
| `Dars` | `dars` | id, date, event, note, createdAt, updatedAt, deleted |
| `Personal` | `personal` | id, date, note (≤3000), createdAt, updatedAt, deleted |
| `Resepi` | `recipes` | id, date, tag (`ayam`/`daging`/`ikan`/`dessert`/`lain-lain`), text (≤10000), createdAt, updatedAt, deleted |
| `Task DH` | `dh` | id, date, tag (`PODCAST`/`MAKTABAH`/`SHOPEE_DH`/`HIKAMULHIKMAH`), text (≤10000), createdAt, updatedAt, deleted |

## Special tabs

| Tab | Columns | Notes |
|---|---|---|
| `Qadha` | prayer, initial, remaining, updatedAt | 5 fixed rows: subuh, zohor, asar, maghrib, isyak |
| `Meta` | key, value | `qadhaHistory` (JSON, last 20 undo steps), `historyUpdatedAt` |
| `Settings` | key, value | `pin`: the server-side PIN. Change the PIN here **and** update `PIN_HASH` in index.html |

Script Properties: `rev` is a counter that goes up on every push.
CacheService: tokens (`tok_<uuid>`, 30 min) and the failed-PIN counter.

## Client state (`localStorage['lifehub_v1']`)

```js
{
  tasks: [], quran: [], dars: [], personal: [], recipes: [], dh: [],
  qadha: { subuh:{initial,remaining}, zohor:{…}, asar:{…}, maghrib:{…}, isyak:{…} },
  history: [ /* qadha undo steps */ ],
  settings: { tab, filter, theme, … }
}
```

Other keys: `lifehub_sync_v1` (sync base, rev, queue) in localStorage; `lifehub_token` and `lifehub_unlocked` in sessionStorage.

## API contract (`API_URL` = the web app's /exec URL)

Every POST uses `Content-Type: text/plain;charset=utf-8`, `credentials:'omit'` and a JSON body.

| Call | Request | Response |
|---|---|---|
| Health | `GET /exec` | `{ok:true,msg}` |
| Revision | `GET /exec?action=rev` | `{ok:true,rev}` (public) |
| Auth | `POST {action:'auth', pin}` | `{ok:true, token, ttl}` / `{ok:false, code:'PIN'}` / `{ok:false, code:'LOCKED', msg}` |
| Read all | `POST {action:'getAll', token}` | `{ok:true, rev, data:{tasks,quran,dars,personal,recipes,dh,qadha,history}}` / `{ok:false, code:'AUTH'}` |
| Push | `POST {action:'push', token, ops:[…]}` | `{ok:true, rev, data}` / `{ok:false, code:'AUTH'}` |

The `ops` array has at most 500 items per call:

```js
{ type:'upsert',  table:'tasks'|'quran'|'dars'|'personal'|'recipes'|'dh', rec:{ id, …columns, updatedAt, deleted? } }
{ type:'qadha',   prayer:'subuh', initial, remaining, updatedAt }
{ type:'history', history:[…], updatedAt }
```

`GET ?action=getAll` is blocked on purpose. It returns `{ok:false, code:'AUTH'}`.

## Migrations

There is no migration tool. To add a table:

1. Add it to `TABLES` and `KNOWN` in Code.gs, and add `name: readTable_('name')` to `readAll_()`.
2. Deploy a new **version** of the existing deployment.
3. Update index.html (see CLAUDE.md §5) and push it to GitHub.

To add a column, append it to the end of `cols`. Old rows read as `''`.
