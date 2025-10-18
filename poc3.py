#!/usr/bin/env python3
import requests, re, time, random
from typing import Optional

BASE = None
S = requests.Session()
S.headers.update({'Cache-Control': 'no-cache'})

SAFE_FILES = '''import os
import re
from flask import Blueprint, request, send_file, Response

files_bp = Blueprint("files", __name__)

BASE_DIR = os.path.realpath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "data"))

@files_bp.get("/download")
def download_file():
    rel = request.args.get("file", "")
    if not rel or not re.match(r'^[a-zA-Z0-9._-]{1,100}$', rel):
        return Response("Invalid file name", status=400)

    rel = rel.replace('/', '').replace('\\\\', '').strip()
    full_path = os.path.realpath(os.path.join(BASE_DIR, rel))

    if (not full_path.startswith(BASE_DIR + os.path.sep) or
        not os.path.exists(full_path) or
        not os.path.isfile(full_path) or
        os.path.islink(os.path.join(BASE_DIR, rel))):
        return Response("File not found", status=404)

    try:
        if not os.path.samefile(os.path.join(BASE_DIR, rel), full_path):
            return Response("File not found", status=404)
        return send_file(full_path, as_attachment=True)
    except PermissionError:
        return Response("Permission denied", status=403)
    except Exception:
        return Response("Internal Server Error", status=500)
'''

def ncs():
    return f"&_={int(time.time()*1000)}{random.randint(1000,9999)}"

def get_c(p, nc=False):
    u = f"{BASE}/api/code?path={p}" + (ncs() if nc else "")
    return S.get(u, timeout=10).json()

def save_c(p, c, s):
    return S.post(f"{BASE}/api/code",
                  headers={'Content-Type': 'application/json'},
                  json={'path': p, 'code': c, 'sha': s}, timeout=10).json()

def show_yaml(c):
    for i, ln in enumerate(c.splitlines(), 1):
        if re.search(r'yaml\.(load|unsafe_load|full_load|load_all)|Loader|FullLoader', ln):
            print(f"{i:4}: {ln.rstrip()}")

def fix_yaml(c):
    c = re.sub(r'yaml\.load\s*\(\s*([^,)\n]+)\s*,\s*Loader\s*=\s*yaml\.\w+\s*\)',
               r'yaml.safe_load(\1)', c)
    c = re.sub(r'yaml\.(full_load|unsafe_load)\s*\(', 'yaml.safe_load(', c)
    c = re.sub(r'(?<!safe_)yaml\.load\s*\(', 'yaml.safe_load(', c)
    return re.sub(r'(?<!safe_)yaml\.load_all\s*\(', 'yaml.safe_load_all(', c)

def diff(o, n):
    ol, nl = o.splitlines(), n.splitlines()
    for i, (a, b) in enumerate(zip(ol, nl), 1):
        if a != b:
            print(f"{i:4}:\n   - {a}\n   + {b}")

def p_theme():
    d = get_c('routes/theme.py', nc=True)
    c, s = d['code'], d['sha']
    show_yaml(c)
    nc = fix_yaml(c)
    if nc != c:
        diff(c, nc)
        save_c('routes/theme.py', nc, s)

def p_files():
    d = get_c('routes/files.py', nc=True)
    c, s = d['code'], d['sha']
    if c.strip() != SAFE_FILES.strip():
        diff(c, SAFE_FILES)
        save_c('routes/files.py', SAFE_FILES, s)

def validate() -> Optional[str]:
    time.sleep(2)
    j = S.post(f"{BASE}/api/validate", headers={'Content-Type':'application/json'}, timeout=150).json()
    print(f"Success: {j.get('success')}")
    print(f"Functional: {j.get('functional')}")
    print(f"RCE (YAML): {j.get('rce')}")
    print(f"Path Traversal: {j.get('path_traversal')}")
    if j.get('output'):
        print(f"Output:\n{j['output']}")
    if j.get('flag'):
        print(f"Flag: {j['flag']}")
        return j['flag']
    return None

def main():
    global BASE
    BASE = input("URL: ").strip().rstrip('/')
    if input("Reset? (y/n): ").strip().lower() != 'y':
        return
    
    p_theme()
    p_files()
    time.sleep(3)
    validate()

if __name__ == '__main__':
    main()
