# Wir holen FastAPI.
# Damit bauen wir unseren kleinen Web-Server.
from fastapi import FastAPI
import time

# Das brauchen wir, damit das Frontend auf den Server zugreifen darf.
from fastapi.middleware.cors import CORSMiddleware

# Hier erstellen wir unsere Server-App.
app = FastAPI()

# Hier erlauben wir Zugriffe vom Frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Bauern:
# schwarz auf Reihe 2 (y=1), weiß auf Reihe 7 (y=6)
black_pawns = [{"x": x, "y": 1} for x in range(8)]
white_pawns = [{"x": x, "y": 6} for x in range(8)]

# Türme in den Ecken der jeweiligen Seiten
black_rooks = [{"x": 0, "y": 0}, {"x": 7, "y": 0}]
white_rooks = [{"x": 0, "y": 7}, {"x": 7, "y": 7}]

# Pferde wie im Schach auf b/g-Linien
black_knights = [{"x": 1, "y": 0}, {"x": 6, "y": 0}]
white_knights = [{"x": 1, "y": 7}, {"x": 6, "y": 7}]

# Damen auf d8 (schwarz) und d1 (weiß)
black_queens = [{"x": 3, "y": 0}]
white_queens = [{"x": 3, "y": 7}]

# Punkte-Stand
white_score = 0
black_score = 0

# Zugreihenfolge
current_turn = "white"

# Zugewiesene Spieler
white_player = ""
black_player = ""

# Letzte Aktivität je Spieler (Auto-Freigabe bei Verbindungsabbruch)
white_last_seen = 0.0
black_last_seen = 0.0

PLAYER_TIMEOUT_SECONDS = 2.5


def clear_all_players_and_reset():
    global white_player
    global black_player
    global white_last_seen
    global black_last_seen

    white_player = ""
    black_player = ""
    white_last_seen = 0.0
    black_last_seen = 0.0
    reset_positions()


def cleanup_disconnected_players():
    global white_player
    global black_player
    global white_last_seen
    global black_last_seen

    now = time.time()
    had_both_players = (white_player != "" and black_player != "")

    if white_player != "" and (now - white_last_seen) > PLAYER_TIMEOUT_SECONDS:
        white_player = ""
        white_last_seen = 0.0

    if black_player != "" and (now - black_last_seen) > PLAYER_TIMEOUT_SECONDS:
        black_player = ""
        black_last_seen = 0.0

    # Wenn ein aktives 2-Spieler-Spiel auseinanderfällt,
    # beide ausloggen und alles freigeben.
    if had_both_players and (white_player == "" or black_player == ""):
        clear_all_players_and_reset()


def touch_player(client_id: str):
    global white_last_seen
    global black_last_seen

    now = time.time()
    if client_id == white_player:
        white_last_seen = now
    if client_id == black_player:
        black_last_seen = now


def current_state():
    cleanup_disconnected_players()
    return {
        "pawns_black": black_pawns,
        "pawns_white": white_pawns,
        "rooks_black": black_rooks,
        "rooks_white": white_rooks,
        "knights_black": black_knights,
        "knights_white": white_knights,
        "queens_black": black_queens,
        "queens_white": white_queens,
        "score": {"white": white_score, "black": black_score},
        "turn": current_turn,
        "players": {
            "white_taken": white_player != "",
            "black_taken": black_player != "",
            "white_player": white_player,
            "black_player": black_player,
        },
    }


def reset_positions():
    global black_pawns
    global white_pawns
    global black_rooks
    global white_rooks
    global black_knights
    global white_knights
    global black_queens
    global white_queens
    global current_turn

    black_pawns = [{"x": x, "y": 1} for x in range(8)]
    white_pawns = [{"x": x, "y": 6} for x in range(8)]
    black_rooks = [{"x": 0, "y": 0}, {"x": 7, "y": 0}]
    white_rooks = [{"x": 0, "y": 7}, {"x": 7, "y": 7}]
    black_knights = [{"x": 1, "y": 0}, {"x": 6, "y": 0}]
    white_knights = [{"x": 1, "y": 7}, {"x": 6, "y": 7}]
    black_queens = [{"x": 3, "y": 0}]
    white_queens = [{"x": 3, "y": 7}]
    current_turn = "white"


def find_pawn_index(pawns: list, x: int, y: int):
    for idx, t in enumerate(pawns):
        if t["x"] == x and t["y"] == y:
            return idx
    return -1


