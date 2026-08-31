# EP09_EN — Asset URL Verification and Use Register

Reviewed: 2026-08-30
Episode: `EP09_PINEAL_01 — The Eye Within`
Branch: `production/ep09-pineal-01-source-lock`

This document records the human-readable verification pass for the production asset pool. The machine-readable canonical register is `ORIGINAL_ASSET_MANIFEST.csv`.

## Verification standard

A link is treated as production-usable only when the verification pass confirms the real content behind the URL, not merely that the domain or page exists. For each asset the pass checks, where available: exact subject/title, creator or institution, date, image/document dimensions or file type, rights/license statement, and whether the content actually supports the intended narration beat.

Verification states used in the CSV:

- `VERIFIED_DIRECT` — exact URL/content and relevant rights metadata were directly confirmed.
- `REPLACED_VERIFIED` — an earlier weak, blocked, retired or ambiguous URL was replaced with a better verified endpoint.
- `VERIFIED_REFERENCE` — correct research/identity source, not a production-ready reusable image.
- `VERIFIED_RIGHTS_HOLD` — correct image/source, but permission is required.
- `VERIFIED_INDEXED_BLOCKED` — correct source was independently indexed, but automated page access was blocked; do not rely on it as the production binary.
- `VERIFIED_COLLECTION` — the collection/category is real, but each chosen file still requires individual license lock.
- `VERIFIED_LOW_RES` — correct and rights-usable, but resolution is weak.
- `VERIFIED_WITH_RIGHTS_NOTE` — content is correct and historically old, but jurisdiction/unknown-author caveat should remain in metadata.
- `HOLD_LICENSE_REVIEW` — source/content is correct but a license inconsistency remains unresolved.

## Major corrections made during verification

1. **Dendy 1899** — the prior BHL deep-link is useful for humans but blocked automated verification. The production manifest now points to the verified full 1899 *Quarterly Journal of Microscopical Science* PDF on Wikimedia, which contains Dendy's paper and Plates XI–XIII.
2. **Princess Elisabeth portrait** — replaced the previous ambiguous/NPG-derived portrait route with the verified Rijksmuseum portrait of Elisabeth of the Palatinate, the philosopher who corresponded with Descartes.
3. **Stanford Encyclopedia** — the former current `pineal-gland` entry is retired. The register now points to the stable Summer 2026 archive of *Descartes and the Pineal Gland*.
4. **Charles Czeisler** — the Harvard profile remains a research reference, but a new 2018 U.S. Navy photograph gives production a high-resolution public-domain researcher image.
5. **Pineal/third-eye historical evidence** — added a verified 1887–88 *Popular Science Monthly* illustration specifically titled *Pineal eye in Hatteria*, with retina, nerve, blood vessel and elongated rods/cones labeled. This is more directly useful to the opening than generic lizard anatomy alone.

## Verified production pool by story function

### 1. Living tuatara — opening biological hook

- **A03 — Sphenodon punctatus (5), TimVickers, 2008**  
  URL: https://commons.wikimedia.org/wiki/File:Sphenodon_punctatus_(5).jpg  
  Verified content: living tuatara photograph, 4224×2376. Public-domain dedication.  
  Use: primary 16:9-friendly hero image under `There are animals alive today with a third eye.`
- **A04 — Sphenodon punctatus**  
  URL: https://commons.wikimedia.org/wiki/File:Sphenodon_punctatus.jpg  
  Verified content: 2232×2052 public-domain tuatara image.  
  Use: alternate living-animal state; useful after a punch-in so the opening is not one repeatedly reframed photo.
- **A05 — Sphenodon punctatus (1)**  
  URL: https://commons.wikimedia.org/wiki/File:Sphenodon_punctatus_(1).jpg  
  Verified content: 2748×1944 public-domain image.  
  Use: second body angle / texture / morphology.
- **A06 — Sphenodon punctatus head**  
  URL: https://commons.wikimedia.org/wiki/File:Sphenodon_punctatus_head.jpg  
  Verified content: 2560×2020 public-domain head close-up.  
  Use: head detail before the historical anatomical proof; do **not** point to a random scale and call it the functional parietal eye.
