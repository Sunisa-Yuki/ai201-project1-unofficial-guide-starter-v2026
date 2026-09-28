"""Unit 2: compare semantic-only vs hybrid retrieval on my 5 test questions.

Counts how many of the top-5 retrieved chunks come from the document that
actually answers the question. Run:  python tools/compare_retrieval.py
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import config, store
from questions import answered

RIGHT_FILE = ["dining_kestrel_commons", "admin_dining_dollars", "admin_grade_appeals",
              "housing_innisfree_hall", "transit_shuttle"]

for mode in (False, True):
    config.HYBRID = mode
    print(f"\n=== {'HYBRID (semantic + BM25)' if mode else 'SEMANTIC ONLY'} ===")
    total = 0
    for q, want in zip(answered(), RIGHT_FILE):
        res = store.search(q["question"])
        hits = sum(r.source.startswith(want) for r in res)
        total += hits
        best = min(r.distance for r in res)
        print(f"{hits}/{len(res)} on-topic  best={best:.3f}  {q['question']}")
        print("      " + ", ".join(r.label for r in res))
    print(f"TOTAL on-topic chunks: {total}/25")
