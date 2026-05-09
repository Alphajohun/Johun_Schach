# Epic 03 - Architektur, API und Code-Qualität

## Ziel

Codebasis und API sollen so strukturiert werden, dass zukünftige Änderungen sicher, testbar und für weitere Coding-Agents schneller umsetzbar sind.

## Scope

- API-Verträge stabilisieren
- Backend-Struktur von globalem Zustand in klarere Module überführen
- Testbarkeit und Observability verbessern

## Out of Scope

- Komplett neuer Tech-Stack
- Deployment-Automation außerhalb der lokalen Startskripte

## Stories

### Story 03.01 - API-Response-Schema standardisieren

**Beschreibung**  
Als Entwickler möchte ich ein einheitliches API-Schema mit Fehlercodes, damit Frontend und Tests robust gegen Änderungen bleiben.

**Aktueller Bezug**  
Endpoints in [`backend/app.py`](backend/app.py:246) und Referenz in [`documentation/spielstand-fuer-coding-agent.md`](documentation/spielstand-fuer-coding-agent.md:160).

**Acceptance Criteria**

- Jeder Endpunkt liefert konsistente Top-Level-Felder
- Fehlerantworten enthalten maschinenlesbaren Code
- API-Referenz wird nach Schema-Änderungen aktualisiert

### Story 03.02 - Backend-Logik in Domänenmodule trennen

**Beschreibung**  
Als Entwickler möchte ich getrennte Verantwortlichkeiten für Session, Regeln und State-Manipulation, damit Änderungen weniger Seiteneffekte erzeugen.

**Aktueller Bezug**  
Monolithische Logik in [`move()`](backend/app.py:328) und Hilfsfunktionen in [`backend/app.py`](backend/app.py:47).

**Acceptance Criteria**

- Sessionlogik ist getrennt von Zugvalidierung
- Figurenlogik ist pro Figurtyp gekapselt
- Endpunktfunktionen enthalten primär Orchestrierung

### Story 03.03 - Automatisierte Tests für Kernregeln einführen

**Beschreibung**  
Als Team möchte ich automatisierte Regressionstests für Spielregeln und Sessionfälle, damit Refactorings sicher möglich sind.

**Aktueller Bezug**  
Derzeit kein Test-Setup in [`backend`](backend) oder [`frontend`](frontend).

**Acceptance Criteria**

- Kernfälle für Dreiecke, Türme, Turn und Reset sind automatisiert getestet
- Mindestens ein End-to-End-ähnlicher API-Flow ist abgedeckt
- Testausführung lokal dokumentiert

### Story 03.04 - Logging und Debug-Ausgaben vereinheitlichen

**Beschreibung**  
Als Entwickler möchte ich strukturierte Logs statt verstreuter Debug-Prints, damit Fehleranalyse reproduzierbar wird.

**Aktueller Bezug**  
Backend-Debug-Prints in [`backend/app.py`](backend/app.py:225) und Frontend-Debug-Logs in [`frontend/src/main.jsx`](frontend/src/main.jsx:271).

**Acceptance Criteria**

- Logging-Level sind klar definiert
- Entwicklungs-Debugging ist aktivierbar ohne Codeänderung
- Produktive Logausgaben enthalten nur relevante Informationen

