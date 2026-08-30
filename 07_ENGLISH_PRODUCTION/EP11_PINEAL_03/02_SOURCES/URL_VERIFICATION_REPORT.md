# EP11_EN — URL Verification and Asset Suitability Audit

Verified: 2026-08-30

Purpose: validate every previously proposed asset endpoint as an actual usable source, correct bad filenames/search-only links, distinguish exact file pages from discovery pages, and add stronger production candidates.

Status vocabulary:
- `VERIFIED_EXACT`: exact object/file/article page opened and content matches the intended asset.
- `VERIFIED_DISCOVERY`: category/search/collection endpoint is live and relevant, but Codex must choose a concrete rights-clean item before acquisition.
- `VERIFIED_REFERENCE`: source is valid for text/research but should not be the preferred viewer-facing image master.
- `RIGHTS_HOLD`: content matches, but reuse must not be assumed from hosting alone.
- `REPLACED`: earlier URL/filename was wrong or needlessly generic and is superseded below.

## High-priority exact assets

### 1. Helena P. Blavatsky — Rijksmuseum portrait
- Exact page: https://commons.wikimedia.org/wiki/File:Portret_van_Helena_Blavatsky,_RP-F-2001-7-67-105.jpg
- Verified content: portrait of Helena Blavatsky; Rijksmuseum object RP-F-2001-7-67-105; ca. 1881–1891.
- Original size reported by source: 3484 × 4708 JPEG.
- Rights: CC0 1.0 / public-domain dedication.
- Production use: strongest opening identity anchor; face close-up; return shot during the Blavatsky synthesis.
- Status: `VERIFIED_EXACT`.

### 2. Walter Baldwin Spencer portrait
- Exact page: https://commons.wikimedia.org/wiki/File:Walter_Baldwin_Spencer.jpg
- Verified content: Walter Baldwin Spencer (1860–1929), historical portrait.
- Original size: 677 × 988 JPEG.
- Rights: Commons page marks public domain because of age.
- Use: human face for nineteenth-century comparative anatomy before showing reptile plates.
- Claim limit: identity only; never imply the portrait itself documents the pineal-eye work.
- Status: `VERIFIED_EXACT`.

### 3. Franz von Leydig portrait
- Exact page: https://commons.wikimedia.org/wiki/File:Franz_Leydig.jpg
- Verified content: Franz von Leydig; published 1908; National Library of Medicine source.
- Original size: 996 × 1360 JPEG.
- Rights: public domain / Public Domain Mark on Commons; NLM believed item public domain.
- Use: early histology/comparative-anatomy genealogy.
- Status: `VERIFIED_EXACT`.

### 4. C. W. Leadbeater portrait
- Exact page: https://commons.wikimedia.org/wiki/File:Charles_Webster_Leadbeater.003.jpg
- Verified content: Charles Webster Leadbeater (1847–1934), Theosophical Society.
- Original size: 312 × 490 JPEG.
- Rights: Commons marks public domain, but source/author metadata are thin. Preserve the file-page rights capture.
- Use: identity reveal immediately before the 1927 gland/chakra contradiction.
- Status: `VERIFIED_EXACT`.

### 5. Hatteria/Sphenodon pineal-eye plate
- Exact page: https://commons.wikimedia.org/wiki/File:PSM_V33_D805_Pineal_eye_in_hatteria.jpg
- Verified content: pineal eye in tuatara/Sphenodon; labels nerve, blood vessel, retina, rods and cones; Popular Science Monthly Vol. 33, 1887–1888.
- Original size: 1210 × 1581 JPEG.
- Rights: public domain / PD-old on Commons.
- Use: one of the best scientific evidence frames for the line about genuinely eye-like structures.
- Status: `VERIFIED_EXACT`.

### 6. Varanus pineal-eye plate
- Exact page: https://commons.wikimedia.org/wiki/File:PSM_V33_D806_Pineal_eye_in_varanus_giganteus.jpg
- Verified content: same historical Popular Science Monthly plate sequence; live exact file endpoint confirmed through the Volume 33 asset listing.
- Rights: historical public-domain source; retain Commons file-page capture at acquisition.
- Use: alternate species plate to avoid visually overusing the Hatteria diagram.
- Status: `VERIFIED_EXACT`.