- **A07/A08 — additional TimVickers tuatara states**  
  URLs: https://commons.wikimedia.org/wiki/File:Sphenodon_punctatus_(2).jpg and https://commons.wikimedia.org/wiki/File:Sphenodon_punctatus_(4).jpg  
  Verified content: 3040×2376 and 2778×1999, public domain.  
  Use: edit reserve and visual variety.

### 2. Direct parietal-eye / tuatara evidence

- **A58 — Pineal eye in Hatteria, 1887–88**  
  URL: https://commons.wikimedia.org/wiki/File:PSM_V33_D805_Pineal_eye_in_hatteria.jpg  
  Verified content: 1210×1581 historical scientific illustration specifically of the pineal eye in Hatteria/Sphenodon; labels include nerve, blood vessel, retina and elongated rods/cones. Public domain.  
  Use: one of the strongest opening evidence shots. Show full illustration, then guided macro crop on labeled anatomy.
- **A02/A14/A15/A16 — Arthur Dendy, 1899**  
  URL: https://upload.wikimedia.org/wikipedia/commons/4/4d/Quarterly_Journal_of_Microscopical_Science%2C_new_ser._vol.42_%281899%29%2C_London%2C_1899.pdf  
  Verified content: full 1899 journal volume containing *On the Development of the Parietal Eye and Adjacent Organs in Sphenodon punctatus* and Plates XI–XIII. Public domain.  
  Use: primary historical document reveal; show title/page context before plate crops. Ideal for `real biology, documented anatomy` rather than decorative old-paper texture.
- **A01 — Spencer, parietal eye of Anolis, 1886**  
  URL: https://commons.wikimedia.org/wiki/File:Spencer_(1886)_parietal_eye_Anolis.PNG  
  Verified content: 470×368 historical anatomy plate, public domain.  
  Use: comparative species evidence after Sphenodon; label Anolis.
- **A10 — Spencer, parietal eye of Varanus, 1886**  
  URL: https://commons.wikimedia.org/wiki/File:Spencer_(1886)_parietal_eye_Varanus.png  
  Verified content: 470×428 historical anatomy plate, public domain.  
  Use: second-species comparison; label Varanus.
- **A65 — Klinckowström, Iguana, 1894**  
  URL: https://commons.wikimedia.org/wiki/File:Klinckowstroem_(1894)_parietal_eye_of_Iguana.png  
  Verified content: 470×329 historical parietal-eye image, public domain.  
  Use: third-species comparison if the edit needs to show this is a broader vertebrate story rather than one strange New Zealand animal.
- **A66 — Pineal eye of Varanus, Popular Science Monthly**  
  URL: https://commons.wikimedia.org/wiki/File:PSM_V33_D806_Pineal_eye_of_varanus.jpg  
  Verified content: indexed historical Varanus pineal-eye illustration, approximately 1523×1802, public domain.  
  Use: companion image to A58; Codex should reopen exact file page at acquisition for final metadata.
- **A11 — Tilney & Warren, 1919 monograph**  
  URL: https://www.biodiversitylibrary.org/item/15619  
  Verified content: complete public-domain monograph with PDF/JPEG2000 download options and large comparative pineal/parietal plate pool.  
  Use: deep-history montage and source for additional non-duplicate plates when Dendy/Spencer alone are visually insufficient.
- **A59 — Hatteria museum wall plate**  
  URL: https://commons.wikimedia.org/wiki/File:MAC_TAV_0057_Tavola_parietale_Hatteria.jpg  
  Verified content: 5615×6739 historic comparative-anatomy plate from Sapienza's collection.  
  Rights: historically old/public-domain basis, but unknown-author jurisdiction caveat should remain in metadata.  
  Use: spectacular full-frame archival plate, especially for nervous/circulatory comparative anatomy; not direct proof of pineal function.

### 3. Modern evolutionary / zoological evidence

- **A09 — Romero & de Souza, 2025**  
  URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC12043008/  
  Verified content: *Evolution of Pineal Nonvisual Opsins in Lizards and the Tuatara and Identification of Lepidopsin*. Explicit CC BY 4.0.  
  Use: modern scientific identity card after historical plates; selected figures can be used with attribution if they support the point cleanly.

### 4. Human pineal anatomy and real tissue

