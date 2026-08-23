# EP01 – Kozyrev Mirrors – Native ImageGen References

**Status:** Fertig generiert und visuell geprüft. Diese Dateien sind keine weiteren Generierungsaufträge, sondern die verbindlichen Referenzen für `NANOBANANA_PROMPTS.md`.

**Ordner:** `05_GENERATED/EP01_KOZYREV/STYLE_REFERENCES/`

## Einsatzlogik

- Pro Zielbild nur die in dessen `Referenz:`-Zeile genannten Dateien hochladen.
- Eine Stilreferenz steuert Bildsprache und Kontinuität; eine zusätzliche Sachreferenz nur Identität, Geometrie, Epoche, Objekt oder Ort.
- Porträts werden nur bei erkennbaren Darstellungen der jeweiligen Person verwendet.
- Fantastische Motive benötigen keine Personenreferenz. Für die Serienkohärenz nutzen sie `REF_EP01_CONCEPTUAL_TIME.png`.
- Sichtbarer Bildtext ist ausschließlich Englisch.

## Fertige Referenzen

### REF_EP01_KOZYREV_IDENTITY.png

**Rolle:** Wiedererkennbare Darstellung von Nikolai Kozyrev in Szenen der 1950er/1960er Jahre.

**Ausgangsreferenz:** `KZ_001_Nikolai_Kozyrev_1959.png`

**Finaler ImageGen-Prompt:**

Create a premium photorealistic 16:9 investigative-documentary reconstruction of Soviet astronomer Nikolai Kozyrev in a late-1950s observatory. Preserve the recognizable facial identity, hairline and age from the uploaded authentic portrait. Show him beside a large period-correct telescope, thoughtful and alert, wearing a modest dark Soviet suit and shirt. Deep blue-black and graphite shadows, warm tungsten practical light, restrained cyan night light, realistic optics, tactile period materials, subtle film grain and controlled negative space. No mirror apparatus, paranormal effect, modern equipment, logo, watermark or visible text.

### REF_EP01_KAZNACHEEV_IDENTITY.png

**Rolle:** Wiedererkennbare Darstellung von Vlail Kaznacheev in den späteren 1990er-Jahre-Szenen.

**Ausgangsreferenz:** `KZ_REF_Kaznacheev_portrait.jpg`

**Finaler ImageGen-Prompt:**

Create a premium photorealistic 16:9 investigative-documentary portrait reconstruction of Russian scientist Vlail Kaznacheev in a modest mid-1990s research office. Preserve the recognizable facial identity, age and hair from the uploaded portrait while replacing ceremonial clothing with a plain dark suit, shirt and tie appropriate to a working scientist. Quietly intense expression, papers and period laboratory details in soft focus, deep graphite shadows, warm tungsten practical light, restrained cyan accent, realistic skin and hands, subtle film grain. No medals, bow tie, paranormal effect, modern electronics, logo, watermark or visible text.

### REF_EP01_APPARATUS_MASTER.png

**Rolle:** Verbindliche Geometrie, Maßstab und Materialität der Spiegelapparatur.

**Ausgangsreferenzen:** `KZ_002_Kozyrev_mirror_apparatus_drawing_1996.jpg` sowie die beste bereits erzeugte technische Variante von `IMG01`.

**Finaler ImageGen-Prompt:**

Create a physically plausible premium 16:9 engineering-documentary reconstruction of the later so-called Kozyrev mirror apparatus. Use the uploaded technical drawing as the authority for geometry: several tall polished aluminum plates form an open spiral or partial cylinder around a simple seated position, with a visible opening, realistic steel supports, fasteners and circular base. Show one anonymous adult nearby only for scale, not experiencing an effect. Modest 1990s Russian research room, deep blue-black and graphite shadows, warm tungsten practical light, restrained cyan reflections, realistic metal optics, subtle film grain. No magical glow, sealed sci-fi capsule, impossible machinery, logo, watermark or visible text.

### REF_EP01_CINEMATIC_LAB.png

**Rolle:** Farbwelt, Licht, Kamera und Laboratmosphäre für realistische Rekonstruktionen.

**Ausgangsreferenzen:** `REF_EP01_KAZNACHEEV_IDENTITY.png` und `REF_EP01_APPARATUS_MASTER.png`

**Finaler ImageGen-Prompt:**

