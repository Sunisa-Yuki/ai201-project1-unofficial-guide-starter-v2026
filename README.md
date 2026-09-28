# The Unofficial Guide

Yuki — corpus: `campus_life`

> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none.
>
> Delete these instruction blocks as you replace them. The `<!-- -->` comments
> are notes to you and don't show up when the page renders — you can leave them
> or remove them.

---

# Unit 1

## What This Does

The Unofficial Guide answers plain-English questions about campus life using the `campus_life` corpus: 88 short student-written posts about dining halls, dorms, laundry, noise, courses, deadlines and the campus shuttle. You ask something like "How long is the wait at Kestrel Commons at lunch?" and it retrieves the closest posts from a local Chroma vector store, checks they're actually close enough (the relevance gate), and has the model answer from those posts only, naming the file each fact came from. Questions the posts don't cover get "I don't have enough information about that" instead of a guess.

## Chunking Strategy

**Chunk size:** up to 350 characters per chunk, split on paragraph boundaries (blank lines), never mid-sentence. A leftover piece under 80 characters is merged into the previous chunk.
**Overlap:** no character overlap. Instead, the post's title line (e.g. "Kestrel Commons", "Laundry in Innisfree Hall") is repeated at the top of every chunk from that post.

When I read the documents I saw that every post is short (183–554 characters) and made of 1–4 short paragraphs, and each paragraph is usually one idea: wait times, then hours and cost; or "the good", then "the bad". The starter's 800-character window never split anything (88 docs became 88 chunks), so a housing post that covers rooms, air conditioning, laundry *and* noise was one chunk that matched every housing question a little. Splitting on paragraphs separates those ideas. The risk is a paragraph like "Hours are 7:00am to 9:00pm weekdays" losing *which* building it's about, which is why I repeat the title instead of using a character overlap: a 120-character overlap would copy half a paragraph from the neighbour, while the title carries the one piece of context that matters. My chunker produces 107 chunks, 265 characters on average (shortest 116, longest 397).

## Sample Chunks

**Chunk 1** — source: `admin_add_drop_deadline.txt#0` — produced by: `chunker.py::split_documents`

```
On the add/drop deadline

You can add a course through the end of the second week. Dropping is a longer window — through the end of week six — but a drop after week two shows as a W on your transcript. Nothing anywhere on the registrar's site says this plainly, and students find out from each other.
```

**Chunk 2** — source: `course_cs_210.txt#0` — produced by: `chunker.py::split_documents`

```
CS 210 Data Structures

I'm a junior and I've done this twice now. Format is lecture with weekly labs; slides go up after class, not before. Assessment: two midterms and a final, all drawn from lecture material rather than the textbook. Midterms are curved, the final is not.

Expect 8 to 10 hours a week outside class.
```

**Chunk 3** — source: `course_math_220_exams.txt#0` — produced by: `chunker.py::split_documents`

```
MATH 220 Linear Algebra — assessment

Two midterms and a cumulative final. Curved to a b- median.

The problem sets are the course; the lectures make sense afterwards rather than during.
```

**Chunk 4** — source: `dining_the_ridgeway_cafe.txt#0` — produced by: `chunker.py::split_documents`

```
The Ridgeway Café

Second-year here. Wait times: 10 to 15 minutes at 12:30, none after 2:00. The thing worth going for is the only place on campus with real espresso. The thing to know is that seating is tight; about 40 seats for a building of 900.

Hours are 7:00am to 4:00pm weekdays only. Costs declining balance only, no meal swipes.
```

**Chunk 5** — source: `housing_innisfree_hall_laundry.txt#0` — produced by: `chunker.py::split_documents`

```
Laundry in Innisfree Hall

Machines take $1.75 wash, $1.75 dry, app-based. There are eight washers and six dryers for the building, which is the wrong ratio and means the dryers back up on Sunday evenings.

Best time to do laundry here is Tuesday or Wednesday morning. Sunday after 6pm you will wait.
```

## Sample Answer

