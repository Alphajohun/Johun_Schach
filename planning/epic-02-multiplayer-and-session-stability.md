# Epic 02 - Multiplayer und Session-Stabilität

## Ziel

Mehrspieler-Sitzungen sollen stabil laufen, Rollenwechsel sauber funktionieren und Verbindungsabbrüche robust abgefangen werden.

## Scope

- Rollenvergabe und Rejoin-Verhalten verbessern
- Timeout- und Heartbeat-Strategie konsolidieren
- Zuschauerverhalten klar definieren

## Out of Scope

- Externe Auth-Provider
- Persistente User-Accounts

## Stories

### Story 02.01 - Deterministisches Rejoin für aktive Spieler

**Beschreibung**  
Als Spieler möchte ich nach kurzem Verbindungsabbruch meine Rolle zuverlässig zurückbekommen, damit ich laufende Partien fortsetzen kann.

**Aktueller Bezug**  
Join-Logik in [`join()`](backend/app.py:246), Timeout-Logik in [`cleanup_disconnected_players()`](backend/app.py:60).

**Acceptance Criteria**

- Rejoin innerhalb definierter Frist stellt vorherige Rolle wieder her
- Gegenspieler bleibt während Rejoin-Fenster aktiv im Match
- UI informiert klar über Rejoin-Status

### Story 02.02 - Heartbeat-Intervall und Timeout harmonisieren

**Beschreibung**  
Als Entwickler möchte ich abgestimmte Heartbeat- und Timeout-Werte, damit unnötige Session-Resets reduziert werden.

**Aktueller Bezug**  
Frontend-Polling in [`setInterval(pollState, 80)`](frontend/src/main.jsx:93), Timeout-Konstante in [`PLAYER_TIMEOUT_SECONDS`](backend/app.py:44).

**Acceptance Criteria**

- Heartbeat-Rate ist konfigurierbar
- Timeout ist zentral konfigurierbar und dokumentiert
- Unerwartete Auto-Resets bei kurzzeitigen Latenzen werden messbar reduziert

### Story 02.03 - Zuschauer-Lebenszyklus konsistent machen

**Beschreibung**  
Als Zuschauer möchte ich klar erkennen, wann ich nur beobachte und wann ich aktiv eine Rolle anfragen kann.

**Aktueller Bezug**  
Rollen-UI in [`if (!hasJoined)`](frontend/src/main.jsx:434) und Zugblockade in [`onClick={async () => { ... }}`](frontend/src/main.jsx:263).

**Acceptance Criteria**

- Zuschauerstatus ist dauerhaft sichtbar
- Wechsel von Zuschauer zu Spieler erfolgt ohne Seitenreload
- Fehlversuche als Zuschauer werden einheitlich kommuniziert

### Story 02.04 - Leave-Handling vereinfachen und absichern

**Beschreibung**  
Als Entwickler möchte ich eine robuste und wartbare Leave-Strategie, damit Session-Enden zuverlässig erkannt werden.

**Aktueller Bezug**  
Browser-Leave-Fallbacks in [`leaveGame`](frontend/src/main.jsx:111), Endpunkte [`leave()`](backend/app.py:298) und [`leave_get()`](backend/app.py:316).

**Acceptance Criteria**

- Ein klar definierter primärer Leave-Pfad existiert
- Fallback-Verhalten ist dokumentiert und getestet
- Keine doppelten Nebenwirkungen bei parallelen Leave-Requests

