# Wir holen FastAPI.
# Damit bauen wir unseren kleinen Web-Server.
from fastapi import FastAPI

# Das brauchen wir, damit das Frontend auf den Server zugreifen darf.
from fastapi.middleware.cors import CORSMiddleware

# Hier erstellen wir unsere Server-App.
app = FastAPI()

# Hier erlauben wir Zugriffe vom Frontend.
# Für diese Lernaufgabe erlauben wir einfach alles.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startposition vom weißen Stein:
# x = Spalte, y = Zeile
white_x = 3
white_y = 0

# Startposition vom schwarzen Stein:
# x = Spalte, y = Zeile
black_x = 3
black_y = 7

# Hier merken wir uns, welcher Browser weiß ist.
# Am Anfang ist noch niemand weiß.
white_player = ""

# Hier merken wir uns, welcher Browser schwarz ist.
# Am Anfang ist noch niemand schwarz.
black_player = ""


# Diese Route wird aufgerufen, wenn ein Browser dem Spiel beitritt.
# Der Browser schickt seine client_id mit.
@app.get("/join")
def join(client_id: str):

    # Wir sagen, dass wir die globalen Variablen verändern wollen.
    global white_player
    global black_player

    # Standardmäßig ist jeder neue Besucher erstmal Zuschauer.
    role = "spectator"

    # Wenn noch niemand weiß ist:
    if white_player == "":
        # dann bekommt dieser Browser die Rolle weiß
        white_player = client_id
        role = "white"

    # Sonst: wenn noch niemand schwarz ist:
    elif black_player == "":
        # dann bekommt dieser Browser die Rolle schwarz
        black_player = client_id
        role = "black"

    # Wenn dieser Browser schon früher weiß war:
    elif white_player == client_id:
        # dann bleibt er weiß
        role = "white"

    # Wenn dieser Browser schon früher schwarz war:
    elif black_player == client_id:
        # dann bleibt er schwarz
        role = "black"

    # Hier schicken wir die Rolle und die aktuellen Positionen zurück.
    return {
        "role": role,
        "white": {"x": white_x, "y": white_y},
        "black": {"x": black_x, "y": black_y}
    }


# Diese Route gibt einfach den aktuellen Stand zurück.
@app.get("/state")
def get_state():
    return {
        "white": {"x": white_x, "y": white_y},
        "black": {"x": black_x, "y": black_y}
    }


# Diese Route nimmt einen Zug vom Frontend an.
# Das Frontend schickt:
# client_id, color, x, y
@app.post("/move")
def move(data: dict):

    # Wir sagen wieder, dass wir globale Variablen ändern wollen.
    global white_x
    global white_y
    global black_x
    global black_y

    # Daten aus dem gesendeten Paket holen
    client_id = data["client_id"]
    color = data["color"]
    x = data["x"]
    y = data["y"]

    # Wenn weiß ziehen will und dieser Browser wirklich weiß ist:
    if color == "white" and client_id == white_player:
        # dann neue Position für weiß speichern
        white_x = x
        white_y = y

    # Wenn schwarz ziehen will und dieser Browser wirklich schwarz ist:
    if color == "black" and client_id == black_player:
        # dann neue Position für schwarz speichern
        black_x = x
        black_y = y

    # Danach schicken wir den neuen Stand zurück.
    return {
        "white": {"x": white_x, "y": white_y},
        "black": {"x": black_x, "y": black_y}
    }