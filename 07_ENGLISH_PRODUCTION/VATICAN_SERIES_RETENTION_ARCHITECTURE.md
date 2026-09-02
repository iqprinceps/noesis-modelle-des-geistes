# Vatican Series — Retention Architecture

**Status:** English-original series design
**Scope:** EP13 to EP17

This document supersedes `03_EPISODEN/TYPE_B/VATIKAN_SERIE_REVIEW_CHECKPOINT_1.md`
and the retention sections of `VATIKAN_SERIE_FINAL_STORY_LOCK.md` for editorial
purposes. Those files remain valid as a record of the source-lock and rights work.

## The only real data the channel has

Checked against the YouTube Data and Analytics APIs on 2026-09-03. The repo
publication records were stale: EP05_EN went public on 2026-09-01, not on the
scheduled 09-05, and its first Short followed on 09-02. Neither has enough
watch time yet to report.

The usable measurement is EP01_EN Kozyrev Mirrors, public since 2026-08-27:
183 views, average view duration 2:09 on a 7:15 runtime, 29.8 percent average
view percentage. Its audience-retention curve is the first evidence this
channel has ever had.

| Time | Audience still watching |
|---|---:|
| 0:21 | 67.5% |
| 0:43 | 56.2% |
| 1:05 | 57.5% |
| 1:27 | 47.5% |
| 1:48 | 40.0% |
| 2:32 | 30.0% |
| 7:15 | 8.8% |

**Half the audience is gone by 1:27.** The two steep drops fall at 0:43, minus
11 points, and at 1:27, minus 10 points.

Mapped onto the EP01 script, both land on the same move. At 0:43 the episode
leaves its contradiction and starts describing the apparatus: cylinder,
clockwise spiral, counterclockwise spiral. At 1:27 it starts a biography:
`Nikolai Alexandrovich Kozyrev was a Soviet astronomer and astrophysicist.`

`00_GLOBAL/RETENTION_QA.md` already carries the rule that was broken:
`An episode-specific contradiction opens before biography or explanation.`

This single curve is worth more than every editorial prediction in the repo,
and it is still one video with 183 views. It is treated as a warning about a
specific failure mode, not as a target curve.

Earlier English episodes are therefore prior attempts, not standards. Their
measurements in `RETENTION_QA.md` are described there as historical records and
explicitly not a target range, and this series treats them the same way.

**Each episode is judged against its own promise.** The question is never whether
an episode matches another episode's hook count, beat density, question count or
word total. The question is what this specific episode promised the viewer in its
first thirty seconds, and whether the rest of it pays that promise.

Measurement is used here for one purpose only: to locate a passage worth reading
again. A number can show that two minutes pass without a turn. It cannot say
whether those two minutes are boring, and it cannot say that a different episode
would have solved it the same way. Every change in this package that was made to
move a number, rather than to serve the episode's own promise, has been reverted.

### What each episode promises

| Episode | Promise made in the opening | Therefore it must |
|---|---|---|
| EP13 | An object that cannot be where it is, and a text nobody was allowed to read | Make the sealed page worth waiting for, then reframe rather than resolve it, then return the object |
| EP14 | A letter that failed and survived, beside an archive sold by weight | Make survival improbable before explaining it, and make the loss land as loss |
| EP15 | A forgery that worked for centuries, undone by one word | Let the viewer find the word, and refuse to let the exposure end the story |
| EP16 | 508 pages of banned books, ended by one sheet of paper | Make administration feel consequential, and keep the ending withheld |
| EP17 | Two books, one young man, two incompatible realities | Tell the case, then make the viewer make the decision the institution had to formalise |

When retention data eventually exists, it replaces this table's assumptions. It
does not replace the principle that the episode is judged on its own terms.

## English-original, not adapted

Every previous English episode is an adaptation of a German master. This series
inverts that. The canonical scripts are the five `VOICE_SCRIPT_EN.txt` files. The
German packages under `03_EPISODEN/TYPE_B/EP13_VATIKAN_01` through `EP17_VATIKAN_05`
remain the authority for facts, claim boundaries, source registers and rights
locks, and they must not be sent to the English voice pipeline.

The reason is measurable. The German drafts use the templated antithesis pattern
`Not X, but Y` twenty-seven times across five scripts. `ENGLISH_PRODUCTION_STANDARD.md`
names that pattern as a marker of synthetic writing. Translating would have
carried all twenty-seven into English. The current English scripts contain none.

## What the German drafts got right, and keeps

- One physical object carries each episode. Envelope, sealed letter, forged
  charter, printed index, ritual book.
- The series thesis: an institution takes something uncertain and gives it a form.
- Mystery is never closed with a dismissive correction. Evidence boundaries are
  produced by naming precise subjects.
- Beat density. The German scripts run 7.0 to 8.6 words per beat, which suits
  material carried by objects and dates. That rhythm is preserved.

## The four defects this design corrects

### 1. The hook spent the payoff

Three of five German drafts stated their midpoint reveal in the cold open. EP13
described the vision before the act that reveals it. EP16 gave the date and
content of the 1966 notification in the first minute and then structured the
final act as its reveal.

