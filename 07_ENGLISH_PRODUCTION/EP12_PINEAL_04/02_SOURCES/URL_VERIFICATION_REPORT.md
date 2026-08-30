# EP12_EN — URL Verification Report

**Episode:** `EP12_PINEAL_04 — DMT at the Threshold`  
**Verification date:** 2026-08-30  
**Purpose:** live-check every previously researched source/asset URL, correct bad or fragile links, add additional high-value assets, and define the exact production use before Codex downloads anything.

## Status vocabulary

- `VERIFIED_GREEN` — source page is live, content matches, and reuse license/public-domain basis is explicit.
- `VERIFIED_GREEN_EXTRACT` — source/PDF is live and reusable; extract the required figure from the verified document instead of depending on an unverified CDN URL.
- `VERIFIED_SOURCE_ONLY` — source is live and appropriate as research/document evidence, but copyrighted media/figure reuse is not cleared.
- `VERIFIED_REFERENCE_ONLY` — real portrait/photo/source is live and correct, but production reuse requires permission or an explicit license.
- `REPLACED` — earlier URL or asset choice was incorrect, fragile, lower quality, or had a different license than assumed; use the replacement listed here.
- `DIRECT_URL_UNVERIFIED` — the publisher/source is verified, but the standalone CDN/download URL could not be independently fetched; do not treat the CDN URL as canonical.

**Important:** URL availability is not the same thing as reuse permission. A live university/news image remains `REFERENCE_ONLY` unless its reuse basis is explicit.

---

# A — Core DMT / pineal / human-DMT scientific evidence

