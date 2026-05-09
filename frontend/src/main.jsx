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
  const calcCellSize = () => {
    const maxBoardWidth = Math.max(280, window.innerWidth - 24)
    return Math.max(34, Math.min(60, Math.floor(maxBoardWidth / 8)))
  }

  const [cellSize, setCellSize] = useState(calcCellSize())

  const [pawnsBlack, setPawnsBlack] = useState([])
  const [pawnsWhite, setPawnsWhite] = useState([])
  const [rooksBlack, setRooksBlack] = useState([])
  const [rooksWhite, setRooksWhite] = useState([])
  const [knightsBlack, setKnightsBlack] = useState([])
  const [knightsWhite, setKnightsWhite] = useState([])
  const [bishopsBlack, setBishopsBlack] = useState([])
  const [bishopsWhite, setBishopsWhite] = useState([])
  const [queensBlack, setQueensBlack] = useState([])
  const [queensWhite, setQueensWhite] = useState([])
  const [kingsBlack, setKingsBlack] = useState([])
  const [kingsWhite, setKingsWhite] = useState([])
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
  const [endOverlay, setEndOverlay] = useState('')
  const [lastRoundEvent, setLastRoundEvent] = useState('')
  const [pendingPromotion, setPendingPromotion] = useState(null)
  const [players, setPlayers] = useState({ white_taken: false, black_taken: false })
  const gameReady = players.white_taken && players.black_taken

  const showEndOverlayAndBackToMenu = (text) => {
    setEndOverlay(text)
    setAuswahl('')
    setSelectedFrom(null)

    window.setTimeout(() => {
      setEndOverlay('')
      setHasJoined(false)
      setRolle('loading')
      setWasGameReady(false)
      setMeldung(text)
    }, 5000)
  }

  const renderEndOverlay = () => {
    if (endOverlay === '') return null
    return (
      <div
        style={{
          position: 'fixed',
          inset: 0,
          backgroundColor: 'rgba(0,0,0,0.75)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 9999
        }}
      >
        <div style={{ fontSize: '56px', fontWeight: 900, color: 'white', letterSpacing: '2px' }}>
          {endOverlay}
        </div>
      </div>
    )
  }

  const submitMove = async (body) => {
    try {
      const res = await fetch(`${API_BASE}/move`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      })

      const data = await res.json()
      applyStateFromServer(data)
      setAuswahl('')
      setSelectedFrom(null)
      setPendingPromotion(null)
      setMeldung(data.message || (data.accepted ? 'Zug gesendet.' : 'Ungültiger Zug.'))

      const msg = (data.message || '').toLowerCase()
      if (msg.includes('schachmatt')) {
        showEndOverlayAndBackToMenu('SCHACHMATT')
      } else if (msg.includes('patt')) {
        showEndOverlayAndBackToMenu('PATT')
      }
    } catch {
      setMeldung('Zug konnte nicht gesendet werden. Prüfe Backend-Verbindung.')
    }
  }

  const renderPromotionMenu = () => {
    if (!pendingPromotion) return null

    const iconColor = pendingPromotion.color.endsWith('_white') ? '#fff' : '#111'
    const textShadow = pendingPromotion.color.endsWith('_white') ? '0 0 0.5px #000' : 'none'

    const options = [
      { key: 'queen', icon: '♛' },
      { key: 'knight', icon: '♞' },
      { key: 'rook', icon: '♜' },
      { key: 'bishop', icon: '♝' }
    ]

    return (
      <div style={{ position: 'fixed', left: 12, top: 12, zIndex: 9998 }}>
        <div style={{ backgroundColor: '#f0ede6', border: '2px solid #8a6a44', borderRadius: '10px', padding: '8px 6px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
          {options.map((opt) => (
            <button
              key={opt.key}
              type="button"
              onClick={() => submitMove({ ...pendingPromotion, promotion: opt.key })}
              style={{
                width: '58px',
                height: '58px',
                border: '1px solid #8a6a44',
                borderRadius: '8px',
                backgroundColor: '#f7f3ea',
                cursor: 'pointer',
                fontSize: '44px',
                lineHeight: 1,
                color: iconColor,
                textShadow
              }}
            >
              {opt.icon}
            </button>
          ))}
          <button
            type="button"
            onClick={() => {
              setPendingPromotion(null)
              setMeldung('Bauernumwandlung abgebrochen.')
            }}
            style={{ width: '58px', height: '40px', border: '1px solid #8a6a44', borderRadius: '8px', backgroundColor: '#eee', cursor: 'pointer', fontSize: '30px', color: '#666' }}
          >
            ×
          </button>
        </div>
      </div>
    )
  }

  const applyStateFromServer = (data) => {
    if (Array.isArray(data.pawns_black)) setPawnsBlack(data.pawns_black)
    if (Array.isArray(data.pawns_white)) setPawnsWhite(data.pawns_white)
    if (Array.isArray(data.rooks_black)) setRooksBlack(data.rooks_black)
    if (Array.isArray(data.rooks_white)) setRooksWhite(data.rooks_white)
    if (Array.isArray(data.knights_black)) setKnightsBlack(data.knights_black)
    if (Array.isArray(data.knights_white)) setKnightsWhite(data.knights_white)
    if (Array.isArray(data.bishops_black)) setBishopsBlack(data.bishops_black)
    if (Array.isArray(data.bishops_white)) setBishopsWhite(data.bishops_white)
    if (Array.isArray(data.queens_black)) setQueensBlack(data.queens_black)
    if (Array.isArray(data.queens_white)) setQueensWhite(data.queens_white)
    if (Array.isArray(data.kings_black)) setKingsBlack(data.kings_black)
    if (Array.isArray(data.kings_white)) setKingsWhite(data.kings_white)
    if (typeof data.round_event === 'string' && data.round_event !== '') {
      if (data.round_event !== lastRoundEvent) {
        setLastRoundEvent(data.round_event)
        showEndOverlayAndBackToMenu(data.round_event)
      }
    }
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
    const onResize = () => setCellSize(calcCellSize())
    window.addEventListener('resize', onResize)
    return () => window.removeEventListener('resize', onResize)
  }, [])

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
    const timer = setInterval(pollState, 80)

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

  const hasBlackPawnAt = (x, y) => pawnsBlack.findIndex((t) => t.x === x && t.y === y)
  const hasWhitePawnAt = (x, y) => pawnsWhite.findIndex((t) => t.x === x && t.y === y)
  const hasBlackRookAt = (x, y) => rooksBlack.findIndex((t) => t.x === x && t.y === y)
  const hasWhiteRookAt = (x, y) => rooksWhite.findIndex((t) => t.x === x && t.y === y)
  const hasBlackKnightAt = (x, y) => knightsBlack.findIndex((t) => t.x === x && t.y === y)
  const hasWhiteKnightAt = (x, y) => knightsWhite.findIndex((t) => t.x === x && t.y === y)
  const hasBlackBishopAt = (x, y) => bishopsBlack.findIndex((t) => t.x === x && t.y === y)
  const hasWhiteBishopAt = (x, y) => bishopsWhite.findIndex((t) => t.x === x && t.y === y)
  const hasBlackQueenAt = (x, y) => queensBlack.findIndex((t) => t.x === x && t.y === y)
  const hasWhiteQueenAt = (x, y) => queensWhite.findIndex((t) => t.x === x && t.y === y)
  const hasBlackKingAt = (x, y) => kingsBlack.findIndex((t) => t.x === x && t.y === y)
  const hasWhiteKingAt = (x, y) => kingsWhite.findIndex((t) => t.x === x && t.y === y)

  const occupiedAt = (x, y) => {
    return (
      hasBlackPawnAt(x, y) !== -1 ||
      hasWhitePawnAt(x, y) !== -1 ||
      hasBlackRookAt(x, y) !== -1 ||
      hasWhiteRookAt(x, y) !== -1 ||
      hasBlackKnightAt(x, y) !== -1 ||
      hasWhiteKnightAt(x, y) !== -1 ||
      hasBlackBishopAt(x, y) !== -1 ||
      hasWhiteBishopAt(x, y) !== -1 ||
      hasBlackQueenAt(x, y) !== -1 ||
      hasWhiteQueenAt(x, y) !== -1 ||
      hasBlackKingAt(x, y) !== -1 ||
      hasWhiteKingAt(x, y) !== -1
    )
  }

  const pathClearStraight = (fromX, fromY, toX, toY) => {
    if (fromX !== toX && fromY !== toY) return false
    if (fromX === toX && fromY === toY) return false

    if (fromX === toX) {
      const step = toY > fromY ? 1 : -1
      let yy = fromY + step
      while (yy !== toY) {
        if (occupiedAt(fromX, yy)) return false
        yy += step
      }
      return true
    }

    const step = toX > fromX ? 1 : -1
    let xx = fromX + step
    while (xx !== toX) {
      if (occupiedAt(xx, fromY)) return false
      xx += step
    }
    return true
  }

  const pathClearDiagonal = (fromX, fromY, toX, toY) => {
    const dx = toX - fromX
    const dy = toY - fromY
    if (dx === 0 && dy === 0) return false
    if (Math.abs(dx) !== Math.abs(dy)) return false

    const stepX = dx > 0 ? 1 : -1
    const stepY = dy > 0 ? 1 : -1
    let xx = fromX + stepX
    let yy = fromY + stepY
    while (xx !== toX && yy !== toY) {
      if (occupiedAt(xx, yy)) return false
      xx += stepX
      yy += stepY
    }
    return true
  }

  const isSquareAttackedBy = (side, x, y) => {
    if (side === 'white') {
      for (const p of pawnsWhite) {
        if ((p.x - 1 === x || p.x + 1 === x) && p.y - 1 === y) return true
      }
      for (const r of rooksWhite) {
        if (pathClearStraight(r.x, r.y, x, y)) return true
      }
      for (const n of knightsWhite) {
        const dx = Math.abs(n.x - x)
        const dy = Math.abs(n.y - y)
        if ((dx === 2 && dy === 1) || (dx === 1 && dy === 2)) return true
      }
      for (const b of bishopsWhite) {
        if (pathClearDiagonal(b.x, b.y, x, y)) return true
      }
      for (const q of queensWhite) {
        if (pathClearStraight(q.x, q.y, x, y) || pathClearDiagonal(q.x, q.y, x, y)) return true
      }
      for (const k of kingsWhite) {
        if (Math.max(Math.abs(k.x - x), Math.abs(k.y - y)) === 1) return true
      }
    } else {
      for (const p of pawnsBlack) {
        if ((p.x - 1 === x || p.x + 1 === x) && p.y + 1 === y) return true
      }
      for (const r of rooksBlack) {
        if (pathClearStraight(r.x, r.y, x, y)) return true
      }
      for (const n of knightsBlack) {
        const dx = Math.abs(n.x - x)
        const dy = Math.abs(n.y - y)
        if ((dx === 2 && dy === 1) || (dx === 1 && dy === 2)) return true
      }
      for (const b of bishopsBlack) {
        if (pathClearDiagonal(b.x, b.y, x, y)) return true
      }
      for (const q of queensBlack) {
        if (pathClearStraight(q.x, q.y, x, y) || pathClearDiagonal(q.x, q.y, x, y)) return true
      }
      for (const k of kingsBlack) {
        if (Math.max(Math.abs(k.x - x), Math.abs(k.y - y)) === 1) return true
      }
    }
    return false
  }

  const whiteKingInCheck = kingsWhite.length > 0 && isSquareAttackedBy('black', kingsWhite[0].x, kingsWhite[0].y)
  const blackKingInCheck = kingsBlack.length > 0 && isSquareAttackedBy('white', kingsBlack[0].x, kingsBlack[0].y)

  const mapDisplayToBoard = (displayX, displayY) => {
    if (rolle === 'black') {
      return { x: 7 - displayX, y: 7 - displayY }
    }
    return { x: displayX, y: displayY }
  }

  const felder = []

  for (let displayY = 0; displayY < 8; displayY++) {
    for (let displayX = 0; displayX < 8; displayX++) {
      const { x, y } = mapDisplayToBoard(displayX, displayY)
      const farbe = (displayX + displayY) % 2 === 0 ? '#f0d9b5' : '#b58863'
      let stein = null

      const blackPawnIndex = hasBlackPawnAt(x, y)
      const whitePawnIndex = hasWhitePawnAt(x, y)
      const blackRookIndex = hasBlackRookAt(x, y)
      const whiteRookIndex = hasWhiteRookAt(x, y)
      const blackKnightIndex = hasBlackKnightAt(x, y)
      const whiteKnightIndex = hasWhiteKnightAt(x, y)
      const blackBishopIndex = hasBlackBishopAt(x, y)
      const whiteBishopIndex = hasWhiteBishopAt(x, y)
      const blackQueenIndex = hasBlackQueenAt(x, y)
      const whiteQueenIndex = hasWhiteQueenAt(x, y)
      const blackKingIndex = hasBlackKingAt(x, y)
      const whiteKingIndex = hasWhiteKingAt(x, y)

      const isCheckedKingCell =
        (whiteKingInCheck && whiteKingIndex !== -1) ||
        (blackKingInCheck && blackKingIndex !== -1)

      const isSelectedBlackRook = auswahl === 'rook_black' && selectedFrom?.x === x && selectedFrom?.y === y
      const isSelectedWhiteRook = auswahl === 'rook_white' && selectedFrom?.x === x && selectedFrom?.y === y
      const isSelectedBlackKnight = auswahl === 'knight_black' && selectedFrom?.x === x && selectedFrom?.y === y
      const isSelectedWhiteKnight = auswahl === 'knight_white' && selectedFrom?.x === x && selectedFrom?.y === y
      const isSelectedBlackBishop = auswahl === 'bishop_black' && selectedFrom?.x === x && selectedFrom?.y === y
      const isSelectedWhiteBishop = auswahl === 'bishop_white' && selectedFrom?.x === x && selectedFrom?.y === y
      const isSelectedBlackQueen = auswahl === 'queen_black' && selectedFrom?.x === x && selectedFrom?.y === y
      const isSelectedWhiteQueen = auswahl === 'queen_white' && selectedFrom?.x === x && selectedFrom?.y === y
      const isSelectedBlackKing = auswahl === 'king_black' && selectedFrom?.x === x && selectedFrom?.y === y
      const isSelectedWhiteKing = auswahl === 'king_white' && selectedFrom?.x === x && selectedFrom?.y === y

      if (blackPawnIndex !== -1) {
        const isSelected = auswahl === 'pawn_black' && selectedFrom?.x === x && selectedFrom?.y === y
        stein = (
          <div
            style={{
              width: 0,
              height: 0,
              borderLeft: `${Math.floor(cellSize * 0.3)}px solid transparent`,
              borderRight: `${Math.floor(cellSize * 0.3)}px solid transparent`,
              borderBottom: `${Math.floor(cellSize * 0.5)}px solid black`,
              filter: isSelected ? 'drop-shadow(0 0 4px red)' : 'none'
            }}
          />
        )
      }

      if (whitePawnIndex !== -1) {
        const isSelected = auswahl === 'pawn_white' && selectedFrom?.x === x && selectedFrom?.y === y
        stein = (
          <div
            style={{
              width: 0,
              height: 0,
              borderLeft: `${Math.floor(cellSize * 0.3)}px solid transparent`,
              borderRight: `${Math.floor(cellSize * 0.3)}px solid transparent`,
              borderBottom: `${Math.floor(cellSize * 0.5)}px solid #fff`,
              filter: isSelected ? 'drop-shadow(0 0 4px red)' : 'drop-shadow(0 0 0.5px #000)'
            }}
          />
        )
      }

      if (blackRookIndex !== -1) {
        stein = (
          <div
            style={{
              height: `${cellSize}px`,
              width: `${cellSize}px`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: `${Math.floor(cellSize * 0.85)}px`,
              lineHeight: 1,
              color: '#111',
              textShadow: isSelectedBlackRook ? '0 0 4px red' : 'none',
              userSelect: 'none'
            }}
          >
            ♜
          </div>
        )
      }

      if (whiteRookIndex !== -1) {
        stein = (
          <div
            style={{
              height: `${cellSize}px`,
              width: `${cellSize}px`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: `${Math.floor(cellSize * 0.85)}px`,
              lineHeight: 1,
              color: '#fff',
              textShadow: isSelectedWhiteRook ? '0 0 4px red, 0 0 0.5px #000' : '0 0 0.5px #000',
              WebkitTextStroke: '0.35px #000',
              userSelect: 'none'
            }}
          >
            ♖
          </div>
        )
      }

      if (blackKnightIndex !== -1) {
        stein = (
          <div
            style={{
              height: `${cellSize}px`,
              width: `${cellSize}px`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: `${Math.floor(cellSize * 0.85)}px`,
              lineHeight: 1,
              color: '#111',
              textShadow: isSelectedBlackKnight ? '0 0 4px red' : 'none',
              userSelect: 'none'
            }}
          >
            ♞
          </div>
        )
      }

      if (whiteKnightIndex !== -1) {
        stein = (
          <div
            style={{
              height: `${cellSize}px`,
              width: `${cellSize}px`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: `${Math.floor(cellSize * 0.85)}px`,
              lineHeight: 1,
              color: '#fff',
              textShadow: isSelectedWhiteKnight ? '0 0 4px red, 0 0 0.5px #000' : '0 0 0.5px #000',
              WebkitTextStroke: '0.35px #000',
              userSelect: 'none'
            }}
          >
            ♘
          </div>
        )
      }

      if (blackBishopIndex !== -1) {
        stein = (
          <div
            style={{
              height: `${cellSize}px`,
              width: `${cellSize}px`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: `${Math.floor(cellSize * 0.85)}px`,
              lineHeight: 1,
              color: '#111',
              textShadow: isSelectedBlackBishop ? '0 0 4px red' : 'none',
              userSelect: 'none'
            }}
          >
            ♝
          </div>
        )
      }

      if (whiteBishopIndex !== -1) {
        stein = (
          <div
            style={{
              height: `${cellSize}px`,
              width: `${cellSize}px`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: `${Math.floor(cellSize * 0.85)}px`,
              lineHeight: 1,
              color: '#fff',
              textShadow: isSelectedWhiteBishop ? '0 0 4px red, 0 0 0.5px #000' : '0 0 0.5px #000',
              WebkitTextStroke: '0.35px #000',
              userSelect: 'none'
            }}
          >
            ♗
          </div>
        )
      }

      if (blackQueenIndex !== -1) {
        stein = (
          <div
            style={{
              height: `${cellSize}px`,
              width: `${cellSize}px`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: `${Math.floor(cellSize * 0.85)}px`,
              lineHeight: 1,
              color: '#111',
              textShadow: isSelectedBlackQueen ? '0 0 4px red' : 'none',
              userSelect: 'none'
            }}
          >
            ♛
          </div>
        )
      }

      if (whiteQueenIndex !== -1) {
        stein = (
          <div
            style={{
              height: `${cellSize}px`,
              width: `${cellSize}px`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: `${Math.floor(cellSize * 0.85)}px`,
              lineHeight: 1,
              color: '#fff',
              textShadow: isSelectedWhiteQueen ? '0 0 4px red, 0 0 0.5px #000' : '0 0 0.5px #000',
              WebkitTextStroke: '0.35px #000',
              userSelect: 'none'
            }}
          >
            ♕
          </div>
        )
      }

      if (blackKingIndex !== -1) {
        stein = (
          <div
            style={{
              height: `${cellSize}px`,
              width: `${cellSize}px`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: `${Math.floor(cellSize * 0.85)}px`,
              lineHeight: 1,
              color: '#111',
              textShadow: isSelectedBlackKing ? '0 0 4px red' : 'none',
              userSelect: 'none'
            }}
          >
            ♚
          </div>
        )
      }

      if (whiteKingIndex !== -1) {
        stein = (
          <div
            style={{
              height: `${cellSize}px`,
              width: `${cellSize}px`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: `${Math.floor(cellSize * 0.85)}px`,
              lineHeight: 1,
              color: '#fff',
              textShadow: isSelectedWhiteKing ? '0 0 4px red, 0 0 0.5px #000' : '0 0 0.5px #000',
              WebkitTextStroke: '0.35px #000',
              userSelect: 'none'
            }}
          >
            ♔
          </div>
        )
      }

      felder.push(
        <div
          key={displayX + '-' + displayY}
          onClick={async () => {
            if (rolle === 'spectator' || rolle === 'loading') {
              setAuswahl('')
              setSelectedFrom(null)
              setMeldung('Als Zuschauer darfst du keine Züge machen.')
              return
            }

            // DEBUG-LOG: möglicher Schlag-Bug, wenn Zielfeld mit Gegnerbauer angeklickt wird.
            if (auswahl === 'pawn_white' && selectedFrom && blackPawnIndex !== -1) {
              console.info('[DEBUG capture-intent blocked?] white selected pawn clicked black-occupied target', {
                selectedFrom,
                target: { x, y },
                blackPawnIndex,
                role: rolle,
                turn
              })
            }

            if (auswahl === 'pawn_black' && selectedFrom && whitePawnIndex !== -1) {
              console.info('[DEBUG capture-intent blocked?] black selected pawn clicked white-occupied target', {
                selectedFrom,
                target: { x, y },
                whitePawnIndex,
                role: rolle,
                turn
              })
            }

            if (blackPawnIndex !== -1) {
              // Wenn ein weißer Bauer bereits ausgewählt ist, soll der gegnerische
              // schwarze Bauer als Ziel-Feld behandelt werden (nicht auswählbar).
              if ((auswahl === 'pawn_white' || auswahl === 'rook_white' || auswahl === 'knight_white' || auswahl === 'bishop_white' || auswahl === 'queen_white' || auswahl === 'king_white') && selectedFrom) {
                // Kein return: weiter unten wird normal der Move-Request gesendet.
              } else {
              if (rolle !== 'black') {
                setAuswahl('')
                setSelectedFrom(null)
                setMeldung('Nur Schwarz darf schwarze Bauern auswählen.')
                return
              }
              if (turn !== 'black') {
                setMeldung('Schwarz ist gerade nicht am Zug.')
                return
              }
              setAuswahl('pawn_black')
              setSelectedFrom({ x, y })
              setMeldung('Schwarzer Bauer ausgewählt.')
              return
              }
            }

            if (blackRookIndex !== -1) {
              if (auswahl === 'pawn_white' && selectedFrom) {
                // gegnerischer Turm als Ziel behandeln
              } else if (auswahl === 'rook_white' && selectedFrom) {
                // gegnerischer Turm als Ziel behandeln
              } else if (auswahl === 'knight_white' && selectedFrom) {
                // gegnerischer Turm als Ziel behandeln
              } else if (auswahl === 'bishop_white' && selectedFrom) {
                // gegnerischer Turm als Ziel behandeln
              } else if (auswahl === 'queen_white' && selectedFrom) {
                // gegnerischer Turm als Ziel behandeln
              } else if (auswahl === 'king_white' && selectedFrom) {
                // gegnerischer Turm als Ziel behandeln
              } else {
                if (rolle !== 'black') {
                  setAuswahl('')
                  setSelectedFrom(null)
                  setMeldung('Nur Schwarz darf schwarze Türme auswählen.')
                  return
                }
                if (turn !== 'black') {
                  setMeldung('Schwarz ist gerade nicht am Zug.')
                  return
                }
                setAuswahl('rook_black')
                setSelectedFrom({ x, y })
                setMeldung('Schwarzer Turm ausgewählt.')
                return
              }
            }

            if (whitePawnIndex !== -1) {
              // Wenn ein schwarzer Bauer bereits ausgewählt ist, soll der gegnerische
              // weiße Bauer als Ziel-Feld behandelt werden (nicht auswählbar).
              if ((auswahl === 'pawn_black' || auswahl === 'rook_black' || auswahl === 'knight_black' || auswahl === 'bishop_black' || auswahl === 'queen_black' || auswahl === 'king_black') && selectedFrom) {
                // Kein return: weiter unten wird normal der Move-Request gesendet.
              } else {
              if (rolle !== 'white') {
                setAuswahl('')
                setSelectedFrom(null)
                setMeldung('Nur Weiß darf weiße Bauern auswählen.')
                return
              }
              if (turn !== 'white') {
                setMeldung('Weiß ist gerade nicht am Zug.')
                return
              }
              setAuswahl('pawn_white')
              setSelectedFrom({ x, y })
              setMeldung('Weißer Bauer ausgewählt.')
              return
              }
            }

            if (whiteRookIndex !== -1) {
              if (auswahl === 'pawn_black' && selectedFrom) {
                // gegnerischer Turm als Ziel behandeln
              } else if (auswahl === 'rook_black' && selectedFrom) {
                // gegnerischer Turm als Ziel behandeln
              } else if (auswahl === 'knight_black' && selectedFrom) {
                // gegnerischer Turm als Ziel behandeln
              } else if (auswahl === 'bishop_black' && selectedFrom) {
                // gegnerischer Turm als Ziel behandeln
              } else if (auswahl === 'queen_black' && selectedFrom) {
                // gegnerischer Turm als Ziel behandeln
              } else if (auswahl === 'king_black' && selectedFrom) {
                // gegnerischer Turm als Ziel behandeln
              } else {
                if (rolle !== 'white') {
                  setAuswahl('')
                  setSelectedFrom(null)
                  setMeldung('Nur Weiß darf weiße Türme auswählen.')
                  return
                }
                if (turn !== 'white') {
                  setMeldung('Weiß ist gerade nicht am Zug.')
                  return
                }
                setAuswahl('rook_white')
                setSelectedFrom({ x, y })
                setMeldung('Weißer Turm ausgewählt.')
                return
              }
            }

            if (blackKnightIndex !== -1) {
              if (auswahl === 'pawn_white' && selectedFrom) {
                // gegnerisches Pferd als Ziel behandeln
              } else if (auswahl === 'rook_white' && selectedFrom) {
                // gegnerisches Pferd als Ziel behandeln
              } else if (auswahl === 'knight_white' && selectedFrom) {
                // gegnerisches Pferd als Ziel behandeln
              } else if (auswahl === 'bishop_white' && selectedFrom) {
                // gegnerisches Pferd als Ziel behandeln
              } else if (auswahl === 'queen_white' && selectedFrom) {
                // gegnerisches Pferd als Ziel behandeln
              } else if (auswahl === 'king_white' && selectedFrom) {
                // gegnerisches Pferd als Ziel behandeln
              } else {
                if (rolle !== 'black') {
                  setAuswahl('')
                  setSelectedFrom(null)
                  setMeldung('Nur Schwarz darf schwarze Pferde auswählen.')
                  return
                }
                if (turn !== 'black') {
                  setMeldung('Schwarz ist gerade nicht am Zug.')
                  return
                }
                setAuswahl('knight_black')
                setSelectedFrom({ x, y })
                setMeldung('Schwarzes Pferd ausgewählt.')
                return
              }
            }

            if (whiteKnightIndex !== -1) {
              if (auswahl === 'pawn_black' && selectedFrom) {
                // gegnerisches Pferd als Ziel behandeln
              } else if (auswahl === 'rook_black' && selectedFrom) {
                // gegnerisches Pferd als Ziel behandeln
              } else if (auswahl === 'knight_black' && selectedFrom) {
                // gegnerisches Pferd als Ziel behandeln
              } else if (auswahl === 'bishop_black' && selectedFrom) {
                // gegnerisches Pferd als Ziel behandeln
              } else if (auswahl === 'queen_black' && selectedFrom) {
                // gegnerisches Pferd als Ziel behandeln
              } else if (auswahl === 'king_black' && selectedFrom) {
                // gegnerisches Pferd als Ziel behandeln
              } else {
                if (rolle !== 'white') {
                  setAuswahl('')
                  setSelectedFrom(null)
                  setMeldung('Nur Weiß darf weiße Pferde auswählen.')
                  return
                }
                if (turn !== 'white') {
                  setMeldung('Weiß ist gerade nicht am Zug.')
                  return
                }
                setAuswahl('knight_white')
                setSelectedFrom({ x, y })
                setMeldung('Weißes Pferd ausgewählt.')
                return
              }
            }

            if (blackBishopIndex !== -1) {
              if (auswahl === 'pawn_white' && selectedFrom) {
                // gegnerischen Läufer als Ziel behandeln
              } else if (auswahl === 'rook_white' && selectedFrom) {
                // gegnerischen Läufer als Ziel behandeln
              } else if (auswahl === 'knight_white' && selectedFrom) {
                // gegnerischen Läufer als Ziel behandeln
              } else if (auswahl === 'bishop_white' && selectedFrom) {
                // gegnerischen Läufer als Ziel behandeln
              } else if (auswahl === 'queen_white' && selectedFrom) {
                // gegnerischen Läufer als Ziel behandeln
              } else if (auswahl === 'king_white' && selectedFrom) {
                // gegnerischen Läufer als Ziel behandeln
              } else {
                if (rolle !== 'black') {
                  setAuswahl('')
                  setSelectedFrom(null)
                  setMeldung('Nur Schwarz darf schwarze Läufer auswählen.')
                  return
                }
                if (turn !== 'black') {
                  setMeldung('Schwarz ist gerade nicht am Zug.')
                  return
                }
                setAuswahl('bishop_black')
                setSelectedFrom({ x, y })
                setMeldung('Schwarzer Läufer ausgewählt.')
                return
              }
            }

            if (whiteBishopIndex !== -1) {
              if (auswahl === 'pawn_black' && selectedFrom) {
                // gegnerischen Läufer als Ziel behandeln
              } else if (auswahl === 'rook_black' && selectedFrom) {
                // gegnerischen Läufer als Ziel behandeln
              } else if (auswahl === 'knight_black' && selectedFrom) {
                // gegnerischen Läufer als Ziel behandeln
              } else if (auswahl === 'bishop_black' && selectedFrom) {
                // gegnerischen Läufer als Ziel behandeln
              } else if (auswahl === 'queen_black' && selectedFrom) {
                // gegnerischen Läufer als Ziel behandeln
              } else if (auswahl === 'king_black' && selectedFrom) {
                // gegnerischen Läufer als Ziel behandeln
              } else {
                if (rolle !== 'white') {
                  setAuswahl('')
                  setSelectedFrom(null)
                  setMeldung('Nur Weiß darf weiße Läufer auswählen.')
                  return
                }
                if (turn !== 'white') {
                  setMeldung('Weiß ist gerade nicht am Zug.')
                  return
                }
                setAuswahl('bishop_white')
                setSelectedFrom({ x, y })
                setMeldung('Weißer Läufer ausgewählt.')
                return
              }
            }

            if (blackQueenIndex !== -1) {
              if (auswahl === 'pawn_white' && selectedFrom) {
                // gegnerische Dame als Ziel behandeln
              } else if (auswahl === 'rook_white' && selectedFrom) {
                // gegnerische Dame als Ziel behandeln
              } else if (auswahl === 'knight_white' && selectedFrom) {
                // gegnerische Dame als Ziel behandeln
              } else if (auswahl === 'queen_white' && selectedFrom) {
                // gegnerische Dame als Ziel behandeln
              } else if (auswahl === 'king_white' && selectedFrom) {
                // gegnerische Dame als Ziel behandeln
              } else {
                if (rolle !== 'black') {
                  setAuswahl('')
                  setSelectedFrom(null)
                  setMeldung('Nur Schwarz darf schwarze Damen auswählen.')
                  return
                }
                if (turn !== 'black') {
                  setMeldung('Schwarz ist gerade nicht am Zug.')
                  return
                }
                setAuswahl('queen_black')
                setSelectedFrom({ x, y })
                setMeldung('Schwarze Dame ausgewählt.')
                return
              }
            }

            if (whiteQueenIndex !== -1) {
              if (auswahl === 'pawn_black' && selectedFrom) {
                // gegnerische Dame als Ziel behandeln
              } else if (auswahl === 'rook_black' && selectedFrom) {
                // gegnerische Dame als Ziel behandeln
              } else if (auswahl === 'knight_black' && selectedFrom) {
                // gegnerische Dame als Ziel behandeln
              } else if (auswahl === 'queen_black' && selectedFrom) {
                // gegnerische Dame als Ziel behandeln
              } else if (auswahl === 'king_black' && selectedFrom) {
                // gegnerische Dame als Ziel behandeln
              } else {
                if (rolle !== 'white') {
                  setAuswahl('')
                  setSelectedFrom(null)
                  setMeldung('Nur Weiß darf weiße Damen auswählen.')
                  return
                }
                if (turn !== 'white') {
                  setMeldung('Weiß ist gerade nicht am Zug.')
                  return
                }
                setAuswahl('queen_white')
                setSelectedFrom({ x, y })
                setMeldung('Weiße Dame ausgewählt.')
                return
              }
            }

            if (blackKingIndex !== -1) {
              if (auswahl && selectedFrom && auswahl.endsWith('_white')) {
                // gegnerischen König als Ziel behandeln (Backend blockiert Schlagen)
              } else {
                if (rolle !== 'black') {
                  setAuswahl('')
                  setSelectedFrom(null)
                  setMeldung('Nur Schwarz darf den schwarzen König auswählen.')
                  return
                }
                if (turn !== 'black') {
                  setMeldung('Schwarz ist gerade nicht am Zug.')
                  return
                }
                setAuswahl('king_black')
                setSelectedFrom({ x, y })
                setMeldung('Schwarzer König ausgewählt.')
                return
              }
            }

            if (whiteKingIndex !== -1) {
              if (auswahl && selectedFrom && auswahl.endsWith('_black')) {
                // gegnerischen König als Ziel behandeln (Backend blockiert Schlagen)
              } else {
                if (rolle !== 'white') {
                  setAuswahl('')
                  setSelectedFrom(null)
                  setMeldung('Nur Weiß darf den weißen König auswählen.')
                  return
                }
                if (turn !== 'white') {
                  setMeldung('Weiß ist gerade nicht am Zug.')
                  return
                }
                setAuswahl('king_white')
                setSelectedFrom({ x, y })
                setMeldung('Weißer König ausgewählt.')
                return
              }
            }

            if (auswahl === '') return

            try {
              const body = {
                client_id: clientId,
                color: auswahl,
                x,
                y
              }

              if (
                (auswahl === 'pawn_black' || auswahl === 'pawn_white' ||
                  auswahl === 'rook_black' || auswahl === 'rook_white' ||
                  auswahl === 'knight_black' || auswahl === 'knight_white' ||
                  auswahl === 'bishop_black' || auswahl === 'bishop_white' ||
                  auswahl === 'queen_black' || auswahl === 'queen_white' ||
                  auswahl === 'king_black' || auswahl === 'king_white') &&
                selectedFrom
              ) {
                body.from_x = selectedFrom.x
                body.from_y = selectedFrom.y
              }

              if ((auswahl === 'pawn_white' || auswahl === 'pawn_black') && selectedFrom) {
                const reachesLastRank = (auswahl === 'pawn_white' && y === 0) || (auswahl === 'pawn_black' && y === 7)
                if (reachesLastRank) {
                  setPendingPromotion(body)
                  setMeldung('Bitte Umwandlungsfigur wählen.')
                  return
                }
              }

              await submitMove(body)
            } catch {
              setMeldung('Zug konnte nicht gesendet werden. Prüfe Backend-Verbindung.')
            }
          }}
          style={{
            height: `${cellSize}px`,
            width: `${cellSize}px`,
            backgroundColor: isCheckedKingCell ? '#ff6b6b' : farbe,
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
        {renderEndOverlay()}
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
        {renderEndOverlay()}
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
          width: '100%',
          display: 'flex',
          justifyContent: 'center',
          overflowX: 'auto',
          padding: '0 6px',
          boxSizing: 'border-box'
        }}
      >
        <div
          style={{
          display: 'grid',
          gridTemplateColumns: `repeat(8, ${cellSize}px)`,
          border: '4px solid #ff0000'
        }}
        >
          {felder}
        </div>
      </div>

      {renderEndOverlay()}
      {renderPromotionMenu()}
    </div>
  )
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />)