- **A17 — Gray's Anatomy plate 719**  
  URL: https://commons.wikimedia.org/wiki/File:Gray719.png  
  Verified content: public-domain brain anatomy plate, 550×503.  
  Use: first human-location reveal, enough surrounding anatomy to prevent misleading scale.
- **A18 — Cancer Research UK pineal-position SVG**  
  URL: https://commons.wikimedia.org/wiki/File:Diagram_showing_the_position_of_the_pineal_gland_in_the_brain_CRUK_416.svg  
  Verified content: clean vector, CC BY-SA 4.0.  
  Use: modern orientation graphic; better than Gray when the edit needs immediate readability.
- **A19 — pineal and pituitary glands SVG**  
  URL: https://commons.wikimedia.org/wiki/File:Diagram_showing_the_pineal_and_pituitary_glands_CRUK_468.svg  
  Verified content: clean CC BY-SA 4.0 vector.  
  Use: secondary endocrine orientation only; do not imply the pituitary is part of the retina→SCN→pineal timing path.
- **A21 — human pineal H&E, low magnification**  
  URL: https://commons.wikimedia.org/wiki/File:Pineal_gland_-_low_mag.jpg  
  Verified content: normal human pineal histology, 2848×4272, CC BY-SA 3.0.  
  Use: strong reality check after mystical language — `this is actual tissue`.
- **A22 — human pineal H&E, very high magnification**  
  URL: https://commons.wikimedia.org/wiki/File:Pineal_gland_-_very_high_mag.jpg  
  Verified content: 2848×4272, CC BY-SA 3.0.  
  Use: cellular-scale transition / microscopic movement.
- **A67 — Pinealocyte rosettes in older pineal gland**  
  URL: https://commons.wikimedia.org/wiki/File:Pinealocyte_Rosettes_in_Older_Pineal_Gland_(40440642443).jpg  
  Verified content: 3264×1840 human H&E, CC0.  
  Use: rights-simple histology reserve; avoid implying age changes cause consciousness effects.
- **A68 — Pinealocytes and astrocytes in young human pineal gland**  
  URL: https://commons.wikimedia.org/wiki/File:Pinealocytes_and_Astrocytes_in_Young_Human_Pineal_Gland_(40406903583).jpg  
  Verified content: 3264×1840 human H&E, CC0.  
  Use: alternate cellular texture / comparative macro state.
- **A24 — scanning electron microscopy of human pineal gland**  
  URL: https://commons.wikimedia.org/wiki/File:Scanning_electron_microscopy_images_of_the_human_pineal_gland,_obtained_through_a_modified_freeze-fractured_sample_procedure.png  
  Verified content: correct 3741×1945 SEM image and underlying 2024 article.  
  Rights: Commons carries a license-review warning.  
  Use: HOLD only; do not put in final edit until Codex resolves license consistency.

### 5. Retina / circadian pathway

- **A20 — Cajal retina drawing, 1911**  
  URL: https://commons.wikimedia.org/wiki/File:Fig_retine.png  
  Verified content: 624×269 historic retinal architecture, public domain.  
  Use: elegant bridge from eye as image-maker to eye as timing sensor.
- **A60 — Retina-diagram.svg**  
  URL: https://commons.wikimedia.org/wiki/File:Retina-diagram.svg  
  Verified content: cleaner vector derivative of Cajal architecture, CC BY-SA 3.0.  
  Use: animation-friendly layer tracing.
- **A61 — Overview of retina photoreceptors (a)**  
  URL: https://commons.wikimedia.org/wiki/File:Overview_of_the_retina_photoreceptors_(a).png  
  Verified content: 1266×391 scientific figure by Blume/Garbazza/Spitschan, CC BY 4.0.  
  Use: modern photoreceptor-cell context before SCN route.
- **A62 — Overview of retina photoreceptors (b)**  
  URL: https://commons.wikimedia.org/wiki/File:Overview_of_the_retina_photoreceptors_(b).png  
  Verified content: 1181×432 spectral-sensitivity figure, CC BY 4.0.  
  Use: optional; only include if spectral sensitivity helps the story rather than making it lecture-like.
