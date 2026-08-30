# EP09_EN — Source Lock and Editorial Research

Reviewed: 2026-08-30
Status: SOURCE LOCKED for voice; media acquisition remains `PENDING_CODEX`

The canonical English script remains a retention-first adaptation. This file locks the factual statements that carry production risk and records the exact wording changes made after source review.

## Claim-to-source lock

| ID | Script claim / beat | Best source | Exact location | Lock decision |
|---|---|---|---|---|
| C01 | Tuatara and many lizards possess a parietal or “third” eye derived from the pineal complex; it contains a simplified retina with photoreceptor cells. | Romero RD, de Souza FSJ. *Evolution of Pineal Nonvisual Opsins in Lizards and the Tuatara and Identification of Lepidopsin: A New Opsin Gene*. Genome Biology and Evolution 17(5), 2025. https://pmc.ncbi.nlm.nih.gov/articles/PMC12043008/ | Abstract and Significance; DOI 10.1093/gbe/evaf058 | LOCKED. This supports the opening image and the use of “third eye”. It does **not** justify assigning one detailed behavioral function to every species. |
| C02 | In most non-mammalian vertebrates the pineal organ is directly photosensory, whereas the mammalian pineal is a non-sensory neuroendocrine organ under photoperiod control. | Ekström P, Meissl H. *Evolution of photosensory pineal organs in new light: the fate of neuroendocrine photoreceptors*. Phil Trans R Soc B 358, 2003. https://pmc.ncbi.nlm.nih.gov/articles/PMC1693265/ | Abstract; pp. 1679–1700; DOI 10.1098/rstb.2003.1303 | LOCKED with evolutionary boundary. The paper explicitly warns that a simple gradual transformation model is ambiguous; narration therefore stays at shared history / changed architecture rather than “the reptile eye became our pineal”. |
| C03 | Pinealocytes and retinal photoreceptors show deep evolutionary, molecular and developmental similarities. | Rath MF et al. *Homeobox genes in the rodent pineal gland: roles in development and phenotype maintenance*. Cell Tissue Res, 2013. https://pmc.ncbi.nlm.nih.gov/articles/PMC3570627/ | §3, “Evolution of the mammalian pinealocyte: pineal and retinal similarities” | LOCKED. Use as evidence for relationship, not for a literal vestigial human eye. |
| C04 | Human light-dark information reaches the pineal through retinal/circadian/neural pathways; melanopsin-containing retinal ganglion cells contribute to non-image-forming light responses. | Arendt J, Aulinas A. *Physiology of the Pineal Gland and Melatonin*. Endotext, updated 2022-10-30. https://www.ncbi.nlm.nih.gov/books/NBK550972/ | “Pineal Physiology” → “Main Function of the Pineal Gland”; “Control of Melatonin Synthesis: A Darkness Hormone” | LOCKED. Supports retina → SCN → hypothalamic/autonomic relay → pineal and nighttime melatonin. |
| C05 | The mammalian pathway includes RHT/retina → SCN → PVN → upper thoracic intermediolateral column → superior cervical ganglion → pineal. | Moore RY. *Neural control of the pineal gland*. Behav Brain Res 73, 1996. https://pubmed.ncbi.nlm.nih.gov/8788489/ | Abstract; pp. 125–130; DOI 10.1016/0166-4328(96)00083-6 | LOCKED. This is the clean pathway reference for animation and fact-checking. |
| C06 | Human melatonin is predominantly a darkness/night signal and circulating levels normally rise at biological night. | Arendt & Aulinas, Endotext. https://www.ncbi.nlm.nih.gov/books/NBK550972/ | Abstract; “Main Function”; “Melatonin Synthesis”; “Control of Melatonin Synthesis: A Darkness Hormone” | LOCKED. Narration deliberately avoids describing melatonin as a knockout/sedative chemical. |
| C07 | Evening reading on a light-emitting e-reader can suppress melatonin, delay circadian phase, increase sleep latency and reduce next-morning alertness under controlled conditions. | Chang A-M, Aeschbach D, Duffy JF, Czeisler CA. *Evening use of light-emitting eReaders negatively affects sleep, circadian timing, and next-morning alertness*. PNAS 112(4), 2015. https://pmc.ncbi.nlm.nih.gov/articles/PMC4313820/ | Results and Materials & Methods; pp. 1232–1237; especially study protocol and Fig. 2/3 results. Twelve adults; randomized crossover; ~4 h before bed for five evenings; device 30–50 photopic lux at eye. | LOCKED to the study conditions. Reported outcomes include 55.12 ± 20.12% evening melatonin suppression, >1.5 h later DLMO and ~10 min longer sleep latency. Do not generalize these magnitudes to every phone/screen exposure. |
| C08 | Descartes gave the pineal gland a central role and called it the principal seat of the soul. | Stanford Encyclopedia of Philosophy, *Descartes and the Pineal Gland*. https://plato.stanford.edu/entries/pineal-gland/ | §2.2; primary reference: Descartes letter of 29 Jan 1640, AT III:19–20 | LOCKED for the episode cliffhanger. Full primary-document lock belongs to EP10. |
| C09 | Elisabeth challenged Descartes to explain how an immaterial soul could determine bodily motion. | Descartes, *Œuvres*, ed. Adam & Tannery, vol. III (1899), Elisabeth to Descartes, 6/16 May 1643. https://fr.wikisource.org/wiki/Correspondance_avec_%C3%89lisabeth/%C3%89lisabeth_%C3%A0_Descartes_-_La_Haye%2C_16_mai_1643 | pp. 660–662 | LOCKED as the historical bridge. Use the public-domain facsimile/edition, not a copyrighted modern translation, for viewer-facing document imagery. |

## Applied script changes

Only three evidence-driven edits were made to `01_SCRIPT/VOICE_SCRIPT_EN.txt`:

1. **Species-function overreach removed.**  
   Old: `It reads brightness, dusk, the movement of the sun, and the rhythm of day and night.`  
   New: `It is a simple photoreceptive organ — closer to a light sensor than to the camera-like eyes beside it.`  
   Reason: the anatomy/light sensitivity is secure; a single detailed behavioral-function list is not equally secure for tuatara and all referenced lizards.

2. **Mammalian transition made anatomically cleaner.**  
   Old: `The pineal gland lost the direct light sensitivity found in other vertebrate arrangements.`  
   New: `In mammals, the pineal gland no longer receives environmental light directly.`  
   Reason: keeps the intended image while avoiding a simplistic linear evolutionary transformation claim.

3. **E-reader outcome made faithful to the experiment.**  
   Old: `Participants became sleepy later and were less alert the following morning.`  
   New: `They felt less sleepy before bed, took longer to fall asleep, and were less alert the following morning.`  
   Reason: this matches the measured evening sleepiness, sleep latency and next-morning alertness outcomes.

## Rights boundary for source documents

Scientific facts and media rights are separate questions. A paper being freely readable does **not** automatically make every figure freely reusable. The Romero 2025 paper is explicitly CC BY 4.0. The Chang PNAS article is a primary source, but the production package must not assume broad Creative Commons rights for its figures; prefer a source-identifying document shot where legally appropriate or recreate a clean data graphic from the reported values with citation. Public-domain historical scans and Commons files are separately logged in `ORIGINAL_ASSET_MANIFEST.csv`.

## Voice-lock verdict

The script is factually ready for native-English aloud QA. No further science rewrite is recommended before voice generation unless the asset acquisition step reveals a provenance conflict that changes a specific line.