def find_rook_index(rooks: list, x: int, y: int):
    for idx, t in enumerate(rooks):
        if t["x"] == x and t["y"] == y:
            return idx
    return -1


def find_knight_index(knights: list, x: int, y: int):
    for idx, t in enumerate(knights):
        if t["x"] == x and t["y"] == y:
            return idx
    return -1


def find_queen_index(queens: list, x: int, y: int):
    for idx, t in enumerate(queens):
        if t["x"] == x and t["y"] == y:
            return idx
    return -1


def cell_occupied(x: int, y: int, ignore_kind: str = "", ignore_index: int = -1):
    for idx, t in enumerate(black_pawns):
        if ignore_kind == "pawn_black" and idx == ignore_index:
            continue
        if t["x"] == x and t["y"] == y:
            return True

    for idx, t in enumerate(white_pawns):
        if ignore_kind == "pawn_white" and idx == ignore_index:
            continue
        if t["x"] == x and t["y"] == y:
            return True

    for idx, t in enumerate(black_rooks):
        if ignore_kind == "rook_black" and idx == ignore_index:
            continue
        if t["x"] == x and t["y"] == y:
            return True

    for idx, t in enumerate(white_rooks):
        if ignore_kind == "rook_white" and idx == ignore_index:
            continue
        if t["x"] == x and t["y"] == y:
            return True

    for idx, t in enumerate(black_knights):
        if ignore_kind == "knight_black" and idx == ignore_index:
            continue
        if t["x"] == x and t["y"] == y:
            return True

    for idx, t in enumerate(white_knights):
        if ignore_kind == "knight_white" and idx == ignore_index:
            continue
        if t["x"] == x and t["y"] == y:
            return True

    for idx, t in enumerate(black_queens):
        if ignore_kind == "queen_black" and idx == ignore_index:
            continue
        if t["x"] == x and t["y"] == y:
            return True

    for idx, t in enumerate(white_queens):
        if ignore_kind == "queen_white" and idx == ignore_index:
            continue
        if t["x"] == x and t["y"] == y:
            return True

    return False


def get_piece_at(x: int, y: int):
    for t in black_pawns:
        if t["x"] == x and t["y"] == y:
            return "pawn_black"

    for t in white_pawns:
        if t["x"] == x and t["y"] == y:
            return "pawn_white"

    for t in black_rooks:
        if t["x"] == x and t["y"] == y:
            return "rook_black"

    for t in white_rooks:
        if t["x"] == x and t["y"] == y:
            return "rook_white"

    for t in black_knights:
        if t["x"] == x and t["y"] == y:
            return "knight_black"

    for t in white_knights:
        if t["x"] == x and t["y"] == y:
            return "knight_white"

    for t in black_queens:
        if t["x"] == x and t["y"] == y:
            return "queen_black"

    for t in white_queens:
        if t["x"] == x and t["y"] == y:
            return "queen_white"

    return ""


def remove_piece_at(x: int, y: int):
    idx = find_pawn_index(black_pawns, x, y)
    if idx != -1:
        del black_pawns[idx]
        return "pawn_black"

    idx = find_pawn_index(white_pawns, x, y)
    if idx != -1:
        del white_pawns[idx]
        return "pawn_white"

    idx = find_rook_index(black_rooks, x, y)
    if idx != -1:
        del black_rooks[idx]
        return "rook_black"

    idx = find_rook_index(white_rooks, x, y)
    if idx != -1:
        del white_rooks[idx]
        return "rook_white"

    idx = find_knight_index(black_knights, x, y)
    if idx != -1:
        del black_knights[idx]
        return "knight_black"

    idx = find_knight_index(white_knights, x, y)
    if idx != -1:
        del white_knights[idx]
        return "knight_white"

    idx = find_queen_index(black_queens, x, y)
    if idx != -1:
        del black_queens[idx]
        return "queen_black"

    idx = find_queen_index(white_queens, x, y)
    if idx != -1:
        del white_queens[idx]
        return "queen_white"

    return ""