### 7. Iguana parietal-eye plate — corrected filename
- Correct exact page: https://commons.wikimedia.org/wiki/File:Klinckowstroem_(1894)_parietal_eye_of_Iguana.png
- Earlier proposal with `.jpg` was wrong and is replaced.
- Verified content: Axel von Klinckowstroem 1894 parietal-eye figure; image reproduced in Tilney & Warren 1919 p.127.
- Original size: 470 × 329 PNG.
- Rights: public domain in source country and US; Commons Public Domain Mark.
- Use: close-up morphological/histological evidence.
- Status: `VERIFIED_EXACT`, `REPLACED_BAD_FILENAME`.

### 8. Modern visible parietal eye — Anolis carolinensis
- Exact page: https://commons.wikimedia.org/wiki/File:Anolis_carolinensis_parietal_eye.JPG
- Verified content: dorsal view of Anolis carolinensis clearly showing parietal eye.
- Original size: 760 × 581 JPEG.
- Rights: CC BY-SA 3.0; attribution/link/change indication required.
- Use: real-animal reality check after historical diagrams.
- Status: `VERIFIED_EXACT`.

### 9. Tilney & Warren 1919 pineal-body monograph
- Exact page: https://commons.wikimedia.org/wiki/File:Morphology_and_Evolutional_Significance_of_the_Pineal_Body.pdf
- Verified content: *The morphology and evolutional significance of the pineal body*, Frederick Tilney and Luther Fiske Warren, Wistar Institute, 1919.
- File: 268-page PDF, about 17 MB; scan sourced from Internet Archive/MBLWHOI.
- Rights: public domain in the US; Commons-hosted old scientific work.
- Use: deep source pool for historical morphology, diagrams, comparative plates, publication-context shots.
- Important: use selected pages as historical evidence, not as standalone modern scientific consensus.
- Status: `VERIFIED_EXACT`.

### 10. Traditional Brow Chakra / Ajna diagram from *The Serpent Power*
- Exact page: https://commons.wikimedia.org/wiki/File:Traditional_Hindu_Diagram_of_Brow_Chakra.jpg
- Verified content: “Traditional Hindu Diagram of Brow Chakra”, source *The Serpent Power*, Sir John Woodroffe, dated 1918 on Commons.
- Original size: 463 × 351 JPEG.
- Rights: Commons marks public domain.
- Use: exact Ajna close-up; visually separates the spiritual forehead center from the anatomical pineal gland.
- Claim limit: do not place a pineal label on this image.
- Status: `VERIFIED_EXACT`.

### 11. Rajasthan brow-chakra image
- Exact page: https://commons.wikimedia.org/wiki/File:Brow_Chakra_Rajasthan_18th_Century.JPG
- Verified content: brow chakra, Rajasthan, 18th century.
- Original size: 1605 × 914 JPEG.
- Rights: public domain on Commons.
- Use: strong pre-modern visual demonstrating that brow-center symbolism predates twentieth-century gland mapping.
- Status: `VERIFIED_EXACT`.

### 12. Avalon/Wellcome “centres or Lotuses of Yoga” image
- Exact Commons page: https://commons.wikimedia.org/wiki/File:The_centres_or_Lotuses_of_Yoga,_in_Avalon%27s_The_Serpent_Power_Wellcome_M0005455.jpg
- Verified content: historical Wellcome image representing the centres/lotuses of Yoga in Avalon's *The Serpent Power*.
- Commons metadata exposes a CC BY 4.0 statement on the digitized image.
- Important rights nuance: Wellcome's current catalogue record for M0005455 describes the 1938 glass-plate item as “In copyright”. Therefore treat the Commons derivative and current Wellcome record as a rights discrepancy that Codex must capture and resolve before commercial picture lock.
- Use: full subtle-body-map context if rights review clears; otherwise prefer the public-domain Woodroffe/Ajna files above.
- Status: `RIGHTS_HOLD_METADATA_CONFLICT`.