**Rule for this series:** the hook states the impossible fact and the question.
It never states the answer. Every episode has one named withheld reveal, recorded
in its editorial map.

| Episode | Withheld until |
|---|---|
| EP13 | The vision text, and that the bishop in white does not survive |
| EP14 | Documents sold by weight during the return from Paris |
| EP15 | The word, hunted by the viewer before it is named |
| EP16 | The date and content of the 1966 notification |
| EP17 | Which category the case belongs in, never resolved |

### 2. The viewer was never in the room

Across the five German drafts, direct address to the viewer appears 3, 1, 2, 0
and 0 times. Two of the five never address the viewer at all. The drafts say
`One knows that the document exists`, which seats the viewer in a lecture rather
than in the story.

That is a defect on its own terms, independent of what any other episode does.
Each of these five episodes turns on a decision somebody had to make with
incomplete information, and an episode about deciding works better when the
viewer is asked to decide.

Every episode now has at least one sustained second-person passage placed at the
emotional centre: the hospital room in EP13, the crates in EP14, the ninth-century
reader in EP15, the scholar and the censor in EP16, the priest's assessment in EP17.

### 3. Interaction was deferred to the end card

Only one German draft had a viewer question inside the script. All five closed
with an essay question of the form `which is more powerful`, which asks for a
paragraph and therefore gets nothing.

Every episode now carries a one-word decision placed immediately before a new
evidentiary turn, and repeated in the closing line. One word is answerable while
still watching; a thesis question is not.

| Episode | Decision | Position |
|---|---|---|
| EP13 | `WORLD or MYSELF` | Before the document reveal |
| EP14 | `KEEP or LEAVE` | At the crates, before the loss is reported |
| EP15 | `CONSUL, SENATE, SATRAP` | Before the anachronism is named |
| EP16 | `BAN or CORRECT` | As the censor, before the 1948 return |
| EP17 | `ILLNESS or PRESENCE` | After the criteria, before the rite opens |

EP15 is deliberately an identification rather than an opinion. The viewer performs
textual criticism before the episode explains it.

### 4. Handoffs promised objects instead of stakes

The German drafts ended by naming the next episode's object: a document with
eighty-one seals, a book of forbidden books. An object is a subject line. It
gives no reason to come back.

Every handoff now carries a human consequence or an unresolved loss.

## Series loop

The closing form is named in every episode from EP13 onward, in the same grammar,
so the thesis accumulates instead of arriving only in the finale.

An envelope gave a vision a body.
An archive gave memory a place.
A charter gave a claim the authority of age.
A list gave dangerous knowledge a title.
A rite gave an invisible claim a procedure.

## Runtime

Runtime follows the material. Eight minutes is a monetisation threshold, not an
editorial target, and no episode may reach it with filler.

Delivered rates differ by language. The German masters run 125 to 135 words per
minute: EP01A 1,314 words in 9:42, EP02_V2 1,222 words in 9:46. The English
narrator is faster. EP01_EN delivers 1,070 words in 7:15, which is 148 words per
minute including pauses, beds and end screen. English runtimes are therefore
calculated at 148.

The German Vatican drafts stood at 872 to 962 spoken words, which projects to
roughly 6:45. The checkpoint rewrite had over-corrected by about 36 percent and
left the series three minutes under the channel's own produced baseline.

Current English scripts:

| Episode | Words | At 148 WPM | Margin over 8:00 |
|---|---:|---:|---:|
| EP13 | 1,331 | 9:00 | +147 |
| EP14 | 1,194 | 8:04 | +10 |
| EP15 | 1,302 | 8:48 | +118 |
| EP16 | 1,288 | 8:42 | +104 |
| EP17 | 1,374 | 9:17 | +190 |

EP14 clears the eight-minute threshold by ten words. Any trim in the edit puts
it under, so it carries no cutting room at all.

Final duration comes from the approved voice master and forced alignment.

## Open production risks

**EP14 and EP16 hero assets.** Both episodes are carried by an object the rights
lock cannot supply as a photograph: the 81-seal letter and the 1948 Index volume.
Both are also the thumbnail. Under the English standard the reconstruction is
carried by cinematic language with an optional 1.5 to 2.0 second disclosure at
first entry, never a permanent badge. A rights-clear photograph of either
original would raise those episodes more than any further script work.

**EP17 case detail.** The cold open narrates the Lancashire case. Those details
are the least locked material in the package and the editorial map treats the
verification as a hard gate before voice.

**EP17 beat density.** At 15.4 words per beat it is the loosest script in the
set. Worth a line-breaking pass during cue-sheet work rather than a rewrite.

## Publication order

Editorial order is EP13 to EP17 and the handoffs are written for it.

If the first two weeks of retention data show a drop between EP13 and EP14, the
strongest available correction is to move EP15 into second position. Its content
does not depend on EP14, and only the two handoff passages would need rewriting.
EP14 and EP16 are the two reconstruction-hero episodes, and they are stronger
later in a run, once the audience is already committed.