def path_clear_straight(from_x: int, from_y: int, to_x: int, to_y: int):
    # Nur gleiche Zeile ODER gleiche Spalte erlaubt.
    if from_x != to_x and from_y != to_y:
        return False

    if from_x == to_x and from_y == to_y:
        return False

    if from_x == to_x:
        step = 1 if to_y > from_y else -1
        y = from_y + step
        while y != to_y:
            if cell_occupied(from_x, y):
                print(
                    "[DEBUG rook-path-blocked]",
                    {"block_x": from_x, "block_y": y, "from": [from_x, from_y], "to": [to_x, to_y]},
                )
                return False
            y += step
        return True

    step = 1 if to_x > from_x else -1
    x = from_x + step
    while x != to_x:
        if cell_occupied(x, from_y):
            print(
                "[DEBUG rook-path-blocked]",
                {"block_x": x, "block_y": from_y, "from": [from_x, from_y], "to": [to_x, to_y]},
            )
            return False
        x += step
    return True


def path_clear_diagonal(from_x: int, from_y: int, to_x: int, to_y: int):
    dx = to_x - from_x
    dy = to_y - from_y

    if dx == 0 and dy == 0:
        return False

    if abs(dx) != abs(dy):
        return False

    step_x = 1 if dx > 0 else -1
    step_y = 1 if dy > 0 else -1
    x = from_x + step_x
    y = from_y + step_y
    while x != to_x and y != to_y:
        if cell_occupied(x, y):
            return False
        x += step_x
        y += step_y
    return True


@app.get("/join")
def join(client_id: str, desired_role: str = "spectator"):
    global white_player
    global black_player
    global white_last_seen
    global black_last_seen

    cleanup_disconnected_players()

    desired_role = desired_role.lower().strip()
    if desired_role not in ["white", "black", "spectator"]:
        desired_role = "spectator"

    if white_player == client_id:
        role = "white"
        assignment = "already_assigned"
        touch_player(client_id)
    elif black_player == client_id:
        role = "black"
        assignment = "already_assigned"
        touch_player(client_id)
    else:
        if desired_role == "white":
            if white_player == "":
                white_player = client_id
                white_last_seen = time.time()
                role = "white"
                assignment = "assigned"
            else:
                role = "spectator"
                assignment = "white_taken"
        elif desired_role == "black":
            if black_player == "":
                black_player = client_id
                black_last_seen = time.time()
                role = "black"
                assignment = "assigned"
            else:
                role = "spectator"
                assignment = "black_taken"
        else:
            role = "spectator"
            assignment = "spectator"

    return {
        "role": role,
        "desired_role": desired_role,
        "assignment": assignment,
        **current_state(),
    }


@app.post("/leave")
def leave(data: dict):
    cleanup_disconnected_players()

    client_id = data.get("client_id", "")

    if client_id == white_player:
        clear_all_players_and_reset()
    elif client_id == black_player:
        clear_all_players_and_reset()

    return {
        "accepted": True,
        "message": "Spieler ausgeloggt.",
        **current_state(),
    }


@app.get("/leave")
def leave_get(client_id: str):
    return leave({"client_id": client_id})


@app.get("/state")
def get_state(client_id: str = ""):
    if client_id != "":
        touch_player(client_id)
    return current_state()