### 13. Shiva with clearly visible third eye — Musée Guimet object photograph
- Exact page: https://commons.wikimedia.org/wiki/File:Shiva_Mus%C3%A9e_Guimet_22971.jpg
- Verified content: Shiva head, Cambodia, Phnom Bok, Bakheng style, late 9th–early 10th century; visible third eye in forehead.
- Original size: 1770 × 2551 JPEG.
- Rights: photographer explicitly released own photograph into public domain worldwide on Commons.
- Use: excellent religious-symbolism anchor for “Eye of Shiva”; full-object shot plus forehead close crop.
- Claim limit: religious/art-historical image only; never evidence for anatomical pineal identification.
- Status: `VERIFIED_EXACT`.

### 14. Cosmic Man / six-chakra transformation — LACMA
- Exact page: https://commons.wikimedia.org/wiki/File:Cosmic_Man_with_Diagrams_of_Newar_Yogic_Six_Chakra_Transformation_LACMA_M.91.118.jpg
- Verified content: LACMA object, “Cosmic Man with Diagrams of Newar Yogic Six Chakra Transformation”.
- Original size reported by Commons: 1255 × 2100 JPEG.
- Use: rich body-as-symbolic-map montage; secondary spiritual visual, not a direct Ajna-pineal proof.
- Acquisition rule: record exact Commons/LACMA rights metadata before final use.
- Status: `VERIFIED_EXACT_CONTENT_RIGHTS_CAPTURE_REQUIRED`.

### 15. Leadbeater — Pineal Gland and Pituitary Body
- Exact page: https://commons.wikimedia.org/wiki/File:Pineal_Gland_and_Pituitary_Body.jpg
- Verified content: diagram titled “Pineal Gland and Pituitary Body Location inside the Brain”; source C. W. Leadbeater, *The Chakras*, 1927.
- Original size: 291 × 170 JPEG; low resolution but historically valuable.
- Rights: Commons marks the work public domain in countries with life+70 or less and identifies it as free of known restrictions; Leadbeater died 1934, so Germany/EU life+70 has expired.
- Use: crucial visual for the episode's argument that later occult writers actively mapped subtle centers onto glands.
- Status: `VERIFIED_EXACT`.

### 16. Leadbeater broader category
- Category: https://commons.wikimedia.org/wiki/Category:The_Chakras_by_C._W._Leadbeater
- Verified purpose: relevant discovery pool for additional color plates and nervous-plexus diagrams.
- Use: discovery only; promote each chosen image to its own exact URL before acquisition.
- Status: `VERIFIED_DISCOVERY`.

### 17. Theosophical Society seal
- Preferred exact vector: https://commons.wikimedia.org/wiki/File:Theosophicalseal.svg
- Also verified raster: https://commons.wikimedia.org/wiki/File:Theosophical_Society_Seal.jpg
- Verified content: Theosophical Society emblem incorporating interlaced triangles, ouroboros, manji, ankh, Om; basic design traced to 1875.
- Rights: SVG uploader releases own work into public domain and underlying historical emblem is marked public domain.
- Use: organizational-context transition, preferably the SVG for clean motion treatment.
- Status: `VERIFIED_EXACT`.

### 18. Descartes pineal diagram
- Preferred exact page: https://commons.wikimedia.org/wiki/File:Descartes_diagram.png
- Verified content: drawing from Descartes' *Treatise of Man* showing sensory signals reaching the pineal gland and acting on the immaterial mind.
- Original: 836 × 1029 PNG current file.
- Rights: Commons identifies original historical work as public domain; page notes PD-Art/reproduction considerations.
- Use: very brief callback to EP10 when narration says Descartes charged the pineal gland with soul-body significance.
- Status: `VERIFIED_EXACT`.

### 19. Descartes pineal in situ — Wellcome high-resolution alternative
- Exact page: https://commons.wikimedia.org/wiki/File:Descartes%3B_view_of_posterior_of_brain_Wellcome_L0008518.jpg
- Verified content: posterior brain view showing pineal in situ; Wellcome Rare Books.
- Original size: 1282 × 1612 JPEG.
- Use: alternate Descartes callback with clearer anatomical context.
- Status: `VERIFIED_EXACT_CONTENT_RIGHTS_CAPTURE_REQUIRED`.

