"""
Smoke test for My Life Hub against a MOCK Apps Script API (no real data touched).

Install once:   pip install playwright && python -m playwright install chromium
Run:            python tests/smoke_test.py
PIN: read from APP_PIN in the environment or the local .env (must match PIN_HASH in index.html).
"""
import json, os, pathlib, re, urllib.parse as up
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]
def _pin():
    if os.environ.get('APP_PIN'): return os.environ['APP_PIN']
    env = ROOT / '.env'
    m = env.exists() and re.search(r'^APP_PIN=(\S+)', env.read_text(), re.M)
    if not m: raise SystemExit('Set APP_PIN (env var or .env) to run the smoke test.')
    return m.group(1)
MOCK_PIN = _pin()
DB = {'tasks': [], 'quran': [], 'dars': [], 'personal': [], 'recipes': [], 'dh': [],
      'qadha': {p: {'initial': 0, 'remaining': 0} for p in ['subuh', 'zohor', 'asar', 'maghrib', 'isyak']},
      'history': []}
TOKENS = set()

def handle(route, req):
    if req.method == 'GET':
        a = up.parse_qs(up.urlparse(req.url).query).get('action', [''])[0]
        res = {'ok': True, 'rev': 1} if a == 'rev' else {'ok': False, 'code': 'AUTH'}
    else:
        b = json.loads(req.post_data)
        if b['action'] == 'auth':
            ok = b['pin'] == MOCK_PIN
            res = {'ok': ok, 'token': 'T', 'ttl': 1800} if ok else {'ok': False, 'code': 'PIN', 'msg': 'Wrong PIN.'}
            if ok: TOKENS.add('T')
        elif b['action'] == 'getAll':
            res = {'ok': True, 'rev': 1, 'data': DB} if b.get('token') in TOKENS else {'ok': False, 'code': 'AUTH'}
        else:
            for o in b.get('ops', []):
                if o['type'] == 'upsert':
                    t = DB[o['table']]; r = dict(o['rec'])
                    t[:] = [x for x in t if x['id'] != r['id']]
                    if not r.get('deleted'): t.append(r)
            res = {'ok': True, 'rev': 2, 'data': DB}
    route.fulfill(status=200, content_type='application/json',
                  headers={'Access-Control-Allow-Origin': '*'}, body=json.dumps(res))

def main():
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': 400, 'height': 860})
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.route('https://script.google.com/**', handle)
        pg.route('https://raw.githubusercontent.com/**', lambda r: r.abort())
        pg.goto((ROOT / 'index.html').as_uri()); pg.wait_for_timeout(1000)
        assert pg.is_visible('#lockScreen'), 'lock screen should show on open'
        pg.fill('#lsPin', MOCK_PIN); pg.wait_for_timeout(1500)
        assert not pg.is_visible('#lockScreen'), 'PIN should unlock'

        # Daily Tasks: multiline remark
        pg.click('[data-tab=tasks]'); pg.fill('#taskItem', 'Test task')
        pg.click('#taskRemark'); pg.keyboard.type('Line 1'); pg.keyboard.press('Enter'); pg.keyboard.type('Line 2')
        pg.click('#taskForm button[type=submit]'); pg.wait_for_timeout(1200)
        assert any(t['remark'] == 'Line 1\nLine 2' for t in DB['tasks'])

        # Personal
        pg.click('[data-tab=personal]'); pg.fill('#psNote', 'note'); pg.click('#personalForm button[type=submit]'); pg.wait_for_timeout(1200)
        assert DB['personal'] and DB['personal'][0]['note'] == 'note'

        # Resepi
        pg.click('[data-tab=recipes]'); pg.click('#recipeForm >> text=#dessert'); pg.fill('#rcText', 'Puding')
        pg.click('#recipeForm button[type=submit]'); pg.wait_for_timeout(1200)
        assert DB['recipes'][0]['tag'] == 'dessert'

        # TASK DH
        pg.click('[data-tab=dh]'); pg.click('#dhForm >> text=#MAKTABAH'); pg.fill('#dhText', 'Susun buku')
        pg.click('#dhForm button[type=submit]'); pg.wait_for_timeout(1200)
        assert DB['dh'][0]['tag'] == 'MAKTABAH'
        pg.fill('#dhSearch', 'zzz'); assert pg.locator('.dh-entry').count() == 0

        # Lock again
        pg.click('#lockBtn'); assert pg.is_visible('#lockScreen')
        assert not errs, errs
        b.close()
    print('ALL SMOKE TESTS PASSED')

if __name__ == '__main__':
    main()
