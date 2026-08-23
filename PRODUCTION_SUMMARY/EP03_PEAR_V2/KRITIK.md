# PEAR — Kritik- und Replikationsgeschichte

> Recherchestand: 21.08.2026, vollständig (Abschnitte 1–7 plus Quellenliste).
> Gliederung strikt nach: BELEGT / BEHAUPTUNG DER BETEILIGTEN / KRITIK / UNBELEGT KURSIEREND.
> Originalzitate bleiben im englischen Original. Keine Wertung des Rechercheurs.
> Vier offene Verifizierungspunkte am Dateiende.
>
> **Inhalt**
> 1. Die Freiburg–Gießen–Replikation (PortREG) — Zahlen, Wortlaut, Rahmung
> 2. Die Effektgröße, ausgerechnet mit Rechenweg
> 3. Der Einwand des einzelnen Operators („Operator 10")
> 4. Methodische Kritik im Einzelnen (Jeffers, Hyman, Alcock, Park)
> 5. Die Gegenrede von Jahn und Dunne
> 6. Wie die Fachwelt heute darauf blickt
> 7. Die drei stärksten und die drei schwächsten Punkte der Kritik

---

## 1. Die Freiburg–Gießen–Replikation (PortREG / Mind-Machine-Interaction-Konsortium)

### 1.1 BELEGT — Primärquelle

**Zitation:**
Jahn, R. G.; Mischo, J.; Vaitl, D.; Dunne, B. J.; Bradish, G. J.; Dobyns, Y. H.;
Lettieri, A.; Nelson, R. D.; Boller, E.; Bösch, H.; Houtkooper, J.; Walter, B. (2000):
*Mind/Machine Interaction Consortium: PortREG Replication Experiments.*
**Journal of Scientific Exploration 14(4), S. 499–555.**

- Volltext-PDF (ICRL, Nachfolgeorganisation von PEAR):
  http://icrl.org/wp-content/uploads/2020/02/2000-mmi-consortium-portreg-replication.pdf
- Weitere Kopien:
  https://www.researchgate.net/publication/244404973_MindMachine_Interaction_Consortium_PortREG_Replication_Experiments
  https://www.academia.edu/6873653/Mind_Machine_Interaction_Consortium_PortREG_Replication_Experiments
- Abstract-Referat: https://www.thefreelibrary.com/Mind/machine+interaction+consortium:+Port+REG+replication...-a084547075

**Die drei beteiligten Labore (Eigenbezeichnungen im Paper):**

| Kürzel | Institution | Ort |
|---|---|---|
| PEAR | Princeton Engineering Anomalies Research, Princeton University | Princeton, NJ |
| FAMMI | *Freiburg Anomalous Mind/Machine Interactions*, Institut für Grenzgebiete der Psychologie und Psychohygiene e.V. (IGPP) | Freiburg |
| GARP | *Giessen Anomalies Research Project*, Justus-Liebig-Universität Gießen | Gießen |

**Zeitraum:** Konsortium gegründet **1996**; Ergebnisse veröffentlicht **2000**.
Das Paper nennt die Replikation ausdrücklich „the first collaborative project undertaken".

### 1.2 BELEGT — Versuchsplan (vorab festgelegt)

Wörtlich aus dem Abstract (S. 499):

> „The agreed upon primary criterion for the anomalous effect was the magnitude of the
> HI–LO data separation, but data also were collected on a number of secondary correlates."

Und aus Abschnitt II.A (S. 505 f.):

> „Although the primary hypothesis to be tested was confirmation of the earlier PEAR results
> on a simple HI–LO mean-shift criterion, secondary investigations were to provide structural
> data on the characteristics and correlates of the phenomena. Specifically, it was agreed that
> each laboratory would use large pools of operators to accumulate 250 experimental 'sessions'
> or 'series,' each series consisting of 1000 200-sample trials in each of the HI, LO, and BL
> intentions …"

Das ist der entscheidende Punkt: **Das Erfolgskriterium (HI–LO-Mittelwertdifferenz) war vor
der Datenerhebung zwischen den drei Laboren vereinbart** — anders als bei den früheren
PEAR-Studien, denen genau das fehlte (siehe Abschnitt 4).

**Umfang:**
- 3 Labore × 250 Serien = **750 Serien**
- pro Serie 1000 Trials je Intention (HI / LO / BL), Trial = Summe aus **200 binären Samples**
  → 3.000 Trials pro Serie → **2.250.000 Trials insgesamt** (= 450 Mio. Bits)
- **227 Operatoren** (FAMMI 80, GARP 69, PEAR 78)
- identische Hardware („PortREG", thermisches Widerstandsrauschen) in allen drei Laboren
- begleitende, unbeaufsichtigte Kalibrierläufe: 1.049 Serien; GARP und PEAR je über 1 Mio.
  Kalibrier-Trials, FAMMI über 850.000

### 1.3 BELEGT — Das Ergebnis in Zahlen

Aus den Tabellen 0 und C.1 des Papers (μ = Mittelwertverschiebung pro 200-Bit-Trial gegenüber
der Zufallserwartung 100; s = empirische Standardabweichung; Z = Z-Wert):

**Tabelle 0 — Frühere PEAR-Daten (522 Serien, 91 Operatoren):**

| | BL | LO | HI | Δ (HI–LO) |
|---|---|---|---|---|
| μ | 0,013372 | −0,015586 | 0,025994 | **0,020800** |
| s | 7,074 | 7,069 | 7,070 | 7,070 |
| Z | 1,7132 | −2,0161 | 3,3688 | **3,8087** |

**Tabelle C.1 — Replikation, alle drei Labore zusammen (750 Serien, 227 Operatoren):**

| | BL | LO | HI | Δ (HI–LO) |
|---|---|---|---|---|
| μ | 0,001008 | −0,004752 | 0,002135 | **0,003443** |
| s | 7,0575 | 7,0556 | 7,0683 | 7,0619 |
| Z | 0,1235 | −0,5820 | 0,2614 | **0,5964** |

**Einzellabore (Δ-Spalte):**
- FAMMI (Freiburg), 250 Serien / 80 Operatoren: μ = 0,006416; Z = **0,6416**
- GARP (Gießen), 250 Serien / 69 Operatoren: μ = 0,002258; Z = **0,2258**
- PEAR (Princeton), 250 Serien / 78 Operatoren: μ = 0,001656; Z = **0,1656**

**Kalibrierungen (Tabelle 00, 1.049 Serien):** FAMMI μ = −0,000901 (Z = −0,1175);
GARP μ = 0,000166 (Z = 0,0253); PEAR μ = −0,000207 (Z = −0,0305) — die Geräte selbst
verhielten sich im unbeaufsichtigten Leerlauf erwartungsgemäß.

**Kernaussagen des Papers, wörtlich:**

Abstract (S. 499):

> „The primary result of this replication effort was that whereas the overall HI–LO mean
> separations proceeded in the intended direction at all three laboratories, the overall sizes
> of these deviations **failed by an order of magnitude** to attain that of the prior experiments,
> **or to achieve any persuasive level of statistical significance.**"

Abschnitt III.A, S. 515:

> „… we conclude that this hypothesis has not been confirmed. Although the agreed upon primary
> indicators of effect, the HI–LO (Δ) mean shifts and their corresponding Z-scores, progress in
> the intended directions in all three laboratory results and in their cross-laboratory
> combinations, the effect size is essentially one order of magnitude smaller than for the prior
> data (.0034 versus .0208) and thus falls well below any credible statistical significance
> (Z = 0.596 versus 3.809)."

Direkt anschließend (S. 516) — die schärfste Formulierung, und sie stammt von den Autoren selbst:

> „Alternatively stated, if the prior PEAR results are used as the standard of replication,
> **this prediction is refuted at a Z = −2.87 level.**"

> „… this **stark failure to replicate** reaffirms an enduring and ubiquitous 'reproducibility
> problem' that has long characterized mind/machine interaction experiments of this class."

Zusammenfassung, Abschnitt IV, S. 538 f.:

> „As far as the replication results themselves are concerned, **we are left with an empirical
> paradox.** Whereas the prior PEAR experiments clearly displayed anomalous secular trends in
> REG output distribution means in correlation with operator intention, the three-laboratory
> replications, which employed essentially similar equipment and protocols, failed by an order
> of magnitude to replicate the primary correlations."

**Merke für die Folge:** Das Ergebnis ist nicht bloß „nicht signifikant". Die PEAR-Vorhersage
wurde mit **Z = −2,87** (≈ p = 0,004 einseitig; das Paper nennt diesen p-Wert auf S. 542 selbst)
zurückgewiesen. Diese Zahl stammt aus dem Paper der Beteiligten, nicht von Kritikern.

### 1.4 BEHAUPTUNG DER BETEILIGTEN — wie sie das Ergebnis gerahmt haben

Die Autoren akzeptieren das Scheitern beim Primärkriterium und verlagern die Deutung auf
„strukturelle Anomalien" in Sekundärparametern. Wörtlich, Abstract:

> „However, various portions of the data displayed a substantial number of interior structural
> anomalies in such features as a reduction in trial-level standard deviations; irregular
> series-position patterns; and differential dependencies on various secondary parameters, such
> as feedback type or experimental run length, to a composite extent well beyond chance
> expectation. The change from the systematic, intention-correlated mean shifts found in the
> prior studies, to this polyglot pattern of structural distortions, testifies to inadequate
> understanding of the basic phenomena involved and suggests a need for more sophisticated
> experiments and theoretical models for their further elucidation."

Die Turbulenz-Metapher (S. 538) — sehr gut als O-Ton:

> „To borrow a fluid mechanical metaphor, **it is as if the influence of operator intention now
> was manifesting itself as a structural 'turbulence' in the output data of the replication,
> rather than in a more orderly displacement of the data streams** as was found in the prior
> PEAR studies."

Zur Größenordnung dieser Sekundärbefunde (S. 544):

> „Appendix II outlines conservative meta-analytical computations that place the composite
> structural anomalies at a level of chance expectation in the range of 0.001 to 0.002
> (two-tailed). This approaches the level of significance that would have been achieved had the
> overall mean-shift replication been successful."

Die sieben Prämissen, die sie im Nachhinein infrage stellen (Abschnitt IV, S. 539–544):
1. *Source independence* — der einfachere PortREG könnte doch nicht gleichwertig sein.
2. *Operator pool equivalence* — anderer Operatorenpool.
3. *Insensitivity to secondary parameters* — Feedback-Art und Run-Länge könnten doch zählen.
4. *Insensitivity to operator attitudes* — Stimmung, Laboratmosphäre, „permission to succeed".
5. *Intention as primary correlate* — vielleicht ist „Intention" gar nicht die richtige Variable.
6. *Replication criterion* — die Replizierbarkeitsnorm selbst wird infrage gestellt.
7. *Anomaly indicators* — vielleicht sind Strukturmerkmale die eigentlichen Indikatoren.

Zu Punkt 1 (S. 539 f.) begründen sie die Abweichung u. a. damit, der PortREG sei als
„small, unobtrusive gray box" ein weniger auffälliger Bestandteil des Aufbaus gewesen; ein
Operator habe zudem vermutet, die Allgegenwart von Bildschirmen habe „much of the novelty of
this format of human/machine interaction" erodiert.

Zu Punkt 6 wörtlich (S. 543):

> „The concept of objective replication or falsification is crucial to the exact sciences. Yet
> examples abound where varying degrees of compromise with rigorous replicability have been
> tolerated out of pragmatic necessity. … **To expect that these hypercomplex systems will
> submit to classical expectations of causality, determinism, and replicability may be overly
> presumptive.**"

Der Versuch, das Scheitern statistisch zu relativieren (S. 542, „Epochen"-Argument):

> „… when PEAR itself, employing a known, productive experiment with the same protocols and
> operator pools, generated an REG database of the scale of PortREG three times in succession,
> it failed to show anomalous yield one time in three. In this view, the joint failure of three
> laboratories to replicate is an event with p = .037, rather than the p = .004 one would infer
> from the above Z-score."

Zu Punkt 3 eine im Video zitierfähige Post-hoc-Selektion (S. 541):

> „Indeed, the breakdown by secondary parameter cells in Table C.7 indicates that data generated
> solely in the most conducive secondary conditions had effect sizes comparable to those seen in
> the prior PEAR experiments."

Schlusssatz des Hauptteils (S. 546):

> „The change from systematic, intention-correlated deviations to a comparably anomalous, albeit
> less orderly pattern of structural distortions testifies to our incomplete understanding of the
> basic phenomena, and warns that future empirical and conceptual efforts must proceed at a more
> sophisticated level."

### 1.5 BELEGT — ein Nebenbefund, der zu Abschnitt 3 gehört

Tabelle P.7 des Papers („Consistency of Operators Between Prior PEAR and Replication
Experiments") vergleicht fünf Operatoren, die an beiden Studien teilnahmen. Vier zeigen nichts
(p = .29 bis .90). Einer, im Paper nur „Operator E" genannt, sticht heraus:
**χ² = 14,035 (p = .003), Z = 3,255 (p = .001, zweiseitig).** Auch in der gescheiterten
Replikation lieferte also ein einzelner, dem Labor bekannter Operator einen signifikanten Wert,
während die Gesamtstichprobe null ergab. Siehe Abschnitt 3.

### 1.6 KRITIK an dieser Rahmung (Vorgriff, Details in Abschnitt 4)

Kernpunkt: Die strukturellen Anomalien waren **nicht vorab spezifiziert**; das Primärkriterium
war es. Das Paper räumt das für einen Teilbereich selbst ein (S. 542):

> „While it is difficult to establish a Bonferroni-type correction factor for this sort of
> retrospective reexamination of an extant database …"

---

## 2. Die Effektgröße — ausgerechnet

### 2.1 BELEGT — Ausgangszahlen

Aus Tabelle 0 des PortREG-Papers (frühere PEAR-Benchmark-Daten, 522 Serien, 91 Operatoren):
- Δμ = **0,020800** (Mittelwertverschiebung pro Trial in Richtung der Absicht)
- Ein Trial = **200 Bits**; Zufallserwartung des Trials = 100; theoretische σ₀ = √50 = 7,071
- Z(Δ) = 3,8087

### 2.2 Rechenweg

**Schritt 1 — Verschiebung pro Bit:**

    0,020800 zusätzliche Treffer pro Trial ÷ 200 Bits pro Trial
      = 0,000104 zusätzliche Treffer pro Bit
      = 1,04 · 10⁻⁴

Die Trefferwahrscheinlichkeit verschiebt sich also von p = 0,500000 auf **p ≈ 0,500104**.

**Schritt 2 — als „einer von wie vielen":**

    1 ÷ 0,000104 ≈ 9.615

→ **Rund ein zusätzlicher Treffer auf 10.000 Münzwürfe.**

**Schritt 3 — Kontrolle über den Datenumfang (aus Z zurückgerechnet):**

    Z = (Δμ / σ₀) · √Nt
    → √Nt = Z · σ₀ / Δμ = 3,8087 · 7,071 / 0,020800 = 1.294,7
    → Nt ≈ 1.676.000 Trials (HI und LO zusammengefasst)

Gegenprobe aus dem Papertext: PEAR beziffert die frühere Datenbasis als „approximately
equivalent to 834 PortREG series", also 834 × 1.000 Trials je Intention × 2 Intentionen
= 1.668.000 Trials. Stimmt überein.

    1.676.000 Trials × 200 Bits ≈ 335 Millionen Bits
    335.000.000 × 0,000104 ≈ 34.800 zusätzliche Treffer

### 2.3 Ein-Satz-Formulierungen für Laien (rechnerisch gedeckt)

- **„PEAR hat rund 335 Millionen Münzwürfe ausgewertet und dabei etwa 35.000 Treffer mehr
  gefunden, als der Zufall erwarten lässt — ungefähr ein zusätzlicher Treffer auf 10.000 Würfe."**
- Alternative: „Statt 50,0000 Prozent kamen 50,0104 Prozent heraus."
- Alternative: „Von 10.000 Bits kippte im Schnitt eines mehr in die gewünschte Richtung."

*(Nur HI: 0,025994 / 200 = 1,30 · 10⁻⁴ → rund 1 auf 7.700. Nur LO: 0,015586 / 200 = 7,79 · 10⁻⁵
→ rund 1 auf 12.800. Die „1 auf 10.000" ist der HI-LO-Mittelwert, also genau die Größe, die PEAR
selbst als Primärkriterium führte.)*

### 2.4 Zum Vergleich: die Effektgröße der Replikation

    Δμ = 0,003443 ÷ 200 Bits = 1,72 · 10⁻⁵
    1 ÷ 0,0000172 ≈ 58.100

→ **rund ein zusätzlicher Treffer auf 58.000** — bei 750 Serien × 1.000 Trials × 2 Intentionen
= 1,5 Mio. Trials = 300 Mio. Bits also gut **5.100 zusätzliche Treffer**, was bei diesem Umfang
mit Z = 0,60 vollständig im Zufallsbereich liegt.

Gegenprobe des Z-Werts: 0,003443 / 7,0619 × √1.500.000 = 0,000488 × 1.224,7 = **0,597**
(Paper: 0,5964). ✔

---

## 3. Der Einwand des einzelnen Operators („Operator 10")

### 3.1 BELEGT — wer es zuerst geschrieben hat

**Zuerst benannt: John Palmer, 1985** — und zwar nicht von einem Skeptiker, sondern von einem
Parapsychologen. McCrone (1994) schreibt dazu wörtlich:

> „Suspicions have hardened as sceptics have looked more closely at the fine detail of Jahn's
> results. Attention has focused on the fact that **one of the experimental subjects — believed
> to be a member of the PEAR laboratory staff — is almost single-handedly responsible for the
> significant results of the studies. This was noted as long ago as 1985 by a fellow
> parapsychologist, John Palmer of Durham University, North Carolina, who wrote a report on
> Jahn's work for the US Army.**"

Der gemeinte Bericht: Palmer, John (1985): *An Evaluative Report on the Current Status of
Parapsychology.* U.S. Army Research Institute for the Behavioral and Social Sciences, Alexandria
VA, Contract DAJA 45-84-M-0405. DTIC-Volltext: https://apps.dtic.mil/sti/tr/pdf/ADA169486.pdf
*Achtung: Die Zuschreibung an Palmer stammt aus McCrone 1994. Der DTIC-Server lieferte bei dieser
Recherche keinen Volltext aus (HTTP 403). Die Seitenangabe im Palmer-Report muss von Hand
verifiziert werden, bevor sie im Video als Fundstelle genannt wird — die McCrone-Aussage über
Palmer ist dagegen zitierfähig.*

**Breit bekannt gemacht: John McCrone, 1994.**
McCrone, John: *Psychic powers: What are the odds?* **New Scientist, 26. November 1994, S. 34–38.**
Der vollständige Artikel liegt als Scan im CIA Reading Room / Internet Archive:
https://archive.org/details/cia-readingroom-document-cia-rdp96-00789r003200250001-9
(Volltext-Datei: .../cia-rdp96-00789r003200250001-9_djvu.txt;
Dokument-ID CIA-RDP96-00789R003200250001-9)

### 3.2 BELEGT — was McCrone wörtlich schreibt

Zur Effektgröße:

> „The size of the effect is about 0.1 per cent, meaning that for every thousand electronic
> tosses, the random event generator is producing about one more head or tail than it should by
> chance alone."

*(Anmerkung zur Zahl: McCrones „1 auf 1.000" ist großzügiger gerundet als die aus den
Originaltabellen gerechnete Größe von rund 1 auf 10.000 — siehe Abschnitt 2. Im Video sollte
die eigene Rechnung aus Tabelle 0 verwendet werden, nicht McCrones Zahl.)*

Zum Operator 10 (McCrone referiert Palmers Befund und aktualisiert ihn):

> „One subject — known as operator 10 — was by far the best performer, and this trend has
> continued. On the most recently available figures, **operator 10 has been involved in only
> 15 per cent of the 14 million trials but contributed a full half of the total 'successes'.**"

Was passiert, wenn man ihn herausrechnet:

> „If this person's figures are taken out of the data pool, scoring in the 'low intention'
> condition falls to chance while 'high intention' scoring drops close to the .05 probability
> boundary considered weakly significant in scientific results."

Zur Identität:

> „Jahn admits that operator 10 — whom he insists must remain anonymous — has been responsible
> for a large proportion of the significant findings."

McCrone hält fest, Operator 10 sei „believed to be a member of the PEAR laboratory staff" —
also eine **Vermutung**, keine Bestätigung.

### 3.3 BEHAUPTUNG DER BETEILIGTEN — Jahns Antwort (im selben Artikel, wörtlich)

> „at least four or five other of the 100 subjects show a more powerful effect than operator 10.
> What is different is that they have been involved in far fewer trials."

> „if these better performers had been able to do as many runs as operator 10 — and if the
> strength of their effects persisted — then operator 10's results would have dropped away into
> the background."

> „when the contributions of all the operators are plotted, they form a smooth continuum. Just
> as there are a few high performers like operator 10 at one end of the spectrum, so there are an
> equal number of poor performers … at the other end."

> „With over 100 subjects, statistically speaking there would have to be a few high-end scorers
> like operator 10, so no sinister conclusions should be drawn from that fact alone."

Ausführlicher, elf Jahre später, in Jahn & Dunne (2005), *The PEAR Proposition*, JSE 19(2),
195–246, S. 211 f. (PDF: https://www.pear-lab.com/pdfs/2005-pear-proposition.pdf):

> „… of the 91 operators contributing to this database of over 1.5 million experimental trials,
> the results of only six lie outside the 0.05 confidence hyperbola in the intended direction of
> HI − LO separation, while two others fall outside in the direction opposite to intention,
> compared to the roughly 4.5/4.5 expected by chance. This hardly overwhelming result is
> complemented by the observation that 47 of the operator points lie above the chance mean and
> 44 below, which is also statistically unimpressive. Notwithstanding, the composite array of
> these 91 operator achievements has its mean value shifted from zero to 0.041, which is a hugely
> significant aberration (p ≈ 7.0 × 10⁻⁵). **Thus, such data assert that the collective anomaly
> is not primarily driven by distinguishable 'superstars,' but rather by a collective array of
> inextricably small individual effects, achieved over many large datasets.**"

Im PortREG-Paper von 2000 (S. 540 f.) formulieren dieselben Autoren die Prämisse so:

> „This presumption seemed soundly based on extensive earlier results that these anomalous
> effects **invariably appeared as broadly distributed, marginal shifts over the full operator
> population, rather than being dominated by a few exceptional operators** (Jahn et al., 1997)."

### 3.4 BELEGT — was in PEARs eigenen Zahlen dazu steht

Aus Jahn, Dunne, Nelson, Dobyns & Bradish (1997), *Correlations of Random Binary Sequences with
Pre-Stated Operator Intention: A Review of a 12-Year Program*, JSE 11(3), 345–367, Abschnitt III.A
(PDF: https://www.pear-lab.com/pdfs/1997-correlations-random-binary-sequences-12-year-review.pdf):

> „For example, 57% of the series display HI–LO score separations in the intended direction
> (zs = 3.15, ps = 8 × 10⁻⁴). In contrast, **the anomaly is not statistically evident in the 52%
> of individual operators producing databases in the intended directions (z₀ = 0.31, p₀ = 0.38)**,
> a feature having possible structural implications …"

Ebenda, Abschnitt III.D („Individual Operator Effects"):

> „Unfortunately, quantitative statistical assessment of these is complicated by the unavoidably
> wide disparity among the operator database sizes, and by the small signal-to-noise ratio of the
> raw data, leaving graphical and analytical representations of the distribution of individual
> operator effects only marginally enlightening."

Und aus dem PortREG-Paper 2000, Tabelle P.7 („Consistency of Operators Between Prior PEAR and
Replication Experiments"): von fünf Operatoren, die an beiden Studien teilnahmen, liefert
„Operator E" **χ² = 14,035 (p = .003) und Z = 3,255 (p = .001 zweiseitig)**, die vier anderen
nichts (p = .29 bis .90).

### 3.5 KRITIK — die parallele Zahl von Ray Hyman

Ray Hyman rechnete bereits 1989 vor, dass die Trefferquote „in the intended direction was only
50.02%" und dass **eine** Operatorin „was responsible for 23% of the total data base. Her hit
rate was 50.05%."
Quelle: Hyman, Ray (1989): *The Elusive Quarry: A Scientific Appraisal of Psychical Research.*
Buffalo, NY: Prometheus Books, S. 152.
*Diese Zitate habe ich sekundär über The Skeptic's Dictionary (https://www.skepdic.com/pear.html)
— eine Meinungs-/Skeptikerseite. Vor Verwendung im Video am Buch verifizieren.*

### 3.6 UNBELEGT KURSIEREND — ausdrücklich NICHT als Tatsache sagen

- **„Operator 10 war Brenda Dunne."** Kursiert in Foren, Blogs und Kommentarspalten. Dafür gibt
  es **keinen Beleg**. McCrone schreibt nur „believed to be a member of the PEAR laboratory
  staff"; Jahn hat die Identität nie preisgegeben. Im Video höchstens als *kursierende Vermutung*
  markieren — mit dem Zusatz, dass sie unbelegt ist.
- **„Operator 10 gehörte zum Laborpersonal."** Ebenfalls nur eine Annahme („believed to be"),
  von PEAR nie bestätigt und nie dementiert. Belegt ist allein Jahns Eingeständnis, dass
  Operator 10 „responsible for a large proportion of the significant findings" war und anonym
  bleiben müsse.
- **„Ohne Operator 10 bleibt gar nichts übrig."** Zu stark. McCrone schreibt: LO fällt auf
  Zufallsniveau, HI sinkt „close to the .05 boundary" — also nicht auf null. Die Datengrundlage
  dieser Rechnung (Stand ~1994, 14 Mio. Trials, alle Gerätetypen) ist zudem nicht identisch mit
  der Benchmark-Datenbank von 2,4972 Mio. Trials aus Jahn et al. 1997.
- **Zitierfähig sind nur die McCrone- und die Hyman-Formulierung** — beide in der obigen,
  vorsichtigen Form.

---

## 4. Methodische Kritik im Einzelnen

### 4.1 BELEGT — Stanley Jeffers, *The PEAR Proposition: Fact or Fallacy?*

**Zitation:** Jeffers, Stanley (2006): *The PEAR Proposition: Fact or Fallacy?*
**Skeptical Inquirer 30(3), Mai/Juni 2006, S. 54–57.**
Volltext-PDF: https://cdn.centerforinquiry.org/wp-content/uploads/sites/29/2006/05/22164608/p54.pdf
Jeffers ist Physiker am Department of Physics and Astronomy, York University, Toronto.

**(a) Kontrolle der Zufallsquelle / Kalibrierung** (S. 55 f.):

> „One characteristic of the methodology employed in experiments in which I have been involved is
> that for every experiment conducted in which a human has consciously tried to bias the outcome,
> another experiment has been conducted immediately following the first when the human
> participant is instructed to ignore the apparatus. Our criterion for significance is thus
> derived by comparing the two sets of experiments. **This is not the methodology of the PEAR
> group, which chooses to only occasionally run a calibration test of the degree of randomness of
> their apparatus.** We contend, although Dobyns (2000) has disputed our claim, that our
> methodology is scientifically more sound."

**(b) Replikation** (S. 56):

> „If the claims are credible, it should be possible for other groups to replicate them. To their
> credit, the PEAR group did enlist two other groups, both based at German universities (Jahn et
> al. 2000) to engage in a triple effort at replication. **These attempts failed to reproduce the
> claimed effects. Even the PEAR group was unable to reproduce a credible effect.**"

**(c) Baseline-Drift / „Baseline Bind"** — Jeffers' schärfster Punkt (S. 56):

Er zitiert zunächst Jahn & Dunne, *Margins of Reality* (1987), zum frühen Befund:

> „namely, of the seventy-six baseline series performed, seven or eight of the means would be
> expected to exceed the 0.05 terminal probability criterion, in one direction or the other,
> simply by chance. In fact not one of them does."

Jeffers' Kommentar:

> „In other words, **the baseline data are too good.** The means of the baseline data conform to
> the means of the calibration data, but the variance of the baseline data is less than that of
> the calibration data."

Und für die Gesamtdatenbank (Figur 4 seines Artikels: alle 91 Operatoren, ~2,5 Mio. Trials):

> „**The baseline data in figure 4 violate PEAR's own criteria for significance** (i.e., p<.05
> terminal probability), and consequently — according to PEAR's own standards — must be regarded
> as evidence for nonrandom behavior in the baseline data. **This has to call into question the
> claimed statistical significance of the data labeled HI and LO in the same plot.**"

*(Zur Einordnung: In Tabelle 0 des PortREG-Papers steht für die früheren PEAR-Daten
BL: μ = 0,013372 mit Z = 1,7132 — die Baseline weicht dort also selbst um mehr als 1,7 σ ab,
während die theoretische Erwartung 0 wäre. Das ist die Zahl hinter Jeffers' Einwand.)*

**(d) Post-hoc-Befunde statt Vorhersagen** (S. 55):

> „Some of the claims advanced by the PEAR group are post-dictions, for example, the claims for
> gender bias, baseline bind, etc. **None of these are actually predicted by any of the many
> interpretations of quantum mechanics.**"

**(e) Fazit** (S. 57):

> „This paper argues that in the light of the difficulties in replication (even by the PEAR group
> itself), the lack of anything approaching a theoretical basis for the claims made, and, perhaps
> most damaging, the published behavior of the baseline data of the PEAR group which by their own
> criteria indicate nonrandom behavior of the device that they claim is random … There are
> reasonable and rational grounds for questioning these claims. Despite the best efforts of the
> PEAR group over a twenty-five-year period, **their impact on mainstream science has been
> negligible.** The PEAR group might argue that this is due to the biased and blinkered mentality
> of mainstream scientists. **I would argue that it is due to the lack of compelling evidence.**"

**(f) Jeffers' eigene Replikationsversuche:**
- Ibison, M. & Jeffers, S. (1998): *A double slit experiment to investigate claims of
  consciousness-related anomalies.* Journal of Scientific Exploration 12(4), 543–550.
  — Nullresultat.
- Jeffers, S. (2003): *Physics and claims for anomalous effects due to consciousness.* In:
  Alcock, J.; Burns, J.; Freeman, A. (Hg.): *Psi Wars: Getting to Grips with the Paranormal.*
  Exeter: Imprint Academic, S. 135–152.

### 4.2 BELEGT — Ray Hyman

- Hyman, Ray (1989): *The Elusive Quarry: A Scientific Appraisal of Psychical Research.*
  Buffalo, NY: Prometheus Books. Zu PEAR insbesondere S. 152 (Zahlen siehe 3.5).
- Hyman gehörte außerdem dem Ausschuss des **National Research Council** (USA) an, dessen
  Bericht *Enhancing Human Performance: Issues, Theories, and Techniques* (National Academy
  Press, Washington 1988) das Parapsychologie-Kapitel von **James Alcock** enthält und die
  REG-Forschung — PEAR eingeschlossen — als nicht überzeugend bewertete.
  *(Genaue Fundstelle im NRC-Bericht vor Verwendung im Video verifizieren.)*

### 4.3 Optional Stopping und fehlende Vorabregistrierung

**Was PEAR selbst dazu sagt** — Jahn & Dunne 2005, *PEAR Proposition*, S. 211: Ergebnisse
nicht-prolifischer Operatoren würden gepoolt,

> „… while guarding both procedurally and analytically against optional stopping artifacts that
> could prejudice the smallest datasets."

Und 1997 (JSE 11(3), Abschnitt II): das Design schließe
„any fouled data or any possible means of favorable data selection" aus.

**Der belegbare Gegenbefund liegt weniger beim Optional Stopping im engen Sinn als bei der
Vorabfestlegung der Auswertung.** Das PortREG-Paper räumt für die von ihm selbst hervorgehobenen
Strukturbefunde ein (S. 542):

> „While it is difficult to establish a Bonferroni-type correction factor for this sort of
> retrospective reexamination of an extant database …"

Fünf Jahre später beschreiben Jahn & Dunne dieselben Analysen als vorab geplant
(*PEAR Proposition* 2005, S. 220):

> „However, **pre-planned analyses** of a number of secondary parameters carried in this study
> revealed a number of interior structural anomalies unexpected by chance."

Diese Diskrepanz zwischen den beiden eigenen Darstellungen ist dokumentiert und lässt sich im
Video als Gegenüberstellung der beiden Zitate zeigen.
*Fairness-Hinweis: Ein Teil der Strukturanalysen war im Konsortialplan tatsächlich vorgesehen —
das Abstract von 2000 nennt „data also were collected on a number of secondary correlates".
Strittig ist nicht die Erhebung der Sekundärdaten, sondern ob die konkreten Auswertungs- und
Aggregationsentscheidungen vorab festgelegt waren.*

**Das PortREG-Design ist demgegenüber der positive Kontrast:** Dort war das Primärkriterium
vorab schriftlich vereinbart („The agreed upon primary criterion …"), und genau dieses Kriterium
scheiterte. Die frühere Benchmark-Datenbank wuchs dagegen über zwölf Jahre ohne einen solchen
vorab fixierten Endpunkt.

### 4.4 BELEGT — Datenauswahl im Nachhinein

PortREG-Paper 2000, S. 541:

> „Indeed, the breakdown by secondary parameter cells in Table C.7 indicates that data generated
> solely in the most conducive secondary conditions had effect sizes comparable to those seen in
> the prior PEAR experiments."

Das ist eine nachträgliche Auswahl derjenigen Zellen, die funktioniert haben — im Paper selbst
so ausgewiesen.

Ebenso das „Epochen"-Argument (S. 542): Die frühere PEAR-Datenbank wird nachträglich in drei
gleich lange Abschnitte geteilt („strong performance over the first, chance performance over the
second, and strong performance over the last"), um die gescheiterte Replikation als normale
Schwankung zu deuten. Die Autoren räumen dazu selbst ein, dass ein Bonferroni-Korrekturfaktor für
„this sort of retrospective reexamination" schwer zu bestimmen sei.

### 4.5 BELEGT — Kontrolle der Zufallsquelle: was dagegenspricht

Aus dem PortREG-Paper, Appendix I (S. 546 f.):

> „In general, the consistency of the data and the deviations of parameter estimates are in
> accord with theoretical expectations for independent random bits having binary probability of
> precisely .5, and hence these calibrations confirm the nominal statistical distribution of the
> overall data."

Kalibrierungsumfang dort: GARP und PEAR je über 1 Mio. Trials, FAMMI über 850.000; geprüft wurden
Mittelwert, Standardabweichung, Schiefe, Kurtosis, χ²-Bins, Runs, Arcus-Sinus-Verteilung und zwei
Autokorrelationsfunktionen. Kalibrier-Z-Werte (Tabelle 00): −0,1175 / 0,0253 / −0,0305.

**Wichtig für die Fairness der Folge:** Der pauschale Vorwurf „das Gerät war fehlerhaft" lässt
sich mit den PortREG-Kalibrierdaten nicht stützen. Jeffers' Einwand ist ein anderer und feinerer:
nicht die *unbeaufsichtigten Kalibrierläufe* seien auffällig, sondern die **Baseline-Läufe mit
Mensch davor** — und PEAR habe Kalibrierung und Baseline nicht durchgängig paarweise erhoben.

### 4.6 Weitere Kritiker, Namen und Fundstellen

- **James Alcock**, York University, Toronto: Parapsychologie-Kapitel im NRC-Bericht *Enhancing
  Human Performance* (National Academy Press, 1988); Mitherausgeber von *Psi Wars* (2003).
- **Robert L. Park**, University of Maryland / American Physical Society: fordert
  Doppelblind-Designs und Mikrowaagen-Tests gegen Versuchsleiter-Bias; PEAR sei darauf nicht
  eingegangen. Fundstelle: Park, R. (2000): *Voodoo Science: The Road from Foolishness to Fraud.*
  Oxford University Press.
  *Diesen Punkt habe ich über https://www.skepdic.com/pear.html (Meinungsseite) —
  Primärstelle bei Park vor Verwendung verifizieren.*
- **C. E. M. Hansel**, Psychologe, University of Wales: bewertete Jahns frühe
  Psychokinese-Experimente und bemängelte fehlende zufriedenstellende Kontrollen, fehlende
  unabhängige Replikation und zu knappe Berichte.
  Fundstelle: Hansel, C. E. M. (1989): *The Search for Psychic Power: ESP and Parapsychology
  Revisited.* Buffalo, NY: Prometheus Books.
  *Diesen Punkt habe ich referiert über die Psi Encyclopedia (SPR) — also über die Gegenseite.
  Kapitel und Seite am Buch verifizieren.*
- **James Alcock** wird in der Psi Encyclopedia mit dem Vorwurf „poor controls and documentation
  with the possibility of fraud, data selection and optional stopping" zitiert; derselbe Artikel
  hält dagegen, Alcock habe „provided no documentation for any of these suspicions".
  Das ist die einzige mir aufgefundene Fundstelle, in der der Vorwurf *optional stopping*
  ausdrücklich gegen PEAR erhoben wird — und sie stammt aus der Darstellung der Gegenseite.
  **Für das Video heißt das: „Optional Stopping" als konkreten, belegten Vorwurf gegen PEAR kann
  ich nicht sauber belegen. Der belegbare Nachbarvorwurf ist die nachträgliche Auswertung
  (4.3/4.4).**
- **York Dobyns** (PEAR) antwortet auf den Kalibrierungs-Einwand in:
  Dobyns, Y. (2000): *Overview of several theoretical models on PEAR data.*
  Journal of Scientific Exploration 14(2), 163–194.

---

## 5. Die Gegenrede — Jahn und Dunne in eigenen Worten

*(Belege: Jahn, R. G. & Dunne, B. J. (2005): The PEAR Proposition. Journal of Scientific
Exploration 19(2), 195–246, PDF: https://www.pear-lab.com/pdfs/2005-pear-proposition.pdf —
sowie das PortREG-Paper von 2000.)*

**Zur Irreproduzierbarkeit als angeblichem Wesensmerkmal** (PEAR Proposition, S. 219):

> „These capricious 'hide-and-seek' characteristics of the effects have provided bountiful fodder
> for superficial skeptics who gleefully hail them as evidence of incompetent experimentation or
> delusional data interpretation. **More profound contemplation, however, suggests that this
> apparent irreproducibility may be an intrinsic feature of the phenomena, and a potentially most
> valuable, if poorly understood, indicator of their fundamental nature.**"

**Zum Replikationsbegriff** (PortREG 2000, S. 543):

> „To expect that these hypercomplex systems will submit to classical expectations of causality,
> determinism, and replicability may be overly presumptive."

**Zur Freiburg-Gießen-Replikation** (PEAR Proposition, S. 220 f.):

> „To summarize, whereas overall HI − LO mean separations, which were the primary criterion of
> this replication effort, proceeded in the intended direction at all three laboratories, the size
> of these deviations failed by an order of magnitude to attain that of our own prior experiments,
> or even to achieve a persuasive level of statistical significance. However, pre-planned analyses
> of a number of secondary parameters carried in this study revealed a number of interior
> structural anomalies unexpected by chance. Utilizing an ingenious Monte Carlo simulation
> technique that precluded any multiple testing artifacts, our analytical specialist, York Dobyns,
> was able to demonstrate that this assortment of departures in the individual and collective
> datasets from the null hypothesis expectations was itself highly significant. **It was as if the
> simple displacements of the mean that had characterized the original benchmark experiments had
> been partially transformed into a number of more subtle anomalous fragments in the new data.**"

**Zur „Superstar"-Kritik** (PEAR Proposition, S. 211 f.), Kernsatz:

> „Thus, such data assert that the collective anomaly is not primarily driven by distinguishable
> 'superstars,' but rather by a collective array of inextricably small individual effects,
> achieved over many large datasets."

**Zum Ton der Kritiker** (PEAR Proposition, S. 204):

> „More despicable have been a few sanctimonious attempts by self-styled critics to discredit the
> work among their audiences of students, administrators, or less technically cognizant
> colleagues."

**Zum Decline-Effekt** (PEAR Proposition, S. 219):

> „In short, there is indeed a decline effect, but it manifests only as an initial phase of a more
> complex pattern of performance evolution."

**Zur epistemologischen Verteidigung:** Jahn/Dunne verweisen auf die gemeinsame Arbeit mit dem
Physiker **Harald Atmanspacher**, *Problems of Reproducibility in Complex Mind–Matter Systems*
(Journal of Scientific Exploration 18(2), 2004, 243–270), die vorschlägt, Mind-Matter-Interaktion
als komplexes System zu behandeln, für das „standard first-order approaches are both
epistemologically and methodologically inadequate".

**Programmatisch** — die grundsätzlichste Form der Gegenrede:
Jahn, R. G. & Dunne, B. J. (1997): *Science of the Subjective.* Journal of Scientific Exploration
11(2), 201–224. PDF: https://www.pear-lab.com/pdfs/1997-science-subjective.pdf
Kernforderung: subjektive Faktoren methodisch in die Naturwissenschaft aufzunehmen, statt sie
auszuschließen.

---

## 6. Wie die Fachwelt heute darauf blickt

### 6.1 BELEGT — die zentrale Meta-Analyse: Bösch, Steinkamp & Boller 2006

**Zitation:** Bösch, Holger; Steinkamp, Fiona; Boller, Emil (2006):
*Examining Psychokinesis: The Interaction of Human Intention With Random Number Generators —
A Meta-Analysis.* **Psychological Bulletin 132(4), S. 497–523.**
DOI: 10.1037/0033-2909.132.4.497
PubMed: https://pubmed.ncbi.nlm.nih.gov/16822162/
(Crossref weist als Förderer u. a. das *Institute for Border Areas of Psychology and Mental
Hygiene* — also das IGPP Freiburg — und das Samueli Institute aus. 252 Literaturangaben.)

**Bemerkenswert für die Folge:** Holger Bösch und Emil Boller sind zwei der Freiburger
Co-Autoren des PortREG-Replikationspapiers von 2000. Dieselben Leute, die die Replikation mit
PEAR durchgeführt haben, legen sechs Jahre später die bislang umfassendste Meta-Analyse des
gesamten Feldes vor.

**Abstract, wörtlich:**

> „Séance-room and other large-scale psychokinetic phenomena have fascinated humankind for
> decades. Experimental research has reduced these phenomena to attempts to influence (a) the
> fall of dice and, later, (b) the output of random number generators (RNGs). **The meta-analysis
> combined 380 studies that assessed whether RNG output correlated with human intention and found
> a significant but very small overall effect size. The study effect sizes were strongly and
> inversely related to sample size and were extremely heterogeneous. A Monte Carlo simulation
> revealed that the small effect size, the relation between sample size and effect size, and the
> extreme effect size heterogeneity found could in principle be a result of publication bias.**"

Das Kernargument in einem Satz: Je größer die Studie, desto kleiner der Effekt — genau das
Muster, das man erwartet, wenn kleine erfolgreiche Studien überproportional veröffentlicht
werden. Die Autoren ziehen daraus den Schluss, Psychokinese sei **„not proven"** (so referiert
in der Antwort von Radin et al., s. u.).

### 6.2 BELEGT — die Debatte im selben Heft des Psychological Bulletin

Das Heft enthält zwei Kommentare und eine Erwiderung — das ist der Ort, an dem beide Seiten
2006 in einem A-Journal direkt aufeinandertreffen:

**(a) Pro-Seite:** Radin, D.; Nelson, R.; Dobyns, Y.; Houtkooper, J. (2006):
*Reexamining psychokinesis: Comment on Bösch, Steinkamp, and Boller (2006).*
Psychological Bulletin 132(4), 529–532. DOI: 10.1037/0033-2909.132.4.529
(Roger Nelson und York Dobyns waren PEAR-Mitarbeiter, Houtkooper Gießener Co-Autor der
Replikation.) Abstract, wörtlich:

> „The authors agree with Bösch et al. that existing studies provide statistical evidence for
> psychokinesis, that the evidence is generally of high methodological quality, and that effect
> sizes are distributed heterogeneously. Bösch et al. postulated the heterogeneity is attributable
> to selective reporting and thus that psychokinesis is 'not proven.' However, Bösch et al.
> assumed that effect size is entirely independent of sample size. For these experiments, this
> assumption is incorrect; it also guarantees heterogeneity. **The authors maintain that selective
> reporting is an implausible explanation for the observed data and hence that these studies
> provide evidence for a genuine psychokinetic effect.**"

**(b) Methodiker-Seite:** Wilson, D. B. & Shadish, W. R. (2006):
*On blowing trumpets to the tulips: To prove or not to prove the null hypothesis — Comment on
Bösch, Steinkamp, and Boller (2006).* Psychological Bulletin 132(4), 524–528.
DOI: 10.1037/0033-2909.132.4.524
(David B. Wilson und William R. Shadish sind ausgewiesene Meta-Analyse-Methodiker ohne Bindung
an die Parapsychologie — das macht diesen Kommentar für die Folge besonders wertvoll.)
Abstract, wörtlich:

> „The authors argue that, for both methodological and philosophical reasons, **it is nearly
> impossible to draw any conclusions from this body of research.** The authors do not agree that
> any significant effect at all, no matter how small, is fundamentally important (Bösch et al.,
> 2006, p. 517), and they suggest that psychokinesis researchers focus either on producing larger
> effects or on specifying the conditions under which they would be willing to accept the null
> hypothesis."

**(c) Erwiderung:** Bösch, H.; Steinkamp, F.; Boller, E. (2006):
*In the eye of the beholder: Reply to Wilson and Shadish (2006) and Radin, Nelson, Dobyns, and
Houtkooper (2006).* Psychological Bulletin 132(4), 533–537.
DOI: 10.1037/0033-2909.132.4.533

### 6.3 BELEGT — spätere Übersichtsarbeiten

- **Cardeña, Etzel (2018):** *The experimental evidence for parapsychological phenomena: A review.*
  **American Psychologist 73(5), 663–677.** DOI: 10.1037/amp0000236
  Pro-Seite, in einem Mainstream-Journal. Abstract wörtlich:
  > „The evidence provides cumulative support for the reality of psi, which cannot be readily
  > explained away by the quality of the studies, fraud, selective reporting, experimental or
  > analytical incompetence, or other frequent criticisms."

- **Reber, Arthur S. & Alcock, James E. (2020):** *Searching for the impossible: Parapsychology's
  elusive quest.* **American Psychologist 75(3), 391–399.** DOI: 10.1037/amp0000486
  Die direkte Erwiderung darauf, im selben Journal. Abstract wörtlich:
  > „Our position is straightforward. **Claims made by parapsychologists cannot be true.** The
  > effects reported can have no ontological status; the data have no existential value. … In the
  > classic English adynaton, 'pigs cannot fly.' Hence, data that suggest that they can are
  > necessarily flawed and result from weak methodology or improper data analyses or are Type I
  > errors."
  *Hinweis zur Verwendung: Reber & Alcock argumentieren ausdrücklich a priori („cannot be true"),
  nicht empirisch. Wenn die Folge beide Seiten fair zeigen will, sollte das kenntlich gemacht
  werden — dieses Zitat ist keine Auswertung der PEAR-Daten, sondern eine Grundsatzposition.*

- **Pallikari, Fotini (2015):** *Investigating the nature of intangible brain-machine interaction.*
  Preprint, arXiv:1507.02219 — https://arxiv.org/pdf/1507.02219
  Reanalyse derselben 380-Studien-Datenbank aus Bösch et al. 2006 (die Daten wurden ihr laut
  Danksagung von Co-Autorin Fiona Steinkamp zur Verfügung gestellt). Abstract, wörtlich:
  > „It is shown that there exists no validation of the hypothesis of brain-machine interaction
  > precisely in absence of interface devices. It is concluded that any evidence in favour of the
  > alleged intangible brain-machine effects, must have resulted from unintended errors during
  > data collection and treatment, known as 'the experimenter expectancy effect'."
  Zum Trichterdiagramm der Datenbank schreibt sie:
  > „the IMMI database of the 380 studies included in the meta-analysis is clearly marked by
  > publication bias"
  *Status: Preprint auf arXiv, nicht in dieser Form peer-reviewed. Pallikari ist Physikerin an
  der Universität Athen und hat selbst in parapsychologischen Journals publiziert — also keine
  außenstehende Skeptikerin. Im Video als „Reanalyse der Meta-Analyse-Daten" bezeichnen, nicht
  als „Fachartikel".*

- **Pallikari, Fotini (2023):** *Understanding the Nature of Psychokinesis.*
  **Journal of Anomalistics / Zeitschrift für Anomalistik 23, 103–131.**
  DOI: 10.23793/zfa.2023.103 — die ausgearbeitete, in einem Fachjournal des Feldes
  veröffentlichte Fassung derselben Argumentation.

### 6.4 BELEGT — wie die Pro-Seite selbst die Replikation heute darstellt

Der Artikel zu PEAR in der *Psi Encyclopedia* der Society for Psychical Research wurde von
**Roger D. Nelson** geschrieben — also von einem PEAR-Mitarbeiter und Mitautor beider
Schlüsselpapiere:
https://psi-encyclopedia.spr.ac.uk/articles/princeton-engineering-anomalies-research-pear/
Dort wird das PortREG-Experiment als „a strict replication in the sense that PEAR software and
REGs were used" beschrieben, mit „positive but non-significant trends at all three labs" trotz
„suitable conditions and sufficient statistical power". Zur Kritik insgesamt heißt es dort,
„most of the critical views expressed about PEAR tend to be simple expressions of bias and an
unquestioned belief in the standard models of science".
Zu Stanley Jeffers wird angeführt, er habe sein optisches Interferenz-Experiment mit Nullresultat
später dem PEAR-Labor überlassen, wo es „a nominally significant effect" gezeigt habe.
**Quellenhinweis: Das ist eine Enzyklopädie der SPR, verfasst von einem Beteiligten — als
Position der Pro-Seite kennzeichnen, nicht als neutrale Fachdarstellung.** Der Artikel behandelt
den Operator-10-Einwand nicht und erwähnt die Bösch-Meta-Analyse nicht.

### 6.5 Zusammenfassung des heutigen Standes

- Es gibt **keine** unabhängige Übersichtsarbeit außerhalb der Parapsychologie, die PEARs
  Primärbefund als etabliert bewertet.
- Die umfassendste Meta-Analyse (Bösch et al. 2006, Psychological Bulletin, 380 Studien) findet
  einen signifikanten, aber extrem kleinen Gesamteffekt und erklärt ihn mit Publikationsbias.
- Die Kommentatoren aus der Meta-Analyse-Methodik (Wilson & Shadish 2006) halten das Feld für
  eine Datenlage, aus der sich „nearly impossible" Schlüsse ziehen lassen.
- Die Pro-Seite (Radin/Nelson/Dobyns/Houtkooper 2006; Cardeña 2018) bestreitet den
  Publikationsbias-Schluss, nicht aber die Kleinheit des Effekts.
- Die Debatte in *American Psychologist* 2018/2020 zeigt: Der Streit läuft heute weniger über die
  PEAR-Zahlen als über die Frage, welche Beweislast ein solcher Effekt zu tragen hätte.

---

## 7. Wo die Kritik am stärksten und wo am schwächsten steht

### Die drei stärksten Punkte

1. **Die vorab festgelegte Replikation ist gescheitert — und PEAR hat das selbst so ausgerechnet.**
   Das PortREG-Konsortium hatte das Erfolgskriterium schriftlich vereinbart, brachte 750 Serien
   und 227 Operatoren auf, und die PEAR-Vorhersage wurde mit **Z = −2,87** zurückgewiesen; die
   Zahl steht auf S. 516 des Papers, das Jahn und Dunne mitverfasst haben.

2. **Die nachträgliche Umdeutung ist im Papier selbst als nachträglich gekennzeichnet.**
   Die „strukturellen Anomalien", auf die das Ergebnis umgedeutet wird, waren nicht das vorab
   vereinbarte Kriterium — das Paper räumt für einen zentralen Teil ein, es handle sich um
   „retrospective reexamination of an extant database", während dieselben Analysen 2005 als
   „pre-planned" beschrieben werden.

3. **Der Baseline-Befund untergräbt die Vergleichsbasis.**
   Jeffers' Einwand betrifft nicht ein Nebenergebnis, sondern die Nulllinie selbst: Wenn die
   Baseline-Daten nach PEARs eigenem p-Kriterium nichtzufällig sind (in Tabelle 0 des
   PortREG-Papers steht BL mit Z = 1,71 statt 0), dann steht die Signifikanz von HI und LO auf
   einem Referenzpunkt, der selbst nicht sauber ist.

### Die drei schwächsten Punkte

1. **„Das Gerät war fehlerhaft."**
   Die begleitenden Kalibrierläufe des PortREG-Experiments umfassen über eine Million Trials pro
   Labor und liegen mit Z-Werten um 0,03 bis 0,12 exakt auf Erwartung, geprüft über Mittelwert,
   Varianz, Schiefe, Kurtosis, Runs und Autokorrelation — ein simpler Gerätefehler ist damit
   nicht plausibel zu machen.

2. **„Operator 10 war eine Mitarbeiterin, also war es Betrug."**
   Belegt sind nur McCrones Zahlen (15 % der Trials, halber Überschuss) und Jahns Eingeständnis
   eines großen Anteils; die Zugehörigkeit zum Labor steht als „believed to be", die Identität
   ist nie bestätigt worden, und Jahns Gegenargument (dass vier bis fünf Operatoren größere
   Effektstärken bei kleineren Datenmengen zeigten) ist unwiderlegt.

3. **„Niemand hat je etwas Ähnliches gefunden."**
   Die Bösch-Meta-Analyse findet über 380 Studien hinweg einen statistisch signifikanten
   Gesamteffekt; strittig ist dessen *Erklärung* (Publikationsbias), nicht seine Existenz in der
   Datenbank — wer im Video sagt, es sei „nie etwas gefunden worden", verkürzt die Fachlage
   falsch.

---

## Quellenliste (alle im Text verwendeten Fundstellen)

**Primärquellen PEAR / Konsortium**
- Jahn, R. G. et al. (2000): Mind/Machine Interaction Consortium: PortREG Replication
  Experiments. JSE 14(4), 499–555.
  http://icrl.org/wp-content/uploads/2020/02/2000-mmi-consortium-portreg-replication.pdf
- Jahn, R. G.; Dunne, B. J.; Nelson, R. D.; Dobyns, Y. H.; Bradish, G. J. (1997): Correlations of
  Random Binary Sequences with Pre-Stated Operator Intention. JSE 11(3), 345–367.
  https://www.pear-lab.com/pdfs/1997-correlations-random-binary-sequences-12-year-review.pdf
- Jahn, R. G. & Dunne, B. J. (2005): The PEAR Proposition. JSE 19(2), 195–246.
  https://www.pear-lab.com/pdfs/2005-pear-proposition.pdf
- Jahn, R. G. & Dunne, B. J. (1997): Science of the Subjective. JSE 11(2), 201–224.
  https://www.pear-lab.com/pdfs/1997-science-subjective.pdf
- Jahn, R. G. & Dunne, B. J. (1987): Margins of Reality. New York: Harcourt Brace Jovanovich.
- Dobyns, Y. (2000): Overview of several theoretical models on PEAR data. JSE 14(2), 163–194.
- Publikationsverzeichnis PEAR: https://www.pear-lab.com/publications

**Kritik**
- McCrone, J. (1994): Psychic powers: What are the odds? New Scientist, 26.11.1994, 34–38.
  https://archive.org/details/cia-readingroom-document-cia-rdp96-00789r003200250001-9
- Palmer, J. (1985): An Evaluative Report on the Current Status of Parapsychology. U.S. Army
  Research Institute. https://apps.dtic.mil/sti/tr/pdf/ADA169486.pdf
- Jeffers, S. (2006): The PEAR Proposition: Fact or Fallacy? Skeptical Inquirer 30(3), 54–57.
  https://cdn.centerforinquiry.org/wp-content/uploads/sites/29/2006/05/22164608/p54.pdf
- Ibison, M. & Jeffers, S. (1998): A double slit experiment … JSE 12(4), 543–550.
- Jeffers, S. (2003): Physics and claims for anomalous effects due to consciousness. In: Psi Wars,
  Imprint Academic, 135–152.
- Hyman, R. (1989): The Elusive Quarry. Prometheus Books (bes. S. 152).
- Alcock, J. (1988), in: Enhancing Human Performance, National Academy Press.
- Hansel, C. E. M. (1989): The Search for Psychic Power. Prometheus Books.
- Park, R. (2000): Voodoo Science. Oxford University Press.

**Meta-Analysen und Übersichten**
- Bösch, H.; Steinkamp, F.; Boller, E. (2006): Psychological Bulletin 132(4), 497–523.
  DOI 10.1037/0033-2909.132.4.497
- Wilson, D. B. & Shadish, W. R. (2006): Psychological Bulletin 132(4), 524–528.
  DOI 10.1037/0033-2909.132.4.524
- Radin, D.; Nelson, R.; Dobyns, Y.; Houtkooper, J. (2006): Psychological Bulletin 132(4),
  529–532. DOI 10.1037/0033-2909.132.4.529
- Bösch, H.; Steinkamp, F.; Boller, E. (2006): In the eye of the beholder. Psychological Bulletin
  132(4), 533–537. DOI 10.1037/0033-2909.132.4.533
- Cardeña, E. (2018): American Psychologist 73(5), 663–677. DOI 10.1037/amp0000236
- Reber, A. S. & Alcock, J. E. (2020): American Psychologist 75(3), 391–399. DOI 10.1037/amp0000486
- Pallikari, F. (2015): arXiv:1507.02219 (Preprint)
- Pallikari, F. (2023): Journal of Anomalistics 23, 103–131. DOI 10.23793/zfa.2023.103

**Sekundär- und Meinungsquellen (im Video als solche kennzeichnen)**
- The Skeptic's Dictionary, „Princeton Engineering Anomalies Research":
  https://www.skepdic.com/pear.html — Skeptikerseite; hier nur als Fundstelle für die
  Hyman- und Park-Zitate benutzt, beide vor Verwendung an der Primärquelle prüfen.
- Psi Encyclopedia (SPR), Artikel „Princeton Engineering Anomalies Research (PEAR) Laboratory",
  verfasst von Roger D. Nelson:
  https://psi-encyclopedia.spr.ac.uk/articles/princeton-engineering-anomalies-research-pear/
  — Position der Pro-Seite, von einem Beteiligten verfasst.

**Noch zu verifizieren, bevor es im Video als Tatsache gesagt wird**
1. Palmer 1985: exakte Seite und Wortlaut zur Operator-10-Feststellung im DTIC-PDF.
2. Hyman 1989, S. 152: Zitat am Buch prüfen (bisher nur sekundär über skepdic).
3. Park 2000: Fundstelle im Buch für die Doppelblind-/Mikrowaagen-Forderung.
4. NRC-Bericht 1988: genaue Fundstelle des PEAR-Abschnitts im Alcock-Kapitel.