| ID | Verified source / download | Live-content verdict | Rights / technical verdict | Exact production use | Action |
|---|---|---|---|---|---|
| A01 | https://www.nature.com/articles/s41598-019-45812-w.pdf | **LIVE PDF; correct Dean et al. 2019 paper; 11 pages.** Contains the rat visual-cortex experiment, pinealectomy comparison, INMT data and figures 1–4. | **CC BY 4.0** stated in the article; third-party credit lines still checked at extraction. | Opening paper reveal; recurring primary-source anchor. | `VERIFIED_GREEN` — archive full PDF + rights page/snapshot. |
| A01B | https://pmc.ncbi.nlm.nih.gov/articles/PMC6597727/ | Correct freely accessible mirror of Dean et al. 2019. | Use as robust text/figure fallback if Nature frontend/CDN is inconvenient. | Research verification and emergency extraction fallback. | `VERIFIED_GREEN_SOURCE` |
| A02 | Dean 2019 **Figure 1**, extracted from A01 PDF/article | Content verified: INMT mRNA expression in rat visual cortex, human medial frontal cortex, rat/human pineal and choroid plexus. | Covered by article CC BY unless a figure credit says otherwise. Earlier direct `media.springernature.com/...Fig1...png` could not be independently fetched by the URL checker. | Show that the source question extends beyond one gland. | `VERIFIED_GREEN_EXTRACT` — extract from verified PDF, do not depend on CDN URL. |
| A03 | Dean 2019 **Figure 2**, extracted from A01 PDF/article | Content verified: INMT/AADC colocalization / cellular molecular machinery. | Same article-license rule; direct CDN not canonical. | Microscopy/molecular-machinery sequence instead of generic glowing-neuron art. | `VERIFIED_GREEN_EXTRACT` |
| A04 | Dean 2019 **Figure 3**, extracted from A01 PDF/article | Correct paper figure; peripheral-tissue INMT/AADC context. | Same article-license rule. | Briefly widen DMT-biosynthesis context beyond a single organ. | `VERIFIED_GREEN_EXTRACT` |
| A05 | Dean 2019 **Figure 4**, extracted from A01 PDF/article | **Central result verified:** extracellular DMT measured in rat visual cortex; pineal-intact vs pinealectomized groups; post-cardiac-arrest increase; no significant post-arrest group difference reported. | Article CC BY 4.0 unless separate credit. Direct publisher image URL is non-canonical because independent CDN fetch was unreliable. | Main evidence reveal: gland present / gland removed / cardiac arrest. | `VERIFIED_GREEN_EXTRACT` — retain full-page and full-figure masters before any crop. |
| A06 | https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2018.01424/full | **LIVE; correct Timmermann et al. 2018 article, “DMT Models the Near-Death Experience”.** | **CC BY 4.0** explicit. | Human DMT/NDE phenomenology bridge. | `VERIFIED_GREEN` |
| A06PDF | https://www.frontiersin.org/articles/10.3389/fpsyg.2018.01424/pdf | **LIVE PDF; 12 pages; correct article.** | CC BY 4.0. | Archive master for document shots. | `VERIFIED_GREEN` |
| A07 | Relevant comparison table/page from A06PDF | Correct comparison material in the verified paper. | CC BY 4.0. | Show the full table/page, then highlight only the features discussed. | `VERIFIED_GREEN_EXTRACT` |
| A08 | https://commons.wikimedia.org/wiki/File:FMRI_Static_Resting-State_Functional_Connectivity_effects_of_DMT.jpg | **LIVE; correct PNAS 2023 DMT fMRI figure; original 2523×3065.** | **CC BY 4.0.** | Real human-administered-DMT fMRI evidence; replace generic psychedelic brain graphics. | `VERIFIED_GREEN` |
| A09 | https://commons.wikimedia.org/wiki/File:FMRI_Dynamic_Resting-State_Functional_Connectivity_effects_of_DMT.jpg | **LIVE; correct PNAS 2023 dynamic-connectivity figure; original 3995×2973.** | **CC BY 4.0.** | Alternate dynamic brain-network visual. | `VERIFIED_GREEN` |
| A10 | https://commons.wikimedia.org/wiki/File:FMRI_Principal_Cortical_Gradient_effects_of_DMT.jpg | **LIVE; correct PNAS 2023 figure; original 3755×3294.** | **CC BY 4.0.** | Scientific network/gradient visual during “what does DMT do?” section. | `VERIFIED_GREEN` |
| A11 | https://commons.wikimedia.org/wiki/File:EEG_Spectral_Power,_Signal_Diversity,_and_Cortical_Traveling_Waves_of_DMT.jpg | **LIVE; correct PNAS 2023 EEG figure; original 3914×2465.** | **CC BY 4.0.** | Real electrophysiology showing administered-DMT changes. | `VERIFIED_GREEN` |
| A12 | https://commons.wikimedia.org/wiki/File:Parallel_Changes_in_EEG_%26_fMRI_induced_by_DMT.jpg | **LIVE; correct simultaneous EEG/fMRI figure; original 2487×3489, 1.28 MB.** | **CC BY 4.0.** | Excellent single frame linking EEG and fMRI changes; strong visual for “measurement catches several dimensions at once.” | `VERIFIED_GREEN` — **new asset.** |
| A13 | https://www.pnas.org/doi/10.1073/pnas.2218949120 | Correct 2023 source paper for A08–A12: *Human brain effects of DMT assessed via EEG-fMRI*. | Use article as source/document anchor; Commons versions provide the clearly licensed figure files. | Paper-title/authorship context for the five human-DMT figures. | `VERIFIED_SOURCE`; use Commons for figure acquisition. |
| A13B | https://pmc.ncbi.nlm.nih.gov/articles/PMC10068756/ | Correct PMCID mirror/source for 2023 paper; access may occasionally trigger browser verification but identity is confirmed. | Research/source fallback. | Source verification and text lookup. | `VERIFIED_SOURCE` |
| A14 | https://pmc.ncbi.nlm.nih.gov/articles/PMC6864083/ | **LIVE; correct 2019 Scientific Reports human DMT EEG paper**, *Neural correlates of the DMT experience assessed with multivariate EEG*. | Article is Open Access; Nature record states CC BY 4.0. | Earlier human EEG evidence: alpha/beta reduction, signal-diversity changes and time-linked subjective experience. | `VERIFIED_GREEN_SOURCE` — **new document asset.** |
| A15 | https://pubmed.ncbi.nlm.nih.gov/8297216/ | **LIVE; correct Strassman & Qualls 1994 dose-response study I**, 11 experienced users, IV DMT. | Bibliographic/abstract source; full journal pages are copyrighted. | Historical proof of controlled human DMT administration and physiological measurement. | `VERIFIED_SOURCE_ONLY` — **new source card.** |
| A16 | https://pubmed.ncbi.nlm.nih.gov/8297217/ | **LIVE; correct 1994 dose-response study II**, 12 volunteers, subjective-effects rating. | Bibliographic/abstract source; journal reproduction not assumed. | Historical scientific bridge from Strassman’s human research to later phenomenology work. | `VERIFIED_SOURCE_ONLY` — **new source card.** |
| A17 | https://pubmed.ncbi.nlm.nih.gov/29095071/ | **LIVE; correct David E. Nichols 2018 review**, *N,N-dimethyltryptamine and the pineal gland: Separating fact from myth*. | Use citation/abstract as research evidence; SAGE full-page reuse requires permission. | Scientific counterweight / boundary source for exaggerated pineal-death claims. | `VERIFIED_SOURCE_ONLY` — **new boundary asset.** |

