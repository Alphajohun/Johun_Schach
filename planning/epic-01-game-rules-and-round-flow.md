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
- Eigene Figuren bleiben grundsätzlich nicht schlagbar
- Validierung und UI-Meldung sind synchron

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