- **A26 — SCN input/output pathways**  
  URL: https://commons.wikimedia.org/wiki/File:Input_and_output_pathways_of_the_suprachiasmatic_nuclei_(SCN).png  
  Verified content: 1296×669, Blume/Garbazza/Spitschan 2019, CC BY 4.0.  
  Use: principal retina→SCN→pineal mechanism source. Animate one path at a time.
- **A27 — light, SCN and pineal/melatonin circuit**  
  URL: https://commons.wikimedia.org/wiki/File:Light,_suprachiasmatic_nuclei_(SCN),_and_the_pinealmelatonin_circuit.jpg  
  Verified content: 718×261 figure from Ma et al., CC BY 4.0.  
  Use: the clearest support for `The sky becomes a molecule.`
- **A28 — Circadian rhythm.svg**  
  URL: https://commons.wikimedia.org/wiki/File:Circadian_rhythm.svg  
  Verified content: SVG, CC BY-SA 4.0.  
  Use: larger day/night context around melatonin; secondary, not primary evidence.
- **A29 — Suprachiasmatic Nucleus.jpg**  
  URL: https://commons.wikimedia.org/wiki/File:Suprachiasmatic_Nucleus.jpg  
  Verified content: 2976×1828 brain-location diagram, CC BY-SA 3.0.  
  Use: short SCN location insert.
- **A30 — Rohde et al. circadian pineal paper**  
  URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC4022116/  
  Verified content: correct open-access article, CC BY.  
  Use: optional molecular-rhythm proof layer if the edit needs one more scale change.

### 6. E-reader study and researchers

- **A31 — Chang et al., PNAS 2015**  
  URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC4313820/  
  Verified content: exact e-reader study. The paper supports 12 healthy adults, randomized crossover conditions, five consecutive evenings, approximately four hours of reading before bed, melatonin suppression/phase delay, longer sleep latency and lower next-morning alertness.  
  Use: show title/byline + readable Methods/Results excerpts; recreate clean data graphics from reported values rather than assuming every published figure is freely reusable.
- **A32 — Anne-Marie Chang official Penn State profile**  
  URL: https://pure.psu.edu/en/persons/anne-marie-chang/  
  Verified content: correct researcher and official portrait.  
  Rights: no open reuse license identified.  
  Use: HOLD_CLEARANCE; paper/byline can represent her if permission is not worth pursuing.
- **A57 — Charles A. Czeisler, U.S. Navy photo**  
  URL: https://commons.wikimedia.org/wiki/File:180531-N-PO203-0057_(27622706847).jpg  
  Verified content: Czeisler lecturing, 4928×3280. U.S. Navy federal work, public domain.  
  Use: production-safe researcher portrait / lecture-context shot for the study team.
- **A33/A34 — Harvard Czeisler/Duffy profiles**  
  URLs: https://sleep.hms.harvard.edu/faculty-staff/charles-czeisler and https://sleep.hms.harvard.edu/faculty-staff/jeanne-f-duffy  
  Verified status: correct official pages are indexed, but automated retrieval was blocked and no open portrait license is established.  
  Use: research identity only; A57 replaces Czeisler's profile image for production.
- **A35 — Manuel Spitschan profile**  
  URL: https://portal.fis.tum.de/en/persons/manuel-spitschan/  
  Verified content: correct institutional profile.  
  Rights: no open portrait reuse license identified.  
  Use: optional/clearance; his CC BY scientific figures are more useful than the face.
- **A36 — Christine Blume profile**  
  URL: https://www.chronobiology.ch/team/christine-blume/  
  Verified content: correct institutional profile and portrait.  
  Rights: no open portrait reuse license identified.  
  Use: optional/clearance; use licensed figure authorship instead if necessary.
- **A12 — Arthur Dendy portrait**  
  URL: https://catalogues.royalsociety.org/CalmView/Record.aspx?id=IM%2F001128&src=CalmView.Catalog  
  Verified content: correct 1922 Russell & Sons Dendy portrait.  
  Rights: catalogue explicitly states Royal Society copyright.  
  Use: only with permission; the episode does not need this portrait badly enough to create a rights bottleneck.

### 7. Descartes / Elisabeth bridge