**Claim boundary for A08–A14:** these are studies of **administered DMT in living human participants**, not proof of endogenous DMT release during dying.

---

# B — Human / animal near-death electrophysiology

| ID | Verified source / download | Live-content verdict | Rights / technical verdict | Exact production use | Action |
|---|---|---|---|---|---|
| B01 | https://commons.wikimedia.org/wiki/File:Rise_of_Absolute_EEG_Power_at_Gamma_Frequency_Bands_at_Near-Death.jpg | **LIVE; correct dying-human EEG figure; original 6318×2885, ~4 MB.** | **CC BY 4.0.** | Demonstrate that terminal human brain physiology can be measured directly — but not DMT. | `VERIFIED_GREEN` |
| B02 | https://commons.wikimedia.org/wiki/File:Surge_of_Gamma_Synchrony_Within_the_Posterior_Hot_Zones_at_Near-Death.jpg | **LIVE; correct figure; original 6322×4456, ~4.4 MB.** | **CC BY 4.0.** | Human near-death synchrony context. | `VERIFIED_GREEN` |
| B03 | https://commons.wikimedia.org/wiki/File:Elevated_Phase-Amplitude_Coupling_of_Gamma_Oscillations_at_Near-Death.jpg | **LIVE; correct figure; original ~6323×2444.** | **CC BY 4.0.** | More technical terminal-state physiology if edit needs a second evidence beat. | `VERIFIED_GREEN` |
| B04 | https://commons.wikimedia.org/wiki/File:Increase_of_Cross-Regional_Phase-Amplitude_Coupling_at_Near-Death.jpg | **LIVE; correct figure; original ~6325×4453.** | **CC BY 4.0.** | Cross-region coupling visual. | `VERIFIED_GREEN` |
| B05 | https://commons.wikimedia.org/wiki/File:Elevated_Directed_Connectivity_in_Gamma_Oscillations_Within_the_Posterior_Hot_Zones_at_Near-Death.jpg | **LIVE; correct figure; original ~6307×6271.** | **CC BY 4.0.** | High-density scientific visual for terminal connectivity. | `VERIFIED_GREEN` |
| B06 | https://pubmed.ncbi.nlm.nih.gov/37126719/ | Correct 2023 PNAS source paper: *Surge of neurophysiological coupling and connectivity of gamma oscillations in the dying human brain*. Four comatose dying patients; reported gamma changes in a subset. | Source identity confirmed; use Commons files above for clearly licensed figures. | Paper-title/authorship anchor for B01–B05. | `VERIFIED_SOURCE_ONLY` — **new document anchor.** |
| B06B | https://pmc.ncbi.nlm.nih.gov/articles/PMC10175832/ | Correct PMCID mirror; browser may show anti-bot interstitial but source identity is confirmed. | Research fallback. | Text verification. | `VERIFIED_SOURCE` |
| B07 | https://pubmed.ncbi.nlm.nih.gov/23940340/ | **LIVE; correct 2013 Borjigin et al. PNAS rat cardiac-arrest EEG paper**, *Surge of neurophysiological coherence and connectivity in the dying brain*. | Bibliographic/source use; figure-reuse license not assumed here. | Scientific prehistory: dying-brain electrophysiology in rats before the later human work. | `VERIFIED_SOURCE_ONLY` — **new source.** |

