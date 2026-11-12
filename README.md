# FreeCAD Carry – Lernplattform (Kurs)

**Kursübersicht:** <https://danielgloeckler.github.io/freecad-carry/>  
**Kapitel 1 – Chassi:** <https://danielgloeckler.github.io/freecad-carry/chassi.html>  
**Rad:** <https://danielgloeckler.github.io/freecad-carry/rad.html>  
**Radlager:** <https://danielgloeckler.github.io/freecad-carry/lager.html>  
**Achse & Schrauben:** <https://danielgloeckler.github.io/freecad-carry/achse.html>  
**Baugruppe:** <https://danielgloeckler.github.io/freecad-carry/baugruppe.html>  
**Originalseiten (PDF):** <https://danielgloeckler.github.io/freecad-carry/original.html>

Aufbau wie eine Lernplattform: **Kursstartseite** mit Fortschritt und fünf
**Kapitel** als Abschnitte. Die Kapitel 2–5 bleiben Schritt-für-Schritt-Trainer
mit einer **Lupe** auf dem Klickpunkt. **Kapitel 1 (Chassi)** ist jetzt eine
PDF-artige Anleitung mit **drei Hilfestufen**.

Über den Button **Kapitel** (oder die Taste **K**) öffnet sich auf jeder Seite
eine kompakte Übersicht mit Bild des fertigen Carry – von dort lässt sich
direkt in jedes Kapitel wechseln. Die Originalseiten aus „FreeCAD Anleitung II“
bleiben als Leseausgabe erhalten.

## Kapitel 1 – Chassi (PDF-Stil, 3 Hilfestufen)

Neues Chassi → Skizze/Rechteck → Symmetrie → **116 × 70 mm** → 5 mm
aufpolstern → Platte → **ein** Kreis R1,5 (10 mm von links, 5 mm von oben) →
Tasche „durch alles“ → **Mehrfach-Transformation mit zwei linearen Mustern**
(9 × 96 mm und 5 × 60 mm) → 45 Löcher → **8 Schraubenlöcher** senken
(1,5 mm) → rot → speichern.

Die Seite bietet oben einen Umschalter **Wenig / Mittel / Viel**:

- **Wenig:** Ziel und Kurzfassung, ohne Einzelklicks.
- **Mittel:** die wichtigsten Schritte mit Bildern (wie die PDF).
- **Viel:** jeder einzelne Klick mit Ausschnitt, Inline-Symbol, **Statusbild**
  („So sollte es aussehen“) und aufklappbaren **„Mehr erklären“**-Hinweisen.

Die Screenshots wurden mit **FreeCAD 1.1** (dunkles Theme) neu erzeugt:
`tools/chassi_guide_shots.py`. Das Skript baut das Modell, öffnet die Dialoge
und speichert die Ausschnitte unter `assets/chassi/`.

## Kapitel 2 – Rad (PDF-Stil, 3 Hilfestufen)

Profil auf XZ mit **Nut R1,75** und den Maßen **5 / 17,5 / 2 / 1 mm** →
**360° rotieren** → Radkörper → **Achsbohrung Ø8** → **Loch Ø5 bei 10 mm** →
**polares Muster 360° / 6 Vorkommen** → grün → **Gummiring R1,75 bei
18,5 mm** als zweiter Körper → fertig → speichern.

Die Seite bietet denselben Umschalter **Wenig / Mittel / Viel** wie Kapitel 1.
Die Screenshots wurden mit **FreeCAD 1.1** (dunkles Theme) erzeugt:
`tools/rad_guide_shots.py`.

## Kapitel 3 – Radlager (13 Schritte)

Bogenprofil auf XZ (40 × 25, Seiten 5, R10) → **symmetrisch 10 mm**
aufpolstern → Bohrung **Ø4,5** bei 15 mm → zwei **Ø3,5** bei ±12 mm →
Sechskant-Vertiefungen **12 mm** tief für die M3-Muttern → grau → speichern.

## Kapitel 4 – Achse & Schrauben (14 Schritte)

Zylinder **Ø4 × 104 mm** (PDF: 84 mm – unser Chassi ist 82 statt 62 mm breit)
→ Kanten **R1** abrunden → braun → speichern. Dann Arbeitsbereich
**Fasteners** installieren → **Senkkopfschraube ISO 7046 M3 × 20** mit Gewinde
→ **Sechskantmutter ISO 4035 M3** → alle Teile speichern.

## Kapitel 5 – Baugruppe (10 Schritte)

Alle Teile in einen Ordner → **A2plus** → Chassi einfügen (fest) → Radlager
über Kreis-Kanten ausrichten → Muttern und Schrauben → alle vier Radlager →
Achsen (Offset −7 mm) → Räder (1 mm Abstand) → fertig.

Hinweise zur Baugruppe: Die Kapitel 2–5 beziehen sich noch auf die frühere
Chassi-Variante mit 82 mm Breite (Achsen 104 mm). Für die neue Variante
**116 × 70 mm** müssen Achslänge und Radabstand später angepasst werden.
Die Schrauben verschwinden in den Senkungen des Chassis, die Muttern in den
Sechskant-Vertiefungen des Radlagers.

## Quelle

Das Carry-Projekt stammt aus **„FreeCAD Anleitung II – Fortgeschrittene
Konstruktionen und Baugruppen“** von **Jürgen Gräber** (2020). Die
Originalseiten sind für den NWT-Unterricht gedacht; Text und Bilder bleiben
Eigentum des Autors. Die Schritt-für-Schritt-Fassung mit den neuen Screenshots
ist eine eigene Umsetzung in FreeCAD 1.1.