@app.post("/move")
def move(data: dict):
    global current_turn
    global white_player
    global black_player

    client_id = data["client_id"]
    color = data["color"]
    x = data["x"]
    y = data["y"]
    from_x = data.get("from_x")
    from_y = data.get("from_y")

    accepted = False
    message = "Ungültiger Zug."

    cleanup_disconnected_players()
    touch_player(client_id)

    # Spielen erst erlauben, wenn beide Farben besetzt sind.
    if white_player == "" or black_player == "":
        return {
            "accepted": False,
            "message": "Spiel startet erst, wenn Weiß und Schwarz besetzt sind.",
            **current_state(),
        }

    if x < 0 or x > 7 or y < 0 or y > 7:
        return {
            "accepted": False,
            "message": "Zug außerhalb des Bretts.",
            **current_state(),
        }

    # Zugreihenfolge erzwingen
    if current_turn == "white" and color not in ["pawn_white", "rook_white", "knight_white", "queen_white"]:
        message = "Weiß ist am Zug."
    elif current_turn == "black" and color not in ["pawn_black", "rook_black", "knight_black", "queen_black"]:
        message = "Schwarz ist am Zug."

    # Schwarzer Bauer: Richtung Gegner (nach unten, y+1)
    elif color == "pawn_black":
        if client_id != black_player:
            message = "Nur der schwarze Spieler darf schwarze Bauern bewegen."
        elif from_x is None or from_y is None:
            message = "Quellfeld fehlt für schwarzen Bauern."
        else:
            idx = find_pawn_index(black_pawns, from_x, from_y)
            if idx == -1:
                message = "Schwarzer Bauer auf Quellfeld nicht gefunden."
            elif from_y == 7:
                message = "Schwarzer Bauer steht am Rand und kann nicht mehr ziehen."
            else:
                one_step_y = from_y + 1
                two_step_y = from_y + 2
                is_forward_one = (x == from_x and y == one_step_y)
                is_forward_two = (x == from_x and from_y == 1 and y == two_step_y)
                is_capture = (y == one_step_y and (x == from_x - 1 or x == from_x + 1))

                if is_forward_one:
                    if cell_occupied(x, y):
                        message = "Vor dem Bauern steht eine Figur."
                    else:
                        black_pawns[idx]["x"] = x
                        black_pawns[idx]["y"] = y
                        accepted = True
                        message = "Schwarzer Bauer wurde bewegt."
                elif is_forward_two:
                    if cell_occupied(from_x, one_step_y) or cell_occupied(x, y):
                        message = "Der Zwei-Felder-Zug ist blockiert."
                    else:
                        black_pawns[idx]["x"] = x
                        black_pawns[idx]["y"] = y
                        accepted = True
                        message = "Schwarzer Bauer wurde 2 Felder bewegt."
                elif is_capture:
                    target_piece = get_piece_at(x, y)
                    if target_piece not in ["pawn_white", "rook_white", "knight_white", "queen_white"]:
                        message = "Diagonal kann nur geschlagen werden, wenn dort eine weiße Figur steht."
                    else:
                        remove_piece_at(x, y)
                        black_pawns[idx]["x"] = x
                        black_pawns[idx]["y"] = y
                        accepted = True
                        message = "Schwarzer Bauer hat geschlagen."
                else:
                    message = "Ungültiger Zug für schwarzen Bauern."

    # Weißer Bauer: Richtung Gegner (nach oben, y-1)
    elif color == "pawn_white":
        if client_id != white_player:
            message = "Nur der weiße Spieler darf weiße Bauern bewegen."
        elif from_x is None or from_y is None:
            message = "Quellfeld fehlt für weißen Bauern."
        else:
            idx = find_pawn_index(white_pawns, from_x, from_y)
            if idx == -1:
                message = "Weißer Bauer auf Quellfeld nicht gefunden."
            elif from_y == 0:
                message = "Weißer Bauer steht am Rand und kann nicht mehr ziehen."
            else:
                one_step_y = from_y - 1
                two_step_y = from_y - 2
                is_forward_one = (x == from_x and y == one_step_y)
                is_forward_two = (x == from_x and from_y == 6 and y == two_step_y)
                is_capture = (y == one_step_y and (x == from_x - 1 or x == from_x + 1))

                if is_forward_one:
                    if cell_occupied(x, y):
                        message = "Vor dem Bauern steht eine Figur."
                    else:
                        white_pawns[idx]["x"] = x
                        white_pawns[idx]["y"] = y
                        accepted = True
                        message = "Weißer Bauer wurde bewegt."
                elif is_forward_two:
                    if cell_occupied(from_x, one_step_y) or cell_occupied(x, y):
                        message = "Der Zwei-Felder-Zug ist blockiert."
                    else:
                        white_pawns[idx]["x"] = x
                        white_pawns[idx]["y"] = y
                        accepted = True
                        message = "Weißer Bauer wurde 2 Felder bewegt."
                elif is_capture:
                    target_piece = get_piece_at(x, y)
                    if target_piece not in ["pawn_black", "rook_black", "knight_black", "queen_black"]:
                        message = "Diagonal kann nur geschlagen werden, wenn dort eine schwarze Figur steht."
                    else:
                        remove_piece_at(x, y)
                        white_pawns[idx]["x"] = x
                        white_pawns[idx]["y"] = y
                        accepted = True
                        message = "Weißer Bauer hat geschlagen."
                else:
                    message = "Ungültiger Zug für weißen Bauern."

    # Schwarzer Turm: horizontal/vertikal, bis vor Hindernis.
    elif color == "rook_black":
        if client_id != black_player:
            message = "Nur der schwarze Spieler darf schwarze Türme bewegen."
        elif from_x is None or from_y is None:
            message = "Quellfeld fehlt für schwarzen Turm."
        else:
            idx = find_rook_index(black_rooks, from_x, from_y)
            target_piece = get_piece_at(x, y)
            print(
                "[DEBUG rook-black-attempt]",
                {
                    "from": [from_x, from_y],
                    "to": [x, y],
                    "target_piece": target_piece,
                    "turn": current_turn,
                    "client_id": client_id,
                },
            )
            if idx == -1:
                message = "Schwarzer Turm auf Quellfeld nicht gefunden."
            elif not path_clear_straight(from_x, from_y, x, y):
                message = "Turm darf nur waagerecht/senkrecht und nicht durch Figuren ziehen."
            else:
                if target_piece in ["pawn_black", "rook_black", "knight_black", "queen_black"]:
                    print(
                        "[DEBUG rook-black-rejected-own-piece]",
                        {"to": [x, y], "target_piece": target_piece},
                    )
                    message = "Eigene Figur blockiert das Zielfeld."
                else:
                    if target_piece != "":
                        captured = remove_piece_at(x, y)
                        print(
                            "[DEBUG rook-black-capture]",
                            {"to": [x, y], "captured": captured},
                        )
                    black_rooks[idx]["x"] = x
                    black_rooks[idx]["y"] = y
                    accepted = True
                    if target_piece == "":
                        message = "Schwarzer Turm wurde bewegt."
                    else:
                        message = "Schwarzer Turm hat geschlagen."

    # Weißer Turm: horizontal/vertikal, bis vor Hindernis.
    elif color == "rook_white":
        if client_id != white_player:
            message = "Nur der weiße Spieler darf weiße Türme bewegen."
        elif from_x is None or from_y is None:
            message = "Quellfeld fehlt für weißen Turm."
        else:
            idx = find_rook_index(white_rooks, from_x, from_y)
            target_piece = get_piece_at(x, y)
            print(
                "[DEBUG rook-white-attempt]",
                {
                    "from": [from_x, from_y],
                    "to": [x, y],
                    "target_piece": target_piece,
                    "turn": current_turn,
                    "client_id": client_id,
                },
            )
            if idx == -1:
                message = "Weißer Turm auf Quellfeld nicht gefunden."
            elif not path_clear_straight(from_x, from_y, x, y):
                message = "Turm darf nur waagerecht/senkrecht und nicht durch Figuren ziehen."
            else:
                if target_piece in ["pawn_white", "rook_white", "knight_white", "queen_white"]:
                    print(
                        "[DEBUG rook-white-rejected-own-piece]",
                        {"to": [x, y], "target_piece": target_piece},
                    )
                    message = "Eigene Figur blockiert das Zielfeld."
                else:
                    if target_piece != "":
                        captured = remove_piece_at(x, y)
                        print(
                            "[DEBUG rook-white-capture]",
                            {"to": [x, y], "captured": captured},
                        )
                    white_rooks[idx]["x"] = x
                    white_rooks[idx]["y"] = y
                    accepted = True
                    if target_piece == "":
                        message = "Weißer Turm wurde bewegt."
                    else:
                        message = "Weißer Turm hat geschlagen."

    # Schwarzes Pferd: L-Zug, darf springen.
    elif color == "knight_black":
        if client_id != black_player:
            message = "Nur der schwarze Spieler darf schwarze Pferde bewegen."
        elif from_x is None or from_y is None:
            message = "Quellfeld fehlt für schwarzes Pferd."
        else:
            idx = find_knight_index(black_knights, from_x, from_y)
            if idx == -1:
                message = "Schwarzes Pferd auf Quellfeld nicht gefunden."
            else:
                dx = abs(x - from_x)
                dy = abs(y - from_y)
                is_l_move = (dx == 2 and dy == 1) or (dx == 1 and dy == 2)
                if not is_l_move:
                    message = "Pferd muss im L ziehen (2+1)."
                else:
                    target_piece = get_piece_at(x, y)
                    if target_piece in ["pawn_black", "rook_black", "knight_black", "queen_black"]:
                        message = "Eigene Figur blockiert das Zielfeld."
                    else:
                        if target_piece != "":
                            remove_piece_at(x, y)
                            message = "Schwarzes Pferd hat geschlagen."
                        else:
                            message = "Schwarzes Pferd wurde bewegt."
                        black_knights[idx]["x"] = x
                        black_knights[idx]["y"] = y
                        accepted = True

    # Weißes Pferd: L-Zug, darf springen.
    elif color == "knight_white":
        if client_id != white_player:
            message = "Nur der weiße Spieler darf weiße Pferde bewegen."
        elif from_x is None or from_y is None:
            message = "Quellfeld fehlt für weißes Pferd."
        else:
            idx = find_knight_index(white_knights, from_x, from_y)
            if idx == -1:
                message = "Weißes Pferd auf Quellfeld nicht gefunden."
            else:
                dx = abs(x - from_x)
                dy = abs(y - from_y)
                is_l_move = (dx == 2 and dy == 1) or (dx == 1 and dy == 2)
                if not is_l_move:
                    message = "Pferd muss im L ziehen (2+1)."
                else:
                    target_piece = get_piece_at(x, y)
                    if target_piece in ["pawn_white", "rook_white", "knight_white", "queen_white"]:
                        message = "Eigene Figur blockiert das Zielfeld."
                    else:
                        if target_piece != "":
                            remove_piece_at(x, y)
                            message = "Weißes Pferd hat geschlagen."
                        else:
                            message = "Weißes Pferd wurde bewegt."
                        white_knights[idx]["x"] = x
                        white_knights[idx]["y"] = y
                        accepted = True

    # Schwarze Dame: wie Turm + Läufer
    elif color == "queen_black":
        if client_id != black_player:
            message = "Nur der schwarze Spieler darf schwarze Damen bewegen."
        elif from_x is None or from_y is None:
            message = "Quellfeld fehlt für schwarze Dame."
        else:
            idx = find_queen_index(black_queens, from_x, from_y)
            if idx == -1:
                message = "Schwarze Dame auf Quellfeld nicht gefunden."
            else:
                is_straight = path_clear_straight(from_x, from_y, x, y)
                is_diagonal = path_clear_diagonal(from_x, from_y, x, y)
                if not is_straight and not is_diagonal:
                    message = "Dame darf nur waagerecht, senkrecht oder diagonal ziehen und nicht durch Figuren ziehen."
                else:
                    target_piece = get_piece_at(x, y)
                    if target_piece in ["pawn_black", "rook_black", "knight_black", "queen_black"]:
                        message = "Eigene Figur blockiert das Zielfeld."
                    else:
                        if target_piece != "":
                            remove_piece_at(x, y)
                            message = "Schwarze Dame hat geschlagen."
                        else:
                            message = "Schwarze Dame wurde bewegt."
                        black_queens[idx]["x"] = x
                        black_queens[idx]["y"] = y
                        accepted = True

    # Weiße Dame: wie Turm + Läufer
    elif color == "queen_white":
        if client_id != white_player:
            message = "Nur der weiße Spieler darf weiße Damen bewegen."
        elif from_x is None or from_y is None:
            message = "Quellfeld fehlt für weiße Dame."
        else:
            idx = find_queen_index(white_queens, from_x, from_y)
            if idx == -1:
                message = "Weiße Dame auf Quellfeld nicht gefunden."
            else:
                is_straight = path_clear_straight(from_x, from_y, x, y)
                is_diagonal = path_clear_diagonal(from_x, from_y, x, y)
                if not is_straight and not is_diagonal:
                    message = "Dame darf nur waagerecht, senkrecht oder diagonal ziehen und nicht durch Figuren ziehen."
                else:
                    target_piece = get_piece_at(x, y)
                    if target_piece in ["pawn_white", "rook_white", "knight_white", "queen_white"]:
                        message = "Eigene Figur blockiert das Zielfeld."
                    else:
                        if target_piece != "":
                            remove_piece_at(x, y)
                            message = "Weiße Dame hat geschlagen."
                        else:
                            message = "Weiße Dame wurde bewegt."
                        white_queens[idx]["x"] = x
                        white_queens[idx]["y"] = y
                        accepted = True

    else:
        message = "Unbekannte Figur."

    if accepted:
        current_turn = "black" if current_turn == "white" else "white"

    return {
        "accepted": accepted,
        "message": message,
        **current_state(),
    }


@app.post("/reset_round")
def reset_round(data: dict):
    global white_score
    global black_score

    client_id = data.get("client_id", "")

    cleanup_disconnected_players()
    touch_player(client_id)

    if client_id == white_player:
        black_score += 1
        message = "Runde zurückgesetzt. Punkt für Schwarz."
        accepted = True
    elif client_id == black_player:
        white_score += 1
        message = "Runde zurückgesetzt. Punkt für Weiß."
        accepted = True
    else:
        message = "Nur Weiß oder Schwarz dürfen die Runde zurücksetzen."
        accepted = False

    if accepted:
        reset_positions()

    return {
        "accepted": accepted,
        "message": message,
        **current_state(),
    }
