import json
from pathlib import Path
BASE = Path(__file__).resolve().parents[1]
mig = BASE / 'server' / 'apps' / 'academies' / 'migrations' / 'data' / 'zq_academy.json'
fix = BASE / 'server' / 'fixtures' / 'academies_2025.json'
if not mig.exists():
    print('migration data not found', mig)
    raise SystemExit(1)
if not fix.exists():
    print('fixture not found', fix)
    raise SystemExit(1)
md = json.loads(mig.read_text(encoding='utf-8'))
fd = json.loads(fix.read_text(encoding='utf-8'))
md_map = {item['id']: item for item in md}
fd_map = {item['pk']: item for item in fd}
md_ids = set(md_map.keys())
fd_ids = set(fd_map.keys())
print('migration ids count:', len(md_ids))
print('fixture ids count:', len(fd_ids))
print('ids only in migration:', sorted(md_ids - fd_ids))
print('ids only in fixture:', sorted(fd_ids - md_ids))

# name differences for common ids
diffs = []
for k in sorted(md_ids & fd_ids):
    mname = md_map[k].get('name') if 'name' in md_map[k] else md_map[k].get('fields', {}).get('name')
    fname = fd_map[k].get('fields', {}).get('name')
    if mname != fname:
        diffs.append((k, mname, fname))
print('name differences count:', len(diffs))
for d in diffs:
    print(d)
