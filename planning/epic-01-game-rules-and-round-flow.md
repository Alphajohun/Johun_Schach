# Epic 01 - Spielregeln und Rundenfluss

## Ziel

Das Spiel soll ein konsistentes und nachvollziehbares Regelwerk erhalten, damit Spielzüge eindeutig validiert werden und eine Runde zuverlässig beendet werden kann.

## Scope

- Figurenregeln präzisieren und vereinheitlichen
- Rundengewinn und Rundenerkennung einführen
- Turn- und Fehlerfeedback robuster machen

## Out of Scope

- Persistente Speicherung von Matches
- Matchmaking über mehrere Spiele gleichzeitig

## Stories

### Story 01.01 - Einheitliche Schlagregeln für alle Figurtypen

**Beschreibung**  
Als Spieler möchte ich, dass Schlagregeln zwischen Dreiecken und Türmen konsistent sind, damit keine unerwarteten Sonderfälle auftreten.

**Aktueller Bezug**  
Dokumentiert in [`documentation/spielstand-fuer-coding-agent.md`](documentation/spielstand-fuer-coding-agent.md:72).

**Acceptance Criteria**

- Dreiecke können gegnerische Figurtypen entsprechend definierter Regel schlagen
- Eigene Figuren bleiben grundsätzlich nicht schlagbar - man kann eigene Figuren nicht schlagen
- Validierung und UI-Meldung sind synchron

Dreiecke heissen ab sofort bauern
Bauern können diagonal schlagen - ein feld in ihre laufrichtung
Türme können horizontal und vertikal Figuren schlagen, die nicht durch andere figuren in der sichtlinie verdeckt sind
figuren können natürlich nur gegnerische figuren schlagen  - das Feld muss besetzt sein
wenn eine Figur angewählt ist und eine gegnerische Figur ausgewählt wird,dann gucken,ob es in der sichtweite der figutr ist und wenn alle schlagbedingungen erfüllt sind,figur schlagen



### Story 01.02 - Explizite Rundengewinn-Bedingung

**Beschreibung**  
Als Spieler möchte ich, dass eine Runde automatisch endet, wenn ein klar definierter Siegfall eintritt.

**Aktueller Bezug**  
Aktuell nur manuelle Aufgabe über [`/reset_round`](backend/app.py:567).

**Acceptance Criteria**

- Es existiert mindestens eine automatische Rundengewinn-Regel
- Bei Rundengewinn wird Score korrekt aktualisiert
- Nach Rundengewinn startet die nächste Runde in sauberem Ausgangszustand

### Story 01.03 - Legale-Züge-Hinweise im Frontend

**Beschreibung**  
Als Spieler möchte ich mögliche Ziel-Felder sichtbar machen, damit Fehlklicks und ungültige Züge reduziert werden.

**Aktueller Bezug**  
Zugauswahl in [`frontend/src/main.jsx`](frontend/src/main.jsx:263).

**Acceptance Criteria**

- Nach Figur-Auswahl werden legale Ziel-Felder visuell markiert
- Klick auf illegales Feld gibt verständliche Meldung
- Markierungen verschwinden nach Zug oder Abwahl zuverlässig

### Story 01.04 - Konsistente Turn-Fehlermeldungen

**Beschreibung**  
Als Spieler möchte ich bei ungültigen Turn-Aktionen eine einheitliche und klare Rückmeldung bekommen.

**Aktueller Bezug**  
Turn-Validierung in [`move()`](backend/app.py:362).

**Acceptance Criteria**

- Alle Turn-Verstöße verwenden ein standardisiertes Fehlermuster
- Frontend zeigt Turn-Fehler priorisiert und ohne widersprüchliche Texte
- API liefert maschinenlesbaren Fehlercode zusätzlich zur Message

### Story 01.05 - Neue Figur "Pferd" mit L-Zug und Sprungregel

**Beschreibung**  
Als Spieler möchte ich eine neue Figur "Pferd" nutzen, die sich im L-Muster bewegt und über andere Figuren springen kann, damit das Spiel taktisch vielfältiger wird.

**Aktueller Bezug**  
Regel- und Zuglogik liegen zentral in [`move()`](backend/app.py:328) sowie in der Regelübersicht in [`documentation/spielstand-fuer-coding-agent.md`](documentation/spielstand-fuer-coding-agent.md:86).

**Acceptance Criteria**

- Pro Farbe gibt es zwei Pferde auf den Startfeldern wie im Schach:
  - Weiß: `b1` und `g1` (Koordinaten `x=1,y=7` und `x=6,y=7`)
  - Schwarz: `b8` und `g8` (Koordinaten `x=1,y=0` und `x=6,y=0`)
- Ein Pferd darf genau im L-Muster ziehen:
  - entweder `2` Felder horizontal + `1` Feld vertikal
  - oder `2` Felder vertikal + `1` Feld horizontal
- Das Pferd darf über andere Figuren springen; Zwischenfelder blockieren den Zug nicht.
- Schlagen erfolgt ausschließlich auf dem Zielfeld (letztes Feld des L-Zugs).
- Pferde dürfen gegnerische Bauern, Türme und Pferde schlagen.
- Eigene Figuren auf dem Zielfeld blockieren den Zug; eigene Figuren sind nicht schlagbar.
- Ungültige Pferd-Züge liefern konsistente Fehlermeldungen in API und UI.

