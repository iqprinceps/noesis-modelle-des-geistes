# EP02_EN Voice Audition Selection

Identical audition excerpt: `pronunciation_test.txt`  
Voice in both: George (`JBFqnCBsd6RMkjVDRZzb`)  
Model: `eleven_multilingual_v2`

| Candidate | Settings | Duration | Scribe content match | Decision |
|---|---|---:|---:|---|
| A | stability 0.58, similarity 0.80, style 0.08, speed 1.06, seed 260802 | 13.189 s | 1.000 | SELECTED |
| B | stability 0.66, similarity 0.82, style 0.04, speed 1.03, seed 260822 | 14.164 s | 1.000 | Reserve only |

Candidate A is selected because it retains complete name/technical-term
intelligibility while moving 0.975 seconds faster across the same 36-word excerpt.
Its slightly greater style value gives the hook more forward pressure without
turning the evidence language theatrical. Candidate B remains a short audit file;
no complete B narration is generated.

The full master uses Candidate A's settings exactly. Any failed line is regenerated
as a targeted pickup with the same voice, model, settings, and seed family; the
master is never globally time-stretched.