**Hard rule:** B01–B07 are **not DMT measurements**. Never place a DMT molecule label over these figures or narrate them as evidence of a human “DMT flood.”

---

# C — Researchers / portraits / real laboratories

| ID | Verified source / download | Live-content verdict | Rights / technical verdict | Exact production use | Action |
|---|---|---|---|---|---|
| C01 | https://commons.wikimedia.org/wiki/File:Rick_Strassman_(academic).png | **LIVE; correct Rick Strassman portrait; original 1031×1247.** | **CC BY 4.0; VRT permission recorded on Commons.** | Direct identity portrait when Strassman’s pineal/birth/death hypothesis is attributed. | `VERIFIED_GREEN` |
| C02 | https://commons.wikimedia.org/wiki/File:190723_Robin_Carhart-Harris,_Centre_for_Psychedelic_Research_meeting.jpg | **LIVE; correct Robin Carhart-Harris research-meeting photo; downloadable Commons version 600×400.** | **CC BY-SA 4.0; VRT/Commons provenance.** | Optional contemporary psychedelic-research face/context. Use this full frame rather than the tiny cropped derivative. | `VERIFIED_GREEN` — **replacement for earlier crop.** |
| C03 | https://medschool.umich.edu/profile/831/jimo-borjigin | **LIVE; correct Jimo Borjigin official profile and portrait.** | University portrait has no explicit open-content license on the profile. | Coauthor/researcher identity; use as reference for a permission request or reconstruction. | `VERIFIED_REFERENCE_ONLY` |
| C04 | https://borjigin.lab.medicine.umich.edu/news/near-death-experience | **LIVE; real Borjigin Lab near-death media/research page.** Earlier bare `scx2.b-cdn.net/...electricalsi.jpg` is not an acceptable canonical production URL. | Lab/news imagery has no explicit CC license. | Real-lab/research-context reference; useful for finding credited originals, not direct use. | `REPLACED_REFERENCE_ONLY` — remove old CDN dependency. |
| C05 | https://today.ucsd.edu/story/donation-fuels-research-on-dmt-and-its-potential-medical-use-to-address-mental-health-conditions | **LIVE; UC San Diego article explicitly identifies Jon Dean and shows his portrait.** | UCSD page is Regents-copyrighted; no open license for the portrait. Earlier `Dean-teaser.jpg` direct URL is replaced by this canonical source page. | First-author portrait/reference and present-day DMT research context. | `VERIFIED_REFERENCE_ONLY` — permission required. |
| C06 | https://www.imperial.ac.uk/news/243893/advanced-brain-imaging-study-hints-dmt/ | **LIVE; correct Christopher Timmermann / DMT imaging article.** | Imperial explicitly notes article photos/graphics may be Imperial or third-party copyright; no blanket CC permission. | Researcher identity / modern DMT program reference. | `VERIFIED_REFERENCE_ONLY` |
| C07 | https://www.imperial.ac.uk/news/193993/magic-mushrooms-create-hyperconnected-brain/ | **LIVE Imperial research article.** Earlier catalog used it as a possible Timmermann/participant visual source. | Article media rights are not open by default. | Reference-only laboratory/participant imagery; never imply it depicts Dean 2019 rat work. | `VERIFIED_REFERENCE_ONLY` |
| C08 | https://www.imperial.ac.uk/news/193993/magic-mushrooms-create-hyperconnected-brain/ | Same verified Imperial source; treatment-room/readout imagery may be useful visually. | Permission required unless a specific image credit grants reuse. | Reference for treatment-room / EEG aesthetic, not archive footage to use automatically. | `VERIFIED_REFERENCE_ONLY` |
| C09 | https://medschool.umich.edu/profile/4418/michael-m-wang | **LIVE; correct Michael M. Wang official profile.** | Institutional portrait reuse not licensed on page. | Optional Dean-2019 coauthor / dying-brain research identity. | `VERIFIED_REFERENCE_ONLY` |
| C10 | https://www.lsu.edu/vetmed/faculty/emeritus.php | **LIVE; current LSU emeritus page identifies Steven A. Barker.** Old `mvsvipa3.lsu.edu/...` URL is obsolete and replaced. | Identity/source only; no cleared production portrait located. | Barker-2013 historical-research context; use text citation unless a rights-cleared portrait is later located. | `REPLACED_SOURCE_ONLY` |

