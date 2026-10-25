"""Bangun ulang index dan simpan hasil pengujian yang dapat direproduksi."""
import json
import platform
from pathlib import Path
from time import perf_counter
import sklearn
from ir_system.engine import SearchEngine

ROOT = Path(__file__).resolve().parent
QUERIES = ['pendidikan matematika', 'gempa Aceh', 'kecerdasan buatan',
           'korupsi pemerintah', 'lagu anime', '', 'dan yang di', 'zzzxxyyqq']

def main():
    engine = SearchEngine(ROOT/'indexdir')
    stats = engine.build(ROOT/'datasets')
    tests = []
    for query in QUERIES:
        start = perf_counter()
        results = engine.search(query)
        tests.append(dict(query=query, seconds=perf_counter()-start, results=results))
    output = dict(environment={'python':platform.python_version(),
                              'sklearn':sklearn.__version__, 'whoosh':'2.7.4'},
                  stats=stats, tests=tests)
    (ROOT/'hasil_pengujian').mkdir(exist_ok=True)
    (ROOT/'hasil_pengujian/results.json').write_text(json.dumps(output,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(stats,indent=2))
    for test in tests:
        print(repr(test['query']), [(r['source'],round(r['score'],6)) for r in test['results']])

if __name__ == '__main__':
    main()
