# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in unit 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"Retrieval works"* is an opinion. *"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**Why this target:**
4 of 5 rather than 5 of 5 because my Kestrel Commons question uses the words "lunch rush" while the post says "between 12:15 and 1:00", and there are 14 other dining posts using the same "wait times" template, so I expect at least one question where the right chunk is outranked by a near-duplicate from another building. Lower than 4 would mean retrieval is failing on questions that each have one clear source document.

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:**
All five, not four, because every chunk carries its filename as metadata and the grounding instruction tells the model to cite it, so a missing source means the prompt is being ignored, not that the question was hard. Missing one would be a real failure, so I'm not leaving room for it.

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.

<!-- The five questions are the ones in `OUT_OF_SCOPE` at the bottom of
     `questions.py`, and `run_eval.py` puts them through the gate and writes
     what happened into your run log. Swap them for your own if you'd rather —
     just keep five of them, or the "4 of 5" above has nothing to be 4 of. -->

**Why this target:**
The OUT_OF_SCOPE questions (Mongolia, diesel engines, Rust) share almost no vocabulary with campus posts, so I expect a clear gap between the two groups of distances. I allow one miss because the ibuprofen question could land near the single health post in the corpus.

---

## 4. Chunks are complete, labelled thoughts

At least 4 of the 5 chunks printed by `python app.py chunks -n 5` start with the post's title line and end on a full sentence, and no chunk in the whole index is shorter than 80 characters.

**Why this target:**
The starter's fallback chunker produced a 2-character chunk on advice_threads, and a chunk like "Hours are 7am to 9pm" is useless if it doesn't say which dining hall it's about. Paragraph splitting plus the repeated title should fix both. 80 characters is the smallest size I saw that still held one complete fact. I allow 1 of 5 to miss because a few posts have no separate title line.


---

## 5. Answers contain the right specific fact

For at least 4 of my 5 test questions, the generated answer contains the `expects` phrase written in `questions.py` (for example "20 to 25 minutes" or "Fenwick Court").

**Why this target:**
The point of this corpus is specific student knowledge like numbers, deadlines and names, so a vague answer that cites the right file but drops the number would still be useless. I picked 4 of 5, not 5 of 5, because the model may paraphrase ("fifteen days" as "15 days"), which a plain string match would count as a miss even when the answer is right.


---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in unit 2:** For at least 4 of 5 questions, the top three
         > results contain the answer.
         >
         > **Why revised:** I couldn't judge "the chunks include one that
         > contains the answer" the same way twice — I scored two questions
         > differently on Monday than on Wednesday. The new version is
         > something I can actually check.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said 4 of 5 but got 2 of 5, so 2 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.

     The whole reason the originals stay visible is so someone can see what you
     said before you knew the answer.
     ───────────────────────────────────────────────────────────────────────── -->