Create a premium photorealistic 16:9 investigative-documentary master frame in a modest mid-1990s Russian laboratory. Show Vlail Kaznacheev, matching the uploaded portrait reference, standing with two anonymous technicians beside the physically plausible open polished-aluminum spiral apparatus from the uploaded apparatus reference. They inspect notes and hardware; nobody is posing. Deep blue-black and graphite shadows, warm tungsten practical lamps, restrained cyan metal reflections, realistic period equipment, tactile surfaces, subtle 35mm film grain, strong depth and clean negative space. No paranormal effect, modern screens, occult props, logo, watermark or visible text.

### REF_EP01_CONCEPTUAL_TIME.png

**Rolle:** Kontrollierte Fantastik für Zeit-, Informations- und Fernwahrnehmungsmotive.

**Ausgangsreferenzen:** `REF_EP01_KOZYREV_IDENTITY.png` und eine kuratierte Mondreferenz.

**Finaler ImageGen-Prompt:**

Create a premium 16:9 conceptual investigative-documentary image. Preserve Nikolai Kozyrev's recognizable identity from the uploaded portrait and place him in a dark observatory whose architecture transitions seamlessly into a restrained lunar landscape. Visualize time as elegant translucent contour currents and delayed light paths bending through the scene, scientifically suggestive but explicitly symbolic. Deep blue-black and graphite palette, restrained cyan light, warm archival highlights, realistic optics, subtle film grain, one clear focal point and sophisticated spatial layering. Mysterious and dreamlike without occult clichés, cheap neon science fiction, logo, watermark or visible text.

### REF_EP01_INFOGRAPHIC_MASTER.png

**Rolle:** Typografie, Hierarchie, Linienführung und Beweisstatus für alle Erklärgrafiken.

**Finaler ImageGen-Prompt:**

Create a premium 16:9 broadcast infographic for an investigative documentary titled “KOZYREV MIRROR: THEORY, DEVICE, TEST”. On a deep blue-black background with warm paper-white geometry and restrained cyan accents, show a historically clear chain: “1 TIME THEORY” with Kozyrev at left, then a separate node “LATER RESEARCHERS”, then “2 MIRROR APPARATUS”, then “3 VERIFIABLE TEST”. Add three small evidence-status labels: “DOCUMENTED”, “CLAIMED”, “OPEN”. Use precise spacing, clean connectors, a physically plausible open aluminum spiral and a simple test diagram. All visible text must be exactly the supplied English wording, correctly spelled and legible. No direct arrow implying Kozyrev built the later apparatus, no decorative clutter, logo or watermark.

### REF_EP01_DOUBLE_BLIND_TEST.png

**Rolle:** Gegenwärtige, neutrale Testumgebung für Doppelblind-, Randomisierungs-, Auswertungs- und Replikationsmotive. Sie verhindert, dass moderne Prüfszenen versehentlich wie das historische Kaznacheev-Labor aussehen.

**Ausgangsreferenzen:** `REF_EP01_CINEMATIC_LAB.png` ausschließlich für Bildsprache und `REF_EP01_APPARATUS_MASTER.png` für die Apparaturgeometrie.

**Finaler ImageGen-Prompt:**

Create a premium photorealistic 16:9 investigative-documentary reference frame for a contemporary rigorous double-blind test of claims associated with a Kozyrev-mirror-like apparatus. Preserve only the established color, lens, lighting, and plausible apparatus geometry from the two references; do not reproduce any recognizable person or 1990s period details. Show a modern neutral university test suite with three clearly separated functional zones visible in one coherent composition: an isolated adult participant seated inside the open polished-aluminum spiral apparatus, a researcher at a computer who cannot see the target assignment, and an independent scorer behind glass reviewing anonymous numbered results. Include realistic acoustic isolation, sealed target envelopes, a timestamp device, and clean ordinary laboratory materials. The mood is controlled, skeptical, precise, and tense rather than sterile. Deep blue-black and graphite shadows, warm practical light, restrained cyan technical accents, realistic optics, subtle film grain, strong depth and clean negative space. No paranormal glow, no outcome implied, no celebrity likeness, no logos, no watermark. Avoid readable text except the short English labels “PARTICIPANT”, “BLIND TARGET”, and “INDEPENDENT SCORE”, correctly spelled and clearly legible.

## Historische Trennung

Die Infografik enthält bewusst den Zwischenschritt **LATER RESEARCHERS**. So wird visuell nicht behauptet, Kozyrev selbst habe die später patentierte Spiegelapparatur gebaut. Das schützt die Folge vor einer leicht angreifbaren Verkürzung, ohne die Dramaturgie abzuschwächen.

