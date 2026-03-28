// Wir holen React, useState und useEffect.
import React, { useEffect, useState } from 'react'

// Damit sagen wir später: Zeige unsere App im Browser an.
import ReactDOM from 'react-dom/client'

const API_BASE = `http://${window.location.hostname}:8000`

function createOrGetClientId() {
  const key = 'schach_client_id'
  const existing = localStorage.getItem(key)
  if (existing) return existing

  const generated = (typeof crypto !== 'undefined' && crypto.randomUUID)
    ? crypto.randomUUID()
    : `${Date.now()}-${Math.random().toString(16).slice(2)}`

  localStorage.setItem(key, generated)
  return generated
}

// Das ist unsere Hauptfunktion für die ganze Seite.
function App() {

  // Positionen der Steine.
  const [weiss, setWeiss] = useState({ x: 3, y: 0 })
  const [schwarz, setSchwarz] = useState({ x: 3, y: 7 })

  // Auswahl: "white", "black" oder leer.
  const [auswahl, setAuswahl] = useState('')

  // Rolle vom Backend: white / black / spectator / loading.
  const [rolle, setRolle] = useState('loading')

  // Gewünschte Farbe für Join-Anfrage.
  const [wunschfarbe, setWunschfarbe] = useState('white')

  // Persistente Browser-ID für /join und /move.
  const [clientId, setClientId] = useState('')

  // Kurze Statusmeldung für Nutzer.
  const [meldung, setMeldung] = useState('Verbinde mit Server...')

  const joinWithPreference = async (id, preferredColor) => {
    try {
      const res = await fetch(
        `${API_BASE}/join?client_id=${encodeURIComponent(id)}&preferred_color=${encodeURIComponent(preferredColor)}`
      )
      const data = await res.json()

      setRolle(data.role)
      setWeiss(data.white)
      setSchwarz(data.black)

      const wanted = preferredColor === 'white' ? 'Weiß' : 'Schwarz'
      if (data.role === 'white') {
        if (data.assignment === 'preferred') {
          setMeldung(`Rolle vergeben: Weiß (Wunsch ${wanted} erfüllt).`)
        } else if (data.assignment === 'fallback') {
          setMeldung(`Wunsch ${wanted} war belegt. Du hast Weiß als Fallback bekommen.`)
        } else {
          setMeldung('Du bist Weiß. Du darfst nur den weißen Stein ziehen.')
        }
      }

      if (data.role === 'black') {
        if (data.assignment === 'preferred') {
          setMeldung(`Rolle vergeben: Schwarz (Wunsch ${wanted} erfüllt).`)
        } else if (data.assignment === 'fallback') {
          setMeldung(`Wunsch ${wanted} war belegt. Du hast Schwarz als Fallback bekommen.`)
        } else {
          setMeldung('Du bist Schwarz. Du darfst nur den schwarzen Stein ziehen.')
        }
      }

      if (data.role === 'spectator') {
        setMeldung('Beide Farben sind belegt. Du bist Zuschauer.')
      }
    } catch {
      setRolle('spectator')
      setMeldung('Backend nicht erreichbar. Bitte starte den Server auf Port 8000.')
    }
  }

  // Beim Start: client_id erstellen, Rolle holen und State-Sync starten.
  useEffect(() => {
    let mounted = true
    const id = createOrGetClientId()
    setClientId(id)

    const preferred = localStorage.getItem('schach_preferred_color') || 'white'
    setWunschfarbe(preferred)

    const join = async () => {
      await joinWithPreference(id, preferred)
    }

    const pollState = async () => {
      try {
        const res = await fetch(`${API_BASE}/state?t=${Date.now()}`, { cache: 'no-store' })
        const data = await res.json()
        if (!mounted) return
        setWeiss(data.white)
        setSchwarz(data.black)
      } catch {
        // polling-fehler still ignorieren, UI bleibt nutzbar
      }
    }

    join()
    const timer = setInterval(pollState, 10)

    return () => {
      mounted = false
      clearInterval(timer)
    }
  }, [])

  const requestRole = async (preferredColor) => {
    if (!clientId) return
    setAuswahl('')
    setWunschfarbe(preferredColor)
    localStorage.setItem('schach_preferred_color', preferredColor)
    await joinWithPreference(clientId, preferredColor)
  }

  const rollenText =
    rolle === 'white' ? 'Weiß' :
      rolle === 'black' ? 'Schwarz' :
        rolle === 'loading' ? 'Lade...' : 'Zuschauer'

  // In diese Liste legen wir später alle 64 Felder vom Brett.
  const felder = []

  // Äußere Schleife: geht durch alle Zeilen von 0 bis 7.
  for (let y = 0; y < 8; y++) {
    // Innere Schleife: geht durch alle Spalten von 0 bis 7.
    for (let x = 0; x < 8; x++) {
      // Feldfarbe.
      const farbe = (x + y) % 2 === 0 ? '#1900ff' : '#b300ff'

      // Was auf dem Feld angezeigt wird.
      let stein = null

      if (weiss.x === x && weiss.y === y) {
        stein = (
          <div
            style={{
              width: '30px',
              height: '30px',
              borderRadius: '50%',
              backgroundColor: 'white',
              border: auswahl === 'white' ? '4px solid red' : '2px solid gray'
            }}
          />
        )
      }

      if (schwarz.x === x && schwarz.y === y) {
        stein = (
          <div
            style={{
              width: '30px',
              height: '30px',
              borderRadius: '50%',
              backgroundColor: 'black',
              border: auswahl === 'black' ? '4px solid red' : '2px solid gray'
            }}
          />
        )
      }

      felder.push(
        <div
          key={x + '-' + y}
          onClick={async () => {
            // Klick auf weißen Stein
            if (weiss.x === x && weiss.y === y) {
              if (rolle !== 'white') {
                setAuswahl('')
                setMeldung('Du bist nicht Weiß und darfst den weißen Stein nicht auswählen.')
                return
              }
              setAuswahl('white')
              setMeldung('Weißer Stein ausgewählt.')
              return
            }

            // Klick auf schwarzen Stein
            if (schwarz.x === x && schwarz.y === y) {
              if (rolle !== 'black') {
                setAuswahl('')
                setMeldung('Du bist nicht Schwarz und darfst den schwarzen Stein nicht auswählen.')
                return
              }
              setAuswahl('black')
              setMeldung('Schwarzer Stein ausgewählt.')
              return
            }

            // Ohne Auswahl kein Zug.
            if (auswahl === '') return

            // Sicherheitscheck: Zuschauer darf nie ziehen.
            if (rolle === 'spectator' || rolle === 'loading') {
              setAuswahl('')
              setMeldung('Als Zuschauer darfst du keine Züge machen.')
              return
            }

            // Sicherheitscheck: Nur die eigene Farbe darf ziehen.
            if (auswahl !== rolle) {
              setAuswahl('')
              setMeldung('Du darfst nur Steine deiner eigenen Farbe bewegen.')
              return
            }

            // Zug ans Backend senden.
            try {
              const res = await fetch(`${API_BASE}/move`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                  client_id: clientId,
                  color: auswahl,
                  x,
                  y
                })
              })

              const data = await res.json()
              setWeiss(data.white)
              setSchwarz(data.black)
              setAuswahl('')
              setMeldung('Zug gesendet.')
            } catch {
              setMeldung('Zug konnte nicht gesendet werden. Prüfe Backend-Verbindung.')
            }
          }}
          style={{
            width: '60px',
            height: '60px',
            backgroundColor: farbe,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer'
          }}
        >
          {stein}
        </div>
      )
    }
  }

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: 'white',
        flexDirection: 'column',
        gap: '16px'
      }}
    >
      <button
        type="button"
        disabled
        style={{
          fontSize: '18px',
          padding: '10px 14px',
          borderRadius: '10px',
          border: '2px solid #333',
          backgroundColor: '#f4f4f4',
          color: '#111',
          fontWeight: 700,
          opacity: 1
        }}
      >
        Du bist: {rollenText}
      </button>

      <div style={{ display: 'flex', gap: '10px' }}>
        <button
          type="button"
          onClick={() => requestRole('white')}
          style={{
            padding: '8px 12px',
            borderRadius: '8px',
            border: wunschfarbe === 'white' ? '3px solid #d60000' : '2px solid #555',
            backgroundColor: '#ffffff',
            cursor: 'pointer',
            fontWeight: 700
          }}
        >
          Ich möchte Weiß
        </button>

        <button
          type="button"
          onClick={() => requestRole('black')}
          style={{
            padding: '8px 12px',
            borderRadius: '8px',
            border: wunschfarbe === 'black' ? '3px solid #d60000' : '2px solid #555',
            backgroundColor: '#111111',
            color: 'white',
            cursor: 'pointer',
            fontWeight: 700
          }}
        >
          Ich möchte Schwarz
        </button>
      </div>

      <div style={{ fontSize: '18px' }}>
        Auswahl: {auswahl === '' ? 'kein Stein ausgewaehlt' : auswahl}
      </div>

      <div style={{ fontSize: '16px', color: '#333' }}>{meldung}</div>

      <div style={{ fontSize: '12px', color: '#777' }}>Client: {clientId || '...'}</div>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(8, 60px)',
          border: '4px solid #ff0000'
        }}
      >
        {felder}
      </div>
    </div>
  )
}

// Hier sagen wir: App im Element mit id="root" anzeigen.
ReactDOM.createRoot(document.getElementById('root')).render(<App />)
