# EP13_EN — Pronunciation Sheet

For the English narrator. Every proper name spoken in `VOICE_SCRIPT_EN.txt` is
listed. Respellings are for an English delivery: the goal is a confident,
consistent English reading, not a native Portuguese or Turkish accent.

| Name | Occurrences | Respelling | Note |
|---|---:|---|---|
| Fatima | 4 | **FAT-uh-muh** | Use the established English pronunciation, stress on the first syllable. Do not switch to Portuguese `FAH-tee-mah` mid-episode. The script deliberately writes it without the accent so the voice engine does not shift stress. |
| Lucia dos Santos | 1 full, 2 short | **loo-SEE-uh dosh SAHN-toosh** | Portuguese, not Italian. `dos` is `dosh`, final `s` in Santos is `sh`. If the engine cannot hold this, fall back to **loo-SEE-uh dos SAN-tos** consistently rather than alternating. |
| Sister Lucia | 1 | **loo-SEE-uh** | Same vowel as above. |
| John Paul II | 2 | **john paul the SECOND** | Spoken as `the Second`, never `the two` or `I I`. |
| John XXIII | 1 | **john the twenty-THIRD** | Spoken as `the Twenty-Third`. |
| Paul VI | 1 | **paul the SIXTH** | Spoken as `the Sixth`. |
| Cardinal Angelo Sodano | 1 | **AN-jel-oh so-DAH-noh** | Italian. Soft `g` in Angelo. |
| Mehmet Ali Agca | 1 | **MEH-met ah-LEE AH-jah** | Turkish `Ağca`. The `ğ` is silent and lengthens the preceding vowel, giving roughly `AH-jah`. Avoid a hard `g`. The script writes it without the diacritic for pipeline safety. |
| Our Lady of the Rosary of Fatima | 1 | **ROH-zuh-ree** | Full title read as one phrase, no pause before `of Fatima`. |
| Holy Office | 1 | plain | Institution, capitalised in the script, no special handling. |
| Holy Father | 1 | plain | Inside the quoted impression of the children. |
| Saint Peter's Square | 2 | plain | |
| Napoleon | 1 | **nuh-POH-lee-un** | In the EP14 handoff. |
| Rome, Portugal, Portuguese, Russia, England, Italian, Alps, Vatican, Church | — | plain | No handling needed. |

## Numbers and dates

The script writes dates in words so the voice reads them naturally. Confirm the
engine does not re-expand them.

| Written | Must be read as |
|---|---|
| `the thirteenth of May, 1981` | thirteenth of May, nineteen eighty-one |
| `the thirteenth of May, 1917` | thirteenth of May, nineteen seventeen |
| `the third of January, 1944` | third of January, nineteen forty-four |
| `the eighteenth of July, 1981` | eighteenth of July, nineteen eighty-one |
| `Sixty-four years earlier` | as written |
| `Twenty-seven years later` | as written |
| `Five nineteen in the afternoon` | five nineteen, not `five point one nine` |
| `In 1957`, `In 1959`, `in 1989`, `in the year 2000` | nineteen fifty-seven, nineteen fifty-nine, nineteen eighty-nine, the year two thousand |
| `eighty-three`, `eighty-one` | as written, in the EP14 handoff |

## Interaction keywords

`WORLD` and `MYSELF` appear in caps twice each, at the midpoint decision and in
the closing line. They are read as ordinary spoken words with slight emphasis,
not spelled out and not shouted. The caps exist for the on-screen card and the
pinned comment.

## Delivery notes

- Measured channel rate for the English narrator is 148 words per minute
  including pauses. At 1,336 words this episode lands near 9:00.
- The cold open runs on short beats. Let the three-word lines breathe rather
  than reading them as one sentence: `It was fired at a pope. / He survived.`
- `And the bishop in white does not survive. / The man reading it in July 1981
  did.` is the turn of the episode. It needs a real pause between the two lines.
- The vision passage is reported speech from a document. Read it level. Do not
  perform it as horror.
