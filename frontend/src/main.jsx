import React, { useEffect, useState } from 'react'
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

function App() {
  const [trianglesBlack, setTrianglesBlack] = useState([])
  const [trianglesWhite, setTrianglesWhite] = useState([])
  const [score, setScore] = useState({ white: 0, black: 0 })
  const [turn, setTurn] = useState('white')

  const [auswahl, setAuswahl] = useState('')
  const [selectedFrom, setSelectedFrom] = useState(null)
  const [hasJoined, setHasJoined] = useState(false)
  const [wasGameReady, setWasGameReady] = useState(false)

  const [rolle, setRolle] = useState('loading')
  const [wunschfarbe, setWunschfarbe] = useState('spectator')
  const [clientId, setClientId] = useState('')
  const [meldung, setMeldung] = useState('Verbinde mit Server...')
  const [players, setPlayers] = useState({ white_taken: false, black_taken: false })
  const gameReady = players.white_taken && players.black_taken

  const applyStateFromServer = (data) => {
    if (Array.isArray(data.triangles_black)) setTrianglesBlack(data.triangles_black)
    if (Array.isArray(data.triangles_white)) setTrianglesWhite(data.triangles_white)
    if (data.score) setScore(data.score)
    if (data.turn) setTurn(data.turn)
    if (data.players) {
      setPlayers({
        white_taken: !!data.players.white_taken,
        black_taken: !!data.players.black_taken
      })
    }
  }

  const joinWithPreference = async (id, desiredRole) => {
    try {
      const res = await fetch(
        `${API_BASE}/join?client_id=${encodeURIComponent(id)}&desired_role=${encodeURIComponent(desiredRole)}`
      )
      const data = await res.json()

      setRolle(data.role)
      applyStateFromServer(data)
      setHasJoined(true)

      if (data.role === 'white') setMeldung('Du bist Weiß.')
      if (data.role === 'black') setMeldung('Du bist Schwarz.')
      if (data.assignment === 'white_taken') setMeldung('Weiß ist bereits belegt. Du bist Zuschauer.')
      if (data.assignment === 'black_taken') setMeldung('Schwarz ist bereits belegt. Du bist Zuschauer.')
      if (data.role === 'spectator' && data.assignment === 'spectator') setMeldung('Du bist Zuschauer.')
    } catch {
      setRolle('spectator')
      setMeldung('Backend nicht erreichbar. Bitte starte den Server auf Port 8000.')
    }
  }

  useEffect(() => {
    let mounted = true
    const id = createOrGetClientId()
    setClientId(id)

    const pollState = async () => {
      try {
        const res = await fetch(`${API_BASE}/state?client_id=${encodeURIComponent(id)}&t=${Date.now()}`, { cache: 'no-store' })
        const data = await res.json()
        if (!mounted) return
        applyStateFromServer(data)
      } catch {
        // absichtlich leer
      }
    }

    pollState()
    const timer = setInterval(pollState, 1000)

    return () => {
      mounted = false
      clearInterval(timer)
    }
  }, [])

  const requestRole = async (preferredColor) => {
    if (!clientId) return
    setAuswahl('')
    setSelectedFrom(null)
    setWasGameReady(false)
    setWunschfarbe(preferredColor)
    await joinWithPreference(clientId, preferredColor)
  }

  useEffect(() => {
    const leaveGame = () => {
      if (!clientId) return
      const payload = JSON.stringify({ client_id: clientId })
      const url = `${API_BASE}/leave`

      // zuverlässiger Fallback: GET-Request via Image (kein CORS nötig)
      const img = new Image()
      img.src = `${API_BASE}/leave?client_id=${encodeURIComponent(clientId)}&t=${Date.now()}`

      if (navigator.sendBeacon) {
        const blob = new Blob([payload], { type: 'application/json' })
        navigator.sendBeacon(url, blob)
      } else {
        fetch(url, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: payload,
          keepalive: true
        }).catch(() => {})
      }
    }

    window.addEventListener('beforeunload', leaveGame)
    window.addEventListener('pagehide', leaveGame)

    return () => {
      window.removeEventListener('beforeunload', leaveGame)
      window.removeEventListener('pagehide', leaveGame)
    }
  }, [clientId])

  useEffect(() => {
    // Nur wenn ein laufendes Spiel (beide waren drin) auseinanderfällt,
    // zurück ins Rollen-Menü. Nicht direkt nach der ersten Rollenwahl.
    if (gameReady) {
      setWasGameReady(true)
      return
    }

    if (wasGameReady && hasJoined && (rolle === 'white' || rolle === 'black')) {
      setHasJoined(false)
      setRolle('loading')
      setAuswahl('')
      setSelectedFrom(null)
      setWasGameReady(false)
      setMeldung('Ein Spieler hat das Spiel verlassen. Bitte Farbe neu wählen.')
    }
  }, [gameReady, wasGameReady, hasJoined, rolle])

  const rollenText =
    rolle === 'white' ? 'Weiß' :
      rolle === 'black' ? 'Schwarz' :
        rolle === 'loading' ? 'Lade...' : 'Zuschauer'

  const hasBlackTriangleAt = (x, y) => trianglesBlack.findIndex((t) => t.x === x && t.y === y)
  const hasWhiteTriangleAt = (x, y) => trianglesWhite.findIndex((t) => t.x === x && t.y === y)

  const felder = []

  for (let y = 0; y < 8; y++) {
    for (let x = 0; x < 8; x++) {
      const farbe = (x + y) % 2 === 0 ? '#1900ff' : '#b300ff'
      let stein = null

      const blackTriangleIndex = hasBlackTriangleAt(x, y)
      const whiteTriangleIndex = hasWhiteTriangleAt(x, y)

      if (blackTriangleIndex !== -1) {
        const isSelected = auswahl === 'triangle_black' && selectedFrom?.x === x && selectedFrom?.y === y
        stein = (
          <div
            style={{
              width: 0,
              height: 0,
              borderLeft: '18px solid transparent',
              borderRight: '18px solid transparent',
              borderBottom: '30px solid black',
              filter: isSelected ? 'drop-shadow(0 0 4px red)' : 'none'
            }}
          />
        )
      }

      if (whiteTriangleIndex !== -1) {
        const isSelected = auswahl === 'triangle_white' && selectedFrom?.x === x && selectedFrom?.y === y
        stein = (
          <div
            style={{
              width: 0,
              height: 0,
              borderLeft: '18px solid transparent',
              borderRight: '18px solid transparent',
              borderBottom: '30px solid white',
              filter: isSelected ? 'drop-shadow(0 0 4px red)' : 'drop-shadow(0 0 1px #333)'
            }}
          />
        )
      }

      felder.push(
        <div
          key={x + '-' + y}
          onClick={async () => {
            if (rolle === 'spectator' || rolle === 'loading') {
              setAuswahl('')
              setSelectedFrom(null)
              setMeldung('Als Zuschauer darfst du keine Züge machen.')
              return
            }

            if (blackTriangleIndex !== -1) {
              if (rolle !== 'black') {
                setAuswahl('')
                setSelectedFrom(null)
                setMeldung('Nur Schwarz darf schwarze Dreiecke auswählen.')
                return
              }
              if (turn !== 'black') {
                setMeldung('Schwarz ist gerade nicht am Zug.')
                return
              }
              setAuswahl('triangle_black')
              setSelectedFrom({ x, y })
              setMeldung('Schwarzes Dreieck ausgewählt.')
              return
            }

            if (whiteTriangleIndex !== -1) {
              if (rolle !== 'white') {
                setAuswahl('')
                setSelectedFrom(null)
                setMeldung('Nur Weiß darf weiße Dreiecke auswählen.')
                return
              }
              if (turn !== 'white') {
                setMeldung('Weiß ist gerade nicht am Zug.')
                return
              }
              setAuswahl('triangle_white')
              setSelectedFrom({ x, y })
              setMeldung('Weißes Dreieck ausgewählt.')
              return
            }

            if (auswahl === '') return

            try {
              const body = {
                client_id: clientId,
                color: auswahl,
                x,
                y
              }

              if ((auswahl === 'triangle_black' || auswahl === 'triangle_white') && selectedFrom) {
                body.from_x = selectedFrom.x
                body.from_y = selectedFrom.y
              }

              const res = await fetch(`${API_BASE}/move`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
              })

              const data = await res.json()
              applyStateFromServer(data)
              setAuswahl('')
              setSelectedFrom(null)
              setMeldung(data.message || (data.accepted ? 'Zug gesendet.' : 'Ungültiger Zug.'))
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

  if (!hasJoined) {
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
        <div style={{ fontSize: '28px', fontWeight: 800 }}>Welche Farbe möchtest du?</div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button
            type="button"
            onClick={() => requestRole('white')}
            disabled={players.white_taken}
            style={{
              padding: '10px 14px',
              borderRadius: '10px',
              border: '2px solid #333',
              backgroundColor: players.white_taken ? '#eee' : '#fff',
              cursor: players.white_taken ? 'not-allowed' : 'pointer',
              fontWeight: 700
            }}
          >
            Weiß {players.white_taken ? '(belegt)' : ''}
          </button>

          <button
            type="button"
            onClick={() => requestRole('black')}
            disabled={players.black_taken}
            style={{
              padding: '10px 14px',
              borderRadius: '10px',
              border: '2px solid #333',
              backgroundColor: players.black_taken ? '#555' : '#111',
              color: 'white',
              cursor: players.black_taken ? 'not-allowed' : 'pointer',
              fontWeight: 700
            }}
          >
            Schwarz {players.black_taken ? '(belegt)' : ''}
          </button>

          <button
            type="button"
            onClick={() => requestRole('spectator')}
            style={{
              padding: '10px 14px',
              borderRadius: '10px',
              border: '2px solid #333',
              backgroundColor: '#f6f6f6',
              cursor: 'pointer',
              fontWeight: 700
            }}
          >
            Zuschauer
          </button>
        </div>
      </div>
    )
  }

  if ((rolle === 'white' || rolle === 'black') && !gameReady) {
    return (
      <div
        style={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: 'white',
          flexDirection: 'column',
          gap: '18px'
        }}
      >
        <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
        <div style={{ fontSize: '30px', fontWeight: 800 }}>Auf Spieler warten</div>
        <div
          style={{
            width: '54px',
            height: '54px',
            borderRadius: '50%',
            border: '6px solid #d9d9d9',
            borderTop: '6px solid #333',
            animation: 'spin 1s linear infinite'
          }}
        />
        <div style={{ fontSize: '16px', color: '#444' }}>
          Du bist {rollenText}. Das Spiel startet, sobald beide Farben besetzt sind.
        </div>
      </div>
    )
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

      <div style={{ fontSize: '18px' }}>
        Auswahl: {auswahl === '' ? 'kein Stein ausgewaehlt' : auswahl}
      </div>

      <div style={{ fontSize: '20px', fontWeight: 700 }}>
        Scoreboard — Weiß: {score.white} | Schwarz: {score.black}
      </div>

      <div style={{ fontSize: '18px', fontWeight: 700 }}>
        Am Zug: {turn === 'white' ? 'Weiß' : 'Schwarz'}
      </div>

      <button
        type="button"
        onClick={async () => {
          try {
            const res = await fetch(`${API_BASE}/reset_round`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ client_id: clientId })
            })
            const data = await res.json()
            applyStateFromServer(data)
            setAuswahl('')
            setSelectedFrom(null)
            setMeldung(data.message || 'Runde zurückgesetzt.')
          } catch {
            setMeldung('Reset fehlgeschlagen. Prüfe Backend-Verbindung.')
          }
        }}
        style={{
          padding: '10px 14px',
          borderRadius: '10px',
          border: '2px solid #333',
          backgroundColor: '#ffe9e9',
          cursor: 'pointer',
          fontWeight: 700
        }}
      >
        Runde aufgeben & Punkt an Gegner
      </button>

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

ReactDOM.createRoot(document.getElementById('root')).render(<App />)