---

# D — Molecules, biosynthesis, microdialysis and method visuals

| ID | Verified source / download | Live-content verdict | Rights / technical verdict | Exact production use | Action |
|---|---|---|---|---|---|
| D01 | https://commons.wikimedia.org/wiki/File:DMT.svg | **LIVE; correct N,N-DMT structural formula.** | **Public domain.** | Clean molecule reveal at “Its full name is N,N-dimethyltryptamine.” | `VERIFIED_GREEN` |
| D02 | https://commons.wikimedia.org/wiki/File:Tryptamine.svg | **LIVE; correct tryptamine structural formula.** | **Public domain.** | Biosynthesis pathway component. | `VERIFIED_GREEN` — **replacement.** Earlier `Tryptamine_structure.svg` currently carries GPLv3 and is no longer our preferred asset. |
| D03 | https://commons.wikimedia.org/wiki/File:Tryptophan.svg | **LIVE; correct tryptophan structure.** | **CC0 1.0.** | Optional upstream pathway context. | `VERIFIED_GREEN` |
| D04 | https://commons.wikimedia.org/wiki/File:Serotonin_(5-HT).svg | **LIVE; correct serotonin structure.** | **Public domain/simple structural formula.** | Optional molecular-family comparison only. | `VERIFIED_GREEN` |
| D05 | https://commons.wikimedia.org/wiki/File:Sonda_para_microdi%C3%A1lisis_cerebral.svg | **LIVE; correct cerebral microdialysis probe schematic; SVG 1000×834.** | **CC BY-SA 4.0.** | Explain “tiny chemical sampling window” before Dean’s result reveal. | `VERIFIED_GREEN` |
| D06 | https://pmc.ncbi.nlm.nih.gov/articles/PMC2492659/ | Correct Borjigin & Liu 2008 long-term microdialysis methods paper. | PMC availability alone does **not** establish open reuse of its figures. | Method-history reference and reconstruction guidance. | `VERIFIED_SOURCE_ONLY` |
| D07 | D06 Figure 1 | Correct pineal/circadian method figure in source paper. | Figure reuse not cleared. | Reference for pineal physiology layout. | `VERIFIED_REFERENCE_ONLY` |
| D08 | D06 Figure 2 | Correct microdialysis-probe construction figure in source paper. | Figure reuse not cleared. | Technical reference for a clean editor-created microdialysis graphic. | `VERIFIED_REFERENCE_ONLY` |
| D09 | D06 Figure 3 | Correct probe-implantation/method figure in source paper. | Figure reuse not cleared. | Procedure reference; no surgical spectacle. | `VERIFIED_REFERENCE_ONLY` |
| D10 | https://pubmed.ncbi.nlm.nih.gov/23881860/ | **LIVE; correct Barker, Borjigin, Lomnicka & Strassman 2013 paper** on endogenous DMT-related compounds in rat pineal-gland microdialysate. | Wiley copyright; full-paper figures are not cleared for reuse. | Important scientific prehistory showing why the pineal/DMT question was experimentally plausible. | `VERIFIED_SOURCE_ONLY` |

---

# E — Pineal anatomy / Descartes / historical science

| ID | Verified source / download | Live-content verdict | Rights / technical verdict | Exact production use | Action |
|---|---|---|---|---|---|
| E01 | https://commons.wikimedia.org/wiki/File:The_Pineal_Gland_Infographic.png | **LIVE; correct modern pineal anatomy infographic; 2000×1414.** | **CC0.** | Quick anatomical orientation before returning to the experiment. | `VERIFIED_GREEN` |
| E02 | https://commons.wikimedia.org/wiki/File:Descartes_diagram.png | **LIVE; correct historical Descartes nervous-system/pineal diagram.** | **Public domain.** | Series callback to “the gland Descartes placed near the soul.” | `VERIFIED_GREEN` |
| E03 | https://commons.wikimedia.org/wiki/File:Descartes;_The_Nervous_System._Diagram_of_the_brain_Wellcome_L0006584.jpg | **LIVE; correct Wellcome Descartes brain/nervous-system scan; original 5787×3018.** | **CC BY 4.0.** | High-resolution historical document reveal / slow push-in. | `VERIFIED_GREEN` |
| E04 | https://www.cancer.gov/publications/dictionaries/cancer-terms/def/pineal-body | **LIVE; correct NCI definition of pineal body, but no unique reusable anatomical illustration is exposed as the asset originally assumed.** | NCI text is reusable subject to policy; graphics require item-specific credit/right checks. | Text/anatomy fact-check source, **not a primary picture asset**. | `REPLACED_SOURCE_ONLY` — remove “NCI anatomical illustration” from acquisition queue. |
| E05 | https://commons.wikimedia.org/wiki/File:Frans_Hals,_Portrait_of_Ren%C3%A9_Descartes.jpg | **LIVE; correct René Descartes portrait; original 2178×2958.** | **Public domain / PD-Art reproduction.** | Humanize the historical callback before showing his anatomical diagram. | `VERIFIED_GREEN` — **new portrait.** |