**Question:** How long is the wait at Kestrel Commons during the lunch rush?

**Answer:**

```
$ python app.py ask "How long is the wait at Kestrel Commons during the lunch rush?"
  (best distance 0.198, cutoff 0.6)

The wait time at Kestrel Commons is 20 to 25 minutes between 12:15 and 1:00. (Source: `dining_kestrel_commons.txt` and `dining_kestrel_commons_followup.txt`)

Sources retrieved: dining_halden_hall_followup.txt, dining_kestrel_commons.txt, dining_kestrel_commons_followup.txt, dining_the_ridgeway_cafe_followup.txt
```

**My relevance cutoff:** 0.7 (`THRESHOLD` in `config.py`, raised from the starter's 0.6)

I ran my five test questions and the five `OUT_OF_SCOPE` questions through `python app.py retrieve` and recorded the best distance for each. In-corpus questions landed at 0.198–0.593; out-of-scope questions at 0.825–0.923, so there is a clean gap between 0.593 and 0.825. Four in-corpus questions sit near 0.2, but the shuttle question is an outlier at 0.593. My chunker split `transit_shuttle.txt` into two chunks, and the question's wording ("running behind") doesn't match the post's ("when the driver is behind"). At the starter's 0.6 it would only just pass, so I moved the cutoff to 0.7, roughly the middle of the gap. That leaves room for paraphrased in-corpus questions while still being well below the closest off-topic one (0.825). What 0.7 would get wrong: an off-topic question that shares campus vocabulary (e.g. "what's the best pizza in town?") could slip under it.

| Question | In corpus? | Best distance |
|---|---|---|
| How long is the wait at Kestrel Commons during the lunch rush? | Yes | 0.198 |
| Do leftover dining dollars roll over from spring to the next autumn? | Yes | 0.207 |
| How many days do I have to start a grade appeal, and who do I go to first? | Yes | 0.201 |
| What does laundry cost in Innisfree Hall and when is the best time to do it? | Yes | 0.206 |
| Which shuttle stop gets skipped when the driver is running behind? | Yes | 0.593 |
| What is the capital of Mongolia? | No | 0.825 |
| How do I change the oil in a diesel engine? | No | 0.923 |
| Who won the 1994 World Cup? | No | 0.886 |
| What is the recommended dosage of ibuprofen for a headache? | No | 0.844 |
| How do I write a for loop in Rust? | No | 0.864 |

## How I Used AI

**1.** I gave Claude the Milestone 3 brief and a few `campus_life` posts and asked for a chunker. It proposed splitting on paragraphs and carrying the post's title into each chunk instead of a character overlap. I checked the output against criterion 4 by reading `python app.py chunks -n 5`, and kept an 80-character minimum so a one-line trailing paragraph gets folded into the previous chunk instead of becoming a fragment like the 2-character chunk the starter made on advice_threads.

**2.** During setup my `pip install -r requirements.txt` failed with "No such file or directory". I pasted the terminal output to Claude, and it pointed out that I had skipped the `git clone` / `cd` step and was running from my Desktop instead of the repo. I re-ran the clone, moved into the repo folder, and made a fresh `.venv` there. I also checked every `expects` phrase Claude suggested for `questions.py` against the actual source file (e.g. "20 to 25 minutes" in `dining_kestrel_commons.txt`) before committing them.

**3. (Unit 2)** I pasted my before-run results into Claude and asked it to score each criterion and find the weakest result. It pointed at the shuttle question (0.593) and suggested hybrid search. It wrote `hybrid_search` so it keeps the real cosine distance on every chunk, which means my gate still works the same. When the after run didn't improve anything, I didn't claim it helped. Checking why led to the word "behind" matching the BIOL 160 posts, and that went into the README as the result.

<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

Evidence: `results/run_2026-09-27_2332_before.md`, produced by `run_eval.py::main` (3 runs per question, cache off, top-k 5, cutoff 0.7, chunks from `chunker.py::split_documents`, retrieval `store.py::search`, semantic only). No `scorer.py`, so I scored every cell by reading the answer text.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunks contain the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Chunks are complete, labelled thoughts (≥4 of 5 samples start with title + end on a full sentence; none < 80 chars) | 4 of 5, min ≥ 80 | 5/5, min 116 | 5/5, min 116 | 5/5, min 116 | MET |
| 5. Answer contains the `expects` phrase | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |

Criteria 3 and 4 are deterministic (the gate is a fixed comparison; the chunker doesn't change between runs), so the same number goes in all three columns.

**Real output, one per criterion (run 1 unless noted):**

Criterion 1: shuttle question, the hardest one. The answer chunk was retrieved (`transit_shuttle.txt`), best distance 0.5925:
```
Sources retrieved: dining_halden_hall_followup.txt, dining_kestrel_commons_followup.txt, dining_north_kitchen_followup.txt, transit_shuttle.txt
```

Criterion 2: every answer names its file, e.g.:
```
You have fifteen days to start a grade appeal, and you must go to the instructor first (*admin_grade_appeals.txt*).
```

Criterion 3: `run_eval.py::check_out_of_scope`, cutoff 0.7, refused 5 of 5:
```
refused  (best distance 0.825)  What is the capital of Mongolia?
refused  (best distance 0.923)  How do I change the oil in a diesel engine?
refused  (best distance 0.886)  Who won the 1994 World Cup?
refused  (best distance 0.844)  What is the recommended dosage of ibuprofen for a headache?
refused  (best distance 0.864)  How do I write a for loop in Rust?
```

Criterion 4: `python app.py index` summary, `chunker.py::split_documents`; all 5 samples under Sample Chunks above start with their title line:
```
chunked  107 chunks, 265 characters on average (shortest 116, longest 397), produced by chunker.py::split_documents
```

Criterion 5: expects phrase "20 to 25 minutes":
```
The wait at Kestrel Commons is 20 to 25 minutes between 12:15 and 1:00 (which is the lunch rush timeframe mentioned).
Source: `dining_kestrel_commons.txt` (and also mentioned in `dining_kestrel_commons_followup.txt`).
```

## Verdicts

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 | Retrieved chunks contain the answer | MET | In all 15 question-runs, the file holding the answer was in the retrieved set, and the answer text matched it. |
| 2 | Every answer names a source | MET | All 15 answers name a `.txt` file, and in every case it's the file the fact actually comes from, not just any retrieved file. |
| 3 | Gate stops out-of-corpus questions | MET | 5 of 5 refused. The closest off-topic question (0.825) was 0.125 above the cutoff. |
| 4 | Chunks are complete, labelled thoughts | MET | 5/5 samples start with the post title and end on a full sentence; the shortest chunk in the index is 116 characters, above the 80 floor. |
| 5 | Answer contains the `expects` phrase | MET | 15/15. Closest call: "fifteen days" could have come out as "15 days" and failed a string match, but it didn't in any run. |

## Diagnoses

**I missed nothing, and that mostly means my targets were set low.** Four of five criteria allowed one miss, and my five questions each have one obvious source document written in the same words as the answer. None of them needs two documents combined or tests paraphrase. The system cleared 5/5 everywhere, so the criteria didn't separate a good system from an OK one.

The one weak spot the runs *did* show is in **retrieval**, on the shuttle question:
- **Stage: retrieval (embedding match).** Best distance 0.593, versus about 0.20 for the other four questions. The question says "running behind"; the post says "when the driver is behind". My chunker split `transit_shuttle.txt` in two, and the chunk with the answer opens with "It's free with a student ID", which dilutes the embedding.
- **Mechanism:** the other 3 of the 4 retrieved files were dining follow-up posts, pulled in because they talk about *waiting* and *timing*, the same general idea as "running behind". Semantic search matched on topic ("delays") instead of on the exact words the question shares with the post ("shuttle", "stop", "driver").
- At the starter's 0.6 cutoff this question would have passed by only 0.007. It's the answer that is one wording change away from being refused.

**Criteria I'd tighten:** criterion 1 to "the answer chunk is ranked #1 in at least 4 of 5", and criterion 3 to "every out-of-scope question is refused *and* its best distance is at least 0.1 above the cutoff".

## The Improvement

**What I changed:** hybrid search. `store.py::hybrid_search` runs BM25 keyword search (`rank-bm25`) alongside semantic search and merges the two rankings with reciprocal rank fusion (k=60). Every chunk keeps its real cosine distance, so the relevance gate (`gate.py::check`, which takes the minimum distance) works exactly as before. It's switched by `HYBRID` in `config.py` (or `AI201_HYBRID=0`), so the before system can still be run. Nothing else changed: same chunker, same top-k, same cutoff, same prompt.

**Why I picked it:** the shuttle question shares exact words with its answer post ("shuttle", "stop", "driver"), but semantic search ranked three dining posts about *waiting* next to it, and keyword matching is what should catch that.

### Run Log — After

Evidence: `results/run_2026-09-27_2337_after.md` (same settings, `HYBRID = True`).

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunks contain the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Chunks are complete, labelled thoughts (≥4 of 5 samples start with title + end on a full sentence; none < 80 chars) | 4 of 5, min ≥ 80 | 5/5, min 116 | 5/5, min 116 | 5/5, min 116 | MET |
| 5. Answer contains the `expects` phrase | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |

Retrieved files for the shuttle question, before and after (identical across all 3 runs of each):
```
BEFORE (semantic): dining_halden_hall_followup.txt, dining_kestrel_commons_followup.txt, dining_north_kitchen_followup.txt, transit_shuttle.txt
AFTER  (hybrid):   course_biol_160.txt, course_biol_160_exams.txt, dining_halden_hall_followup.txt, transit_shuttle.txt
```

Answer file present in the retrieved set, counted by file, for all five questions:

| Question | Before: right file / files retrieved | After |
|---|---|---|
| Kestrel wait | 2/4 | 2/4 |
| Dining dollars | 1/5 | 1/5 |
| Grade appeal | 1/5 | 1/5 |
| Innisfree laundry | 2/5 | 2/5 |
| Shuttle | 1/4 | 1/4 |

**Did it help?** No. All five criteria are the same (still 5/5 on every run), and the thing I was trying to fix didn't improve: the shuttle question still retrieves exactly one relevant file. Hybrid only swapped *which* noise came back. BM25 matched the word "behind" in `course_biol_160.txt` ("falling behind once is very hard to recover from"), so two biology posts replaced two dining posts. The grade-appeal question also picked up `health_center.txt` and `admin_meal_plan_changes.txt`, which weren't there before. The answers were unaffected because the model ignored the noise, but retrieval is not cleaner. I can tell because the retrieved-source lists in the two results files differ while the relevant-file counts are identical.

## What's Still Broken

No criterion is missed, but these problems are still there:

- **Noisy top-k.** 1–2 of every 4–5 retrieved files are relevant; the rest is filler that happens to share a word or a topic. I'd try either a stricter per-chunk cutoff (drop any chunk more than ~0.2 worse than the best one) or BM25 with a stopword list tuned to this corpus, so generic words like "behind" and "first" don't count as matches. I stopped here because the brief allows one change per unit, and the criteria as written can't show the difference.
- **The shuttle question's 0.593 distance.** Hybrid doesn't change distances, so it is still the answer most at risk of being refused. The next thing I'd test is keeping short posts whole (one post = one chunk) for posts under ~400 characters, so the "free with a student ID" sentence doesn't dominate the answer chunk.

## What I'd Do Differently

I'd write criteria that could actually fail. Criterion 1 would require the answer chunk to be **ranked first**, not just somewhere in the top 5. I'd add a precision criterion, like "at least half of retrieved chunks come from a relevant document", which would have caught the noise problem both before and after. And at least one of my five questions would need a paraphrase or two documents to answer, because all five of mine were written in the corpus's own words, so they were easy.
