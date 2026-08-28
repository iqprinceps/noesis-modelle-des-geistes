# Adaptiver Standard für Dokument-Evidenzbilder

Dieser Standard gilt projektübergreifend für echte Dokumente, Patente, Briefe,
Akten und Paper. Er erzwingt weder Dokumentbilder noch eine feste Zahl davon.
Wenn ein Dokument als Beleg gezeigt wird, muss das Zuschauerbild jedoch genau
die Aussage sichtbar machen, die die Voice in diesem Moment nennt.

## Fundstelle statt Dekoration

- Die gesprochene Schlüsselphrase wird im Originaldokument gesucht. Eine
  beliebige gelbe Linie oder ein nur ungefähr passender Seitenausschnitt gilt
  nicht als Hervorhebung.
- Die echte Fundstelle wird direkt markiert. Bei „Monroe called it Hemi-Sync“
  muss deshalb `Gateway and Hemi-Sync` beziehungsweise die tatsächlich zitierte
  Hemi-Sync-Stelle lesbar und sichtbar hervorgehoben sein.
- Kann die Phrase nicht zuverlässig gefunden werden, stoppt die Asseterzeugung.
  Sie darf nicht stillschweigend durch irgendeinen Ausschnitt derselben Seite
  ersetzt werden.

## Vollständiger relevanter Text

- Der vollständige relevante Absatz oder Textblock bleibt sichtbar. Zeilen
  dürfen weder rechts/links noch oben/unten mitten im Satz abgeschnitten sein.
- Der Ausschnitt bewahrt die volle Textspaltenbreite. Engere Detailcrops sind nur
  zulässig, wenn nachweislich keine Satzfortsetzung außerhalb liegt.
- Seitenkontext und vergrößerte Fundstelle dürfen gemeinsam gezeigt werden. Die
  Vergrößerung dient der Lesbarkeit, nicht einer dramatischeren Behauptung.
- Hervorhebungen bleiben transparent, verdecken keine Buchstaben und markieren
  nur Text, der im Original tatsächlich vorhanden ist.

## Bewegung und Lesbarkeit

- Dokument-, Karten- und andere Leseeinstellungen werden im finalen Render nicht
  durch Pan/Zoom beschnitten. Eine ruhige Einstellung ist hier oft stärker als
  eine künstliche Kamerafahrt.
- Filmische Stills dürfen sich bewegen, sofern die Fahrt subpixelgenau, weich
  ein- und ausläuft und keine relevanten Bildinformationen aus dem sicheren
  Bereich schiebt.
- Frameraten werden ohne sichtbare Kadenzsprünge vereinheitlicht; 24-fps-Clips
  dürfen nicht durch einfache 24→30-Duplizierung ruckeln.

## Abnahme je Dokumentbild

1. Passt die sichtbare Originalseite zur Voice-Aussage?
2. Ist die tatsächlich genannte Phrase gefunden und korrekt hervorgehoben?
3. Ist der vollständige relevante Absatz lesbar, ohne abgeschnittene Zeilen?
4. Bleiben Dokumenttitel, Datum, Autor oder Institution sichtbar, wenn sie für
   die Aussage relevant sind?
5. Erzeugt die Montage keine stärkere Behauptung als das Original?
6. Bleibt die Fundstelle auch im finalen Render und auf kleiner Wiedergabegröße
   erkennbar?

Die wiederverwendbare Referenzimplementierung liegt unter
`tools/document_evidence_renderer.py`. Episodenspezifische Builder sollen diese
Logik verwenden oder dieselben Prüfungen nachweisbar erfüllen.