---

# F — Esoteric / third-eye / Theosophical visual genealogy

| ID | Verified source / download | Live-content verdict | Rights / technical verdict | Exact production use | Action |
|---|---|---|---|---|---|
| F01 | https://commons.wikimedia.org/wiki/File:Oriental_MS_Indic_beta_511_Wellcome_L0029118.jpg | **LIVE; correct Wellcome tantric-body manuscript image; original 2950×3755.** | **CC BY 4.0.** | Premium historical esoteric anchor: chakras/nadi/kundalini; distinguish belief-system document from anatomy. | `VERIFIED_GREEN` |
| F02 | https://commons.wikimedia.org/wiki/File:Leadbeater%27s_Chakras_Pictures.JPG | **LIVE; correct Leadbeater 1927 chakra plate set; original 1700×2200.** | **Public domain per Commons record; preserve PD rationale.** | Theosophical visual genealogy / callback to earlier “third eye” episode. | `VERIFIED_GREEN` |
| F03 | https://commons.wikimedia.org/wiki/File:Nervous_plexi.jpg | **LIVE; correct Leadbeater “nervous plexi” mapping; original 760×1014.** | **Public domain.** | Visually show esoteric anatomy being mapped onto the body. | `VERIFIED_GREEN` |
| F04 | https://commons.wikimedia.org/wiki/File:Chakracrown.jpg | **LIVE; correct Leadbeater crown-chakra plate; 793×915.** | **Public domain.** | Head/vision symbolic beat. | `VERIFIED_GREEN` |
| F05 | https://commons.wikimedia.org/wiki/File:Chakraroot.jpg | **LIVE; correct Leadbeater root-chakra plate; 732×864.** | **Public domain.** | Optional comparative insert to show a whole system rather than cherry-picking only Ajna. | `VERIFIED_GREEN` |
| F06 | https://commons.wikimedia.org/wiki/File:Chakra6.svg | **LIVE; correct Ajna symbol; SVG ~770×700.** | **CC0 1.0.** | Clean iconographic third-eye insert. | `VERIFIED_GREEN` |
| F07 | https://commons.wikimedia.org/wiki/File:Eye_of_Providence_(icon,_19th_c.).jpg | **LIVE; correct 19th-century Eye of Providence icon; ~472×650.** | **Public domain.** | Optional broader “seeing eye” cultural motif. **No direct lineage to pineal/DMT should be implied.** | `VERIFIED_GREEN` |
| F08 | https://commons.wikimedia.org/wiki/File:Charles_Webster_Leadbeater.005.jpg | **LIVE; correct Charles Webster Leadbeater portrait; original 833×511.** | **Public-domain mark; Commons notes historical PD basis.** | Put a real face on the Theosophical genealogy before his chakra plates. | `VERIFIED_GREEN` — **new portrait.** |
| F09 | https://commons.wikimedia.org/wiki/File:Portret_van_Helena_Blavatsky,_RP-F-2001-7-67-105.jpg | **LIVE; correct Helena Blavatsky portrait; Rijksmuseum source; original 3484×4708, 2.15 MB.** | **CC0 1.0.** | Optional Theosophical founder portrait / wider occult genealogy. | `VERIFIED_GREEN` — **new high-resolution portrait.** |

---

# G — Strassman hypothesis / book-context sources