### 20. DMT 2019 — Nature / Scientific Reports
- Exact article: https://www.nature.com/articles/s41598-019-45812-w
- DOI: https://doi.org/10.1038/s41598-019-45812-w
- PMC mirror: https://pmc.ncbi.nlm.nih.gov/articles/PMC6597727/
- Verified content: Dean et al., “Biosynthesis and Extracellular Concentrations of N,N-dimethyltryptamine (DMT) in Mammalian Brain”, Scientific Reports 9, 9333 (2019), published 27 June 2019.
- Rights: PMC explicitly states CC BY 4.0 for article content, subject to third-party figure credit exceptions.
- Use: final laboratory bridge to EP12; article title/figure/data state.
- Claim limit: rat/mammalian-brain data; no direct inference to human dreams, birth, death or mystical experience.
- Status: `VERIFIED_EXACT`.

## Previously proposed discovery/reference URLs that are valid but not acquisition-ready

- https://commons.wikimedia.org/wiki/Category:Ajna — live relevant category, `VERIFIED_DISCOVERY`; replace with exact files such as the two verified brow-chakra images above.
- https://commons.wikimedia.org/wiki/Category:Chakras — live broad category, `VERIFIED_DISCOVERY`; too generic to remain a final production asset endpoint.
- https://commons.wikimedia.org/wiki/Category:Pineal_gland — live anatomy discovery category, `VERIFIED_DISCOVERY`; select exact historical anatomy file before lock.
- https://commons.wikimedia.org/wiki/Category:Theosophical_Society — live context category, `VERIFIED_DISCOVERY`; never download the category itself.
- https://commons.wikimedia.org/wiki/Category:Theosophical_Society_Adyar — discovery/context only; require exact file promotion.
- https://archive.org/search?query=%22pineal+eye%22+Spencer+Lacertilia — search endpoint is useful for discovery but is not a source master; use `VERIFIED_DISCOVERY` and prefer exact public-domain plates/monographs where possible.
- https://archive.org/search?query=%22Thought-Forms%22+Besant+Leadbeater — discovery only; exact edition/scan and jurisdiction rights must be captured before use.
- https://www.theosociety.org/pasadena/sd/sd-hp.htm — valid text/reference pathway for *The Secret Doctrine*; `VERIFIED_REFERENCE`, not preferred viewer-facing archive image.
- https://sacred-texts.com/the/sd/sd2-0-co.htm — valid searchable transcription; `VERIFIED_REFERENCE`, not picture master.
- https://www.aghori.it/woodroffe_the_serpent_power.pdf — valid research PDF endpoint but final image master should preferably be an exact rights-clean scan/file page; `VERIFIED_REFERENCE`.
- https://lakshminarayanlenasia.com/articles/Chakras-by-CW-Leadbeater.pdf — research PDF is useful for wording/page verification; exact Commons files are now preferred for viewer-facing diagrams.

## Corrections applied to earlier shortlist

1. `Klinckowstroem_1894_parietal_eye_of_Iguana.jpg` was incorrect. Correct file is `Klinckowstroem_(1894)_parietal_eye_of_Iguana.png`.
2. Generic Ajna/Chakra category links are demoted from asset status to discovery status; exact Woodroffe/Rajasthan files are now primary.
3. Generic Met/Cleveland collection searches are no longer treated as selected assets. A concrete public-domain Shiva file from Musée Guimet is now the first-choice third-eye object.
4. Generic Leadbeater category is demoted to discovery; `Pineal_Gland_and_Pituitary_Body.jpg` is promoted to exact primary evidence.
5. Generic Descartes historical-illustration category is demoted; `Descartes_diagram.png` and a Wellcome pineal-in-situ file are promoted.
6. Wellcome M0005455 has a metadata conflict: Commons exposes CC BY 4.0 while the current Wellcome catalogue marks the glass-plate item “In copyright”. It stays on hold until Codex records the exact rights basis of the file actually used.

## Production conclusion

EP11 now has a verified, redundant asset spine rather than a collection of untested search links. Priority acquisition should begin with the exact Blavatsky, Spencer, Leydig, Leadbeater, Hatteria, Varanus, Iguana, Anolis, Tilney/Warren, Woodroffe/Ajna, Rajasthan, Shiva, Theosophical seal, Descartes and DMT endpoints above. Category/search links remain useful only for optional expansion.