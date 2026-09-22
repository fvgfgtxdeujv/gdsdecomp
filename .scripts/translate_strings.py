"""Machine-translate the zh_CN column of gdre_strings.csv (English -> Simplified Chinese).

Standalone dev utility for translators; not used by the build. It fills the
zh_CN column in-place as an initial draft, meant to be reviewed manually
afterwards (machine output is NOT committed blindly).

Engines (probed at startup, only reachable ones are used, in order):
  1. deep-translator GoogleTranslator   (translate.google.com)
  2. googletrans                        (translate.google.com)
  3. deep-translator MyMemoryTranslator (api.mymemory.translated.net, keyless)
Protected during translation: printf placeholders (%s/%d), BBCode tags.
Literal "\\n" sequences are translated per-line and rejoined.
Skipped (left for manual review): file-dialog filters, technical nouns,
and rows whose zh_CN cell is already filled.
Usage: python .scripts/translate_strings.py [--dry-run]
"""
import asyncio
import csv
import inspect
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

CSV_PATH = Path(__file__).resolve().parent.parent / "standalone" / "translations" / "gdre_strings.csv"
DRY_RUN = "--dry-run" in sys.argv

# Exact keys that must not be machine-translated
SKIP_EXACT = {
    "PCK", "GDScript", "MP3", "ADPCM", "PCM 8-bit", "PCM 16-bit",
    "Ogg Vorbis", "Quite OK", "PingPong", "--:-- / --:--",
    "ERROR:", "ERROR: ", " (Mono)", " (Steam Mono edition)",
}
TOKEN = "\u27e6{}\u27e7"  # ⟦0⟧ style placeholder


def should_skip(key: str) -> bool:
    if key in SKIP_EXACT:
        return True
    if key.startswith("*."):  # file dialog filter globs
        return True
    if not re.search(r"[A-Za-z]{2,}", key):  # no real words
        return True
    return False


def protect(s: str):
    tokens = []

    def rep(m):
        tokens.append(m.group(0))
        return TOKEN.format(len(tokens) - 1)

    return re.sub(r"\[url=[^\]]*\]|\[/url\]|\[b\]|\[/b\]|%[sd]", rep, s), tokens


def restore(s: str, tokens):
    for i, t in enumerate(tokens):
        if TOKEN.format(i) not in s:
            return None
    for i, t in enumerate(tokens):
        s = s.replace(TOKEN.format(i), t)
    return s


def mt_google_dt(seg: str) -> str:
    from deep_translator import GoogleTranslator
    return GoogleTranslator(source="en", target="zh-CN").translate(seg)


def mt_googletrans(seg: str) -> str:
    from googletrans import Translator

    async def _t():
        tr = Translator()
        r = tr.translate(seg, src="en", dest="zh-cn")
        if inspect.iscoroutine(r):
            r = await r
        return r.text

    return asyncio.run(_t())


def mt_mymemory(seg: str) -> str:
    from deep_translator import MyMemoryTranslator
    return MyMemoryTranslator(source="en-US", target="zh-CN").translate(seg)


def _probe(url: str, timeout: int = 8) -> bool:
    try:
        import requests
        requests.get(url, timeout=timeout)
        return True
    except Exception:
        return False


def build_engines():
    engines = []
    if _probe("https://translate.google.com/m?tl=zh-CN&sl=en&q=test"):
        engines += [mt_google_dt, mt_googletrans]
    if _probe("https://api.mymemory.translated.net/get?q=test&langpair=en|zh-CN"):
        engines.append(mt_mymemory)
    return engines


def translate_entry(key: str, engines):
    out_segs = []
    for seg in key.split("\\n"):
        lead, mid, trail = re.match(r"^(\s*)(.*?)(\s*)$", seg, re.S).groups()
        if not mid:
            out_segs.append(seg)
            continue
        prot, tokens = protect(mid)
        res = None
        for fn in engines:
            try:
                cand = fn(prot)
                if cand:
                    back = restore(cand, tokens)
                    if back is not None:
                        res = back.strip()
                        break
            except Exception:
                time.sleep(0.5)
                continue
            time.sleep(0.1)
        time.sleep(0.25)
        if res is None:
            return key, None
        out_segs.append(lead + res + trail)
    return key, "\\n".join(out_segs)


def main():
    with open(CSV_PATH, encoding="utf-8", newline="") as f:
        rows = [r for r in csv.reader(f)]
    header, body = rows[0], rows[1:]
    zh_idx = header.index("zh_CN")

    todo = []
    for r in body:
        if not r:
            continue
        while len(r) < len(header):
            r.append("")
        if r[zh_idx].strip() or should_skip(r[0]):
            continue
        todo.append(r)
    print(f"{len(todo)} entries to translate (of {len(body)} rows)")

    results, fails = {}, []
    engines = build_engines()
    if not engines:
        print("ERROR: no translation engine reachable (Google and MyMemory both blocked)")
        sys.exit(2)
    print(f"engines: {[fn.__name__ for fn in engines]}")
    with ThreadPoolExecutor(max_workers=3) as ex:
        futs = {ex.submit(translate_entry, r[0], engines): r[0] for r in todo}
        for i, fut in enumerate(as_completed(futs), 1):
            key, val = fut.result()
            if val is None:
                fails.append(key)
            else:
                results[key] = val
            if i % 25 == 0:
                print(f"  ... {i}/{len(todo)}")

    for r in body:
        if r and r[0] in results:
            r[zh_idx] = results[r[0]]

    if DRY_RUN:
        for r in body:
            if r and r[zh_idx].strip():
                print(f"{r[0]!r} -> {r[zh_idx]!r}")
        return

    with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL, lineterminator="\n")
        w.writerow(header)
        w.writerows(body)

    print(f"done: {len(results)} translated, {len(fails)} failed")
    for k in fails:
        print("FAILED: " + repr(k))


if __name__ == "__main__":
    main()