| ID | Verified source | Live-content verdict | Rights verdict | Exact production use | Action |
|---|---|---|---|---|---|
| G01 | https://www.rickstrassman.com/ | **LIVE official Rick Strassman site.** | Website content is not assumed freely reproducible as imagery. | Identity/bibliographic source; route to primary-author material. | `VERIFIED_SOURCE_ONLY` |
| G02 | https://www.rickstrassman.com/publications/the-spirit-molecule/chapter-summaries/ | **LIVE official author page and now the preferred primary attribution source.** It explicitly states that he considered the pineal a likely endogenous-DMT source and that he **speculated** about DMT roles in dreams, meditation, birth, near-death and death. | Use as research/source evidence; do not reproduce large blocks of website/book text on screen without permission. | Replaces vague secondary attribution and eliminates the need for an unauthorized book scan. Editor may build a clean citation card with author/title/URL and a very short fair-use quotation if desired. | `VERIFIED_SOURCE_ONLY` — **resolves former G02 “source text pending”.** |
| G03 | https://www.rickstrassman.com/why-wont-dmt-go-away/ | **LIVE official author essay.** Useful because Strassman distinguishes evidence, hypothesis and speculation around endogenous DMT. | Source-only unless explicit web-content permission is obtained. | Nuanced attribution/boundary support. | `VERIFIED_SOURCE_ONLY` — **new source.** |

---

# Replacements / removals caused by this verification pass

1. **Dean direct `media.springernature.com` figure URLs:** do not use as canonical acquisition URLs. The verified Nature PDF is the canonical master; extract Figures 1–4 from it. The figures/content and CC BY license are verified in the PDF/article.
2. **`Tryptamine_structure.svg`:** replace with `https://commons.wikimedia.org/wiki/File:Tryptamine.svg`. The former file currently carries GPLv3 due to derivative history; the replacement is explicitly public domain.
3. **Robin Carhart-Harris cropped portrait:** prefer the full Commons meeting image; it retains more context and the same CC BY-SA provenance.
4. **Old Borjigin/Mashour CDN image (`scx2.b-cdn.net/...electricalsi.jpg`):** remove from production-download queue. Use the official Borjigin Lab source pages as research/reference and clear any specific photo separately.
5. **Old Jon Dean direct `Dean-teaser.jpg`:** remove as canonical URL. Use the verified UCSD Today story as the identity/source page; portrait remains permission-only.
6. **Old LSU `mvsvipa3.lsu.edu` URL:** replace with current `https://www.lsu.edu/vetmed/faculty/emeritus.php`.
7. **NCI “pineal illustration”:** no standalone reusable picture verified on the cited definition page. Keep NCI as an anatomy text source only.
8. **Commercial Strassman book scan/cover:** unnecessary for the key hypothesis attribution because the author’s official chapter-summary page explicitly states the speculation. Keep book scans out unless rights are separately cleared.

# Production recommendation

The strongest evidence-led visual sequence now has enough genuine assets to avoid generic AI for most of the episode:

1. **Dean paper title → Figure 1 → microdialysis schematic → Figure 4.**
2. **Strassman portrait + official hypothesis citation** as historical attribution, not scientific confirmation.
3. **DMT structure + real human DMT EEG/fMRI figures** to show what administered DMT actually does in measured human experiments.
4. **Timmermann 2018 paper/table** for DMT/NDE phenomenological overlap.
5. **Human near-death EEG figures** as a separate terminal-brain measurement track, visibly labelled “EEG — not DMT measurement.”
6. **Descartes portrait/diagram + Wellcome tantra + Leadbeater/Blavatsky imagery** for the cultural projection/history layer.
7. Generated reconstructions only for transitions, experiential imagery and procedure visualization where no truthful archive frame exists.

# Codex acquisition gate

Codex may automatically download only rows marked `VERIFIED_GREEN` / `VERIFIED_GREEN_EXTRACT` in this report or the synchronized manifest. `SOURCE_ONLY` and `REFERENCE_ONLY` assets must stay outside the approved production-originals folder. For every approved asset Codex must still capture the source page, exact license, creator/credit, original dimensions, SHA-256 and a rights snapshot before changing status to `QA_PASS`.
