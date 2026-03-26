// Wir holen React und useState.
// useState brauchen wir für veränderbare Daten.
import React, { useState } from 'react'

// Damit sagen wir später: Zeige unsere App im Browser an.
import ReactDOM from 'react-dom/client'

// Das ist unsere Hauptfunktion für die ganze Seite.
function App() {

  // Hier speichern wir die Position vom weißen Stein.
  // x = Spalte, y = Zeile.
  const [weiss, setWeiss] = useState({ x: 3, y: 0 })

  // Hier speichern wir die Position vom schwarzen Stein.
  const [schwarz, setSchwarz] = useState({ x: 3, y: 7 })

  // Hier merken wir uns, ob gerade ein Stein ausgewählt ist.
  // Am Anfang ist nichts ausgewählt, deshalb ist der Text leer.
  const [auswahl, setAuswahl] = useState('')

  // In diese Liste legen wir später alle 64 Felder vom Brett.
  const felder = []

  // Äußere Schleife: geht durch alle Zeilen von 0 bis 7.
  for (let y = 0; y < 8; y++) {

    // Innere Schleife: geht durch alle Spalten von 0 bis 7.
    for (let x = 0; x < 8; x++) {

      // Hier berechnen wir die Farbe vom Feld.
      // Gerade Summe = hell, ungerade Summe = dunkel.
      let farbe = (x + y) % 2 === 0 ? '#1900ff' : '#b300ff'

      // In dieser Variablen speichern wir, was im Feld angezeigt wird.
      // Am Anfang ist das Feld leer.
      let stein = null

      // Prüfen: steht der weiße Stein auf diesem Feld?
      if (weiss.x === x && weiss.y === y) {

        // Wenn ja, bauen wir einen weißen Kreis.
        stein = (
          <div style={{
            // Breite vom Kreis
            width: '30px',
            // Höhe vom Kreis
            height: '30px',
            // 50% Rundung macht aus dem Rechteck einen Kreis
            borderRadius: '50%',
            // Farbe vom Stein
            backgroundColor: 'white',
            // Wenn weiß ausgewählt ist, roter Rand. Sonst grauer Rand.
            border: auswahl === 'weiss' ? '4px solid red' : '2px solid gray'
          }} />
        )
      }

      // Prüfen: steht der schwarze Stein auf diesem Feld?
      if (schwarz.x === x && schwarz.y === y) {

        // Wenn ja, bauen wir einen schwarzen Kreis.
        stein = (
          <div style={{
            // Breite vom Kreis
            width: '30px',
            // Höhe vom Kreis
            height: '30px',
            // 50% Rundung macht aus dem Rechteck einen Kreis
            borderRadius: '50%',
            // Farbe vom Stein
            backgroundColor: 'black',
            // Wenn schwarz ausgewählt ist, roter Rand. Sonst kein Rand.
            border: auswahl === 'schwarz' ? '4px solid red' : 'none'
          }} />
        )
      }

      // Jetzt fügen wir ein Feld zur Liste hinzu.
      felder.push(
        <div
          // Jeder Eintrag braucht einen eindeutigen Schlüssel.
          key={x + '-' + y}

          // Was beim Klick auf dieses Feld passieren soll.
          onClick={() => {

            // Wenn auf den weißen Stein geklickt wurde:
            if (weiss.x === x && weiss.y === y) {
              // Weiß auswählen
              setAuswahl('weiss')
              // Und hier aufhören
              return
            }

            // Wenn auf den schwarzen Stein geklickt wurde:
            if (schwarz.x === x && schwarz.y === y) {
              // Schwarz auswählen
              setAuswahl('schwarz')
              // Und hier aufhören
              return
            }

            // Wenn gerade weiß ausgewählt ist:
            if (auswahl === 'weiss') {
              // Weißen Stein auf dieses Feld setzen
              setWeiss({ x: x, y: y })
              // Auswahl wieder löschen
              setAuswahl('')
            }

            // Wenn gerade schwarz ausgewählt ist:
            if (auswahl === 'schwarz') {
              // Schwarzen Stein auf dieses Feld setzen
              setSchwarz({ x: x, y: y })
              // Auswahl wieder löschen
              setAuswahl('')
            }
          }}

          // Aussehen von diesem Feld
          style={{
            // Breite vom Feld
            width: '60px',
            // Höhe vom Feld
            height: '60px',
            // Feldfarbe
            backgroundColor: farbe,
            // Inhalt in die Mitte setzen
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            // Zeigt mit der Maus: hier kann man klicken
            cursor: 'pointer'
          }}
        >
          {/* Hier kommt der Stein hinein, wenn einer auf dem Feld steht. */}
          {stein}
        </div>
      )
    }
  }

  // Jetzt geben wir die ganze Seite zurück.
  return (
    <div style={{
      // Ganze Höhe vom Browserfenster benutzen
      minHeight: '100vh',
      // Inhalt mit Flexbox anordnen
      display: 'flex',
      // Inhalt waagerecht mittig
      alignItems: 'center',
      // Inhalt senkrecht mittig
      justifyContent: 'center',
      // Weißer Hintergrund
      backgroundColor: 'white',
      // Elemente untereinander statt nebeneinander
      flexDirection: 'column',
      // Abstand zwischen Text und Brett
      gap: '20px'
    }}>

      {/* Zeigt an, ob gerade ein Stein ausgewählt ist */}
      <div style={{ fontSize: '20px' }}>
        Auswahl: {auswahl === '' ? 'kein Stein ausgewaehlt' : auswahl}
      </div>

      {/* Das eigentliche Brett */}
      <div style={{
        // Raster-Anzeige
        display: 'grid',
        // 8 Spalten mit je 60 Pixel
        gridTemplateColumns: 'repeat(8, 60px)',
        // Äußerer Rand vom Brett
        border: '4px solid #ff0000'
      }}>
        {/* Hier werden alle Felder angezeigt */}
        {felder}
      </div>
    </div>
  )
}

// Hier sagen wir: App im Element mit id="root" anzeigen.
ReactDOM.createRoot(document.getElementById('root')).render(<App />)