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

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |
| 5 |  |  |  |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