- **A37 — René Descartes portrait, Statens Museum for Kunst**  
  URL: https://commons.wikimedia.org/wiki/File:Frans_I_Hals,_Ren%C3%A9_Descartes_1596-1650,_DEP7,_Statens_Museum_for_Kunst.jpg  
  Verified content: 2953×3877 museum-quality state; public domain / CC0 digital reproduction.  
  Use: clean face reveal when narration turns from biological time to consciousness.
- **A38 — Descartes nervous-system/brain diagram, Wellcome**  
  URL: https://commons.wikimedia.org/wiki/File:Descartes%3B_The_Nervous_System._Diagram_of_the_brain_Wellcome_L0006584.jpg  
  Verified content: 5787×3018, CC BY 4.0.  
  Use: ideal final visual because it places eye, brain and Cartesian physiology in one authentic historical frame.
- **A39/A40 — additional Cartesian diagrams**  
  URLs: https://commons.wikimedia.org/wiki/File:Descartes_diagram.png and https://commons.wikimedia.org/wiki/File:Descartes_brain_section.png  
  Verified content: historical public-domain diagrams, 836×1029 and 800×1000.  
  Use: backup/close-up states so A38 is not stretched across the whole handoff.
- **A41 — Princess Elisabeth of the Palatinate, Rijksmuseum**  
  URL: https://commons.wikimedia.org/wiki/File:Elizabeth_(1618-80)_van_de_Paltz,_dochter_van_Frederik_V,_koning_van_Bohemen,_bijgenaamd_de_%27Winterkoning%27_Rijksmuseum_SK-A-4314.jpeg  
  Verified content: correct philosopher Princess Elisabeth, 1905×2658; Rijksmuseum/public-domain artwork with open data/CC0 treatment.  
  Use: face reveal immediately before her challenge to Descartes.
- **A42 — Elisabeth to Descartes, 16 May 1643**  
  URL: https://fr.wikisource.org/wiki/Correspondance_avec_%C3%89lisabeth/%C3%89lisabeth_%C3%A0_Descartes_-_La_Haye%2C_16_mai_1643  
  Verified content: correct letter text in the public-domain Adam & Tannery edition.  
  Use: locator/transcription plus link path to archival scan; final viewer card should show the facsimile page, not generic webpage chrome.
- **A43 — Stanford Encyclopedia archived entry**  
  URL: https://plato.stanford.edu/archives/sum2026/entries/pineal-gland/  
  Verified content: Summer 2026 archive of *Descartes and the Pineal Gland*.  
  Use: scholarly locator only; not a visual asset.

### 8. Historical esoteric / chakra material

These are cultural-history assets, never scientific evidence.

- **A44 — Traditional Hindu Diagram of Brow Chakra**  
  URL: https://commons.wikimedia.org/wiki/File:Traditional_Hindu_Diagram_of_Brow_Chakra.jpg  
  Verified content: 463×351 historic Ajna/brow chakra diagram associated with John Woodroffe's *The Serpent Power*; public domain.  
  Use: authentic early-20th-century published Ajna image, explicitly captioned as esoteric/historical.
- **A45 — Ajna chakra.svg**  
  URL: https://commons.wikimedia.org/wiki/File:Ajna_chakra.svg  
  Verified content: modern clean vector by Flappiefh, CC BY-SA 3.0.  
  Use: animated Ajna symbol after historical context has been established.
- **A46 — Chakra6.svg**  
  URL: https://commons.wikimedia.org/wiki/File:Chakra6.svg  
  Verified content: modern CC0 Ajna symbol.  
  Use: rights-simple motion-graphics alternative.
- **A47 — Leadbeater's Chakras Pictures**  
  URL: https://commons.wikimedia.org/wiki/File:Leadbeater%27s_Chakras_Pictures.JPG  
  Verified content: 1700×2200 public-domain plate collection from *The Chakras* (1927), explicitly described as clairvoyantly observed depictions.  
  Use: strong Theosophical visual; captioning must make clear this is esoteric literature, not measurement.
- **A48 — 7 Chakras Combined Reordered**  
  URL: https://commons.wikimedia.org/wiki/File:7_Chakras_Combined_Reordered.JPG  
  Verified content: 576×792 Leadbeater-derived public-domain full-body chakra image.  
  Use: system-level context rather than a decontextualized forehead symbol.
