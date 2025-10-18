import requests
import re
import time

URL = "http://43.203.171.66:19999"

def classify(text):
    s = 0
    gp = [r"perhaps", r"might", r"seems", r"appears", r"I find", r"I've found", r"doesn't it\?", r"isn't it\?", r"There's a", r"It's not", r"recognition", r"peculiar", r"curious", r"intriguing", r"fascinating"]
    s += sum(1 for p in gp if re.search(p, text, re.IGNORECASE)) * 2
    lp = [r"^[A-Z][^.!?]{20,80}\n\n", r"Moreover,", r"Furthermore,", r"In conclusion,", r"For instance,", r"For example,", r"Ultimately,", r"In other words,", r"That is to say,"]
    s -= sum(1 for p in lp if re.search(p, text)) * 2
    st = [s.strip() for s in re.split(r'[.!?]+', text) if len(s.strip()) > 10]
    if st:
        al = sum(len(s.split()) for s in st) / len(st)
        s += 1 if al > 25 else -1 if al < 20 else 0
    s += 1 if text.count('–') + text.count('—') >= 2 else 0
    s += 1 if text.count('?') >= 2 else 0
    s += 1 if len(re.findall(r'\bI\b', text)) >= 3 else 0
    s -= 1 if len(re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)) >= 5 else 0
    return 1 if s > 0 else 0

def run():
    for _ in range(200):
        time.sleep(0.6)
        r = requests.get(f"{URL}/challenge").json()
        cid, txt = r['id'], r['challenges']
        ans = [classify(t) for t in txt]
        time.sleep(0.6)
        r = requests.post(f"{URL}/challenge/{cid}", json={"answers": ans}).json()
        if "correct" in r['result'] and "incorrect" not in r['result']:
            return r['result']
    return "Failed after 200 attempts"

if __name__ == "__main__":
    print(run())