- **A49 — Pineal Gland and Pituitary Body**  
  URL: https://commons.wikimedia.org/wiki/File:Pineal_Gland_and_Pituitary_Body.jpg  
  Verified content: historically relevant public-domain Leadbeater image but only 291×170.  
  Use: brief reference insert only; Codex should try to reacquire the original page from a full book scan for better resolution.
- **A63 — Sapta Chakra, 1899**  
  URL: https://commons.wikimedia.org/wiki/File:Sapta_Chakra,_1899.jpg  
  Verified content: 1993×3393 historical Indian manuscript image, public domain.  
  Use: high-quality historical chakra-system context that predates Leadbeater and avoids modern anonymous mystic art.
- **A64 — Sapta Chakra cropped state**  
  URL: https://commons.wikimedia.org/wiki/File:Sapta_Chakra,_1899_(cropped).jpg  
  Verified content: 1993×2294 public-domain crop.  
  Use: closer editorial state only after showing full context.
- **A69 — Yogin in meditation, chakras and kundalini serpent**  
  URL: https://commons.wikimedia.org/wiki/File:Yogin_in_meditation_chakras_kundalini_snake.jpg  
  Verified content: 2936×3809 historical Indian yogic/chakra image.  
  Use: meditation/kundalini cultural resonance; do not connect it causally to human pineal physiology.
- **A70 — Yogin with six chakras, Kangra**  
  URL: https://commons.wikimedia.org/wiki/File:Yogin_with_six_chakras,_India,_Punjab_Hills,_Kangra,_late_18th_century.jpg  
  Verified content: correct historical painting but only 250×498.  
  Use: backup/brief insert only because of resolution.

### 9. Museum-grade religious third-eye iconography — The Met Open Access

All seven object pages below were verified as the intended works and marked Public Domain / Download Image by The Met. Preserve object title, culture/date, accession source and museum credit in the rights register even where attribution is not legally required.

- **A50 — Shiva, mid-7th century** — https://www.metmuseum.org/art/collection/search/38158  
  Use: sculptural vertical third-eye iconography.
- **A51 — Shiva print, ca. 1880–1900** — https://www.metmuseum.org/art/collection/search/722761  
  Use: very readable full-figure cultural-history shot.
- **A52 — Madan-Bhasma, 1890** — https://www.metmuseum.org/art/collection/search/78255  
  Verified description explicitly states Shiva opens his third eye and burns Kama.  
  Use: strongest narrative/mythic third-eye image.
- **A53 — Harihara** — https://www.metmuseum.org/art/collection/search/38162  
  Use: iconographic continuity; Shiva half retains the vertical eye.
- **A54 — Ekamukhalinga** — https://www.metmuseum.org/art/collection/search/38250  
  Use: strong close face / third-eye macro detail.
- **A55 — Kali chromolithograph** — https://www.metmuseum.org/art/collection/search/78257  
  Verified description notes light from the third eye.  
  Use: late-19th-century devotional print-state alternative.
- **A56 — Shiva as Mrityunjaya** — https://www.metmuseum.org/art/collection/search/38127  
  Use: three-eye/yogic posture connection in historical iconography.

## Production selection recommendation

The final edit should not use all 70 rows. Recommended Tier-1 picture pool after Codex acquisition:

1. 4–5 TimVickers living tuatara states.
2. A58 Hatteria pineal-eye illustration.
3. Dendy title/page + Plates XI–XIII.
4. Spencer Anolis + Varanus and one additional comparative plate.
5. Romero/de Souza modern source card.
6. Gray/CRUK human pineal location.
7. Two real pineal histology states.
8. Cajal/retina photoreceptor state.
9. A26 SCN route + A27 light→melatonin route.
10. Chang paper + recreated study design/outcome graphics.
11. Czeisler public-domain Navy photo if a researcher face improves pacing.
12. Descartes portrait + Wellcome diagram.
13. Elisabeth Rijksmuseum portrait + facsimile letter page.
14. Two historical chakra assets maximum in EP09 unless the edit explicitly creates a short cultural-resonance beat.
15. Two to three Met third-eye objects maximum, with A52 as the strongest narrative choice.

This yields enough authentic material to cut the episode primarily from real assets rather than generated filler while keeping science, history and esoteric iconography visibly separated.
