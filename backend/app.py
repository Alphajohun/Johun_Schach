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

# Läufer wie im Schach auf c/f-Linien
black_bishops = [{"x": 2, "y": 0}, {"x": 5, "y": 0}]
white_bishops = [{"x": 2, "y": 7}, {"x": 5, "y": 7}]

# Damen auf d8 (schwarz) und d1 (weiß)
black_queens = [{"x": 3, "y": 0}]
white_queens = [{"x": 3, "y": 7}]

# Könige auf e8 (schwarz) und e1 (weiß)
black_kings = [{"x": 4, "y": 0}]
white_kings = [{"x": 4, "y": 7}]

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
round_event = ""
round_event_until = 0.0
en_passant = {"active": False, "by": "", "capture_x": -1, "capture_y": -1, "pawn_x": -1, "pawn_y": -1}
last_move = None


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
    event_text = ""
    if round_event != "" and time.time() < round_event_until:
        event_text = round_event
    return {
        "pawns_black": black_pawns,
        "pawns_white": white_pawns,
        "rooks_black": black_rooks,
        "rooks_white": white_rooks,
        "knights_black": black_knights,
        "knights_white": white_knights,
        "bishops_black": black_bishops,
        "bishops_white": white_bishops,
        "queens_black": black_queens,
        "queens_white": white_queens,
        "kings_black": black_kings,
        "kings_white": white_kings,
        "score": {"white": white_score, "black": black_score},
        "turn": current_turn,
        "round_event": event_text,
        "last_move": last_move,
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
    global black_bishops
    global white_bishops
    global black_queens
    global white_queens
    global black_kings
    global white_kings
    global en_passant
    global last_move
    global current_turn

    black_pawns = [{"x": x, "y": 1} for x in range(8)]
    white_pawns = [{"x": x, "y": 6} for x in range(8)]
    black_rooks = [{"x": 0, "y": 0}, {"x": 7, "y": 0}]
    white_rooks = [{"x": 0, "y": 7}, {"x": 7, "y": 7}]
    black_knights = [{"x": 1, "y": 0}, {"x": 6, "y": 0}]
    white_knights = [{"x": 1, "y": 7}, {"x": 6, "y": 7}]
    black_bishops = [{"x": 2, "y": 0}, {"x": 5, "y": 0}]
    white_bishops = [{"x": 2, "y": 7}, {"x": 5, "y": 7}]
    black_queens = [{"x": 3, "y": 0}]
    white_queens = [{"x": 3, "y": 7}]
    black_kings = [{"x": 4, "y": 0}]
    white_kings = [{"x": 4, "y": 7}]
    en_passant = {"active": False, "by": "", "capture_x": -1, "capture_y": -1, "pawn_x": -1, "pawn_y": -1}
    last_move = None
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


def find_bishop_index(bishops: list, x: int, y: int):
    for idx, t in enumerate(bishops):
        if t["x"] == x and t["y"] == y:
            return idx
    return -1


def find_king_index(kings: list, x: int, y: int):
    for idx, t in enumerate(kings):
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

    for idx, t in enumerate(black_bishops):
        if ignore_kind == "bishop_black" and idx == ignore_index:
            continue
        if t["x"] == x and t["y"] == y:
            return True

    for idx, t in enumerate(white_bishops):
        if ignore_kind == "bishop_white" and idx == ignore_index:
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

    for idx, t in enumerate(black_kings):
        if ignore_kind == "king_black" and idx == ignore_index:
            continue
        if t["x"] == x and t["y"] == y:
            return True

    for idx, t in enumerate(white_kings):
        if ignore_kind == "king_white" and idx == ignore_index:
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

    for t in black_bishops:
        if t["x"] == x and t["y"] == y:
            return "bishop_black"

    for t in white_bishops:
        if t["x"] == x and t["y"] == y:
            return "bishop_white"

    for t in black_queens:
        if t["x"] == x and t["y"] == y:
            return "queen_black"

    for t in white_queens:
        if t["x"] == x and t["y"] == y:
            return "queen_white"

    for t in black_kings:
        if t["x"] == x and t["y"] == y:
            return "king_black"

    for t in white_kings:
        if t["x"] == x and t["y"] == y:
            return "king_white"

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

    idx = find_bishop_index(black_bishops, x, y)
    if idx != -1:
        del black_bishops[idx]
        return "bishop_black"

    idx = find_bishop_index(white_bishops, x, y)
    if idx != -1:
        del white_bishops[idx]
        return "bishop_white"

    idx = find_queen_index(black_queens, x, y)
    if idx != -1:
        del black_queens[idx]
        return "queen_black"

    idx = find_queen_index(white_queens, x, y)
    if idx != -1:
        del white_queens[idx]
        return "queen_white"

    idx = find_king_index(black_kings, x, y)
    if idx != -1:
        del black_kings[idx]
        return "king_black"

    idx = find_king_index(white_kings, x, y)
    if idx != -1:
        del white_kings[idx]
        return "king_white"

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


def get_king_position(side: str):
    kings = white_kings if side == "white" else black_kings
    if len(kings) == 0:
        return None
    return kings[0]["x"], kings[0]["y"]


def is_square_attacked_by(attacker_side: str, x: int, y: int):
    if attacker_side == "white":
        for p in white_pawns:
            if (p["x"] - 1 == x or p["x"] + 1 == x) and p["y"] - 1 == y:
                return True
        for r in white_rooks:
            if path_clear_straight(r["x"], r["y"], x, y):
                return True
        for n in white_knights:
            dx = abs(n["x"] - x)
            dy = abs(n["y"] - y)
            if (dx == 2 and dy == 1) or (dx == 1 and dy == 2):
                return True
        for b in white_bishops:
            if path_clear_diagonal(b["x"], b["y"], x, y):
                return True
        for q in white_queens:
            if path_clear_straight(q["x"], q["y"], x, y) or path_clear_diagonal(q["x"], q["y"], x, y):
                return True
        for k in white_kings:
            if max(abs(k["x"] - x), abs(k["y"] - y)) == 1:
                return True
    else:
        for p in black_pawns:
            if (p["x"] - 1 == x or p["x"] + 1 == x) and p["y"] + 1 == y:
                return True
        for r in black_rooks:
            if path_clear_straight(r["x"], r["y"], x, y):
                return True
        for n in black_knights:
            dx = abs(n["x"] - x)
            dy = abs(n["y"] - y)
            if (dx == 2 and dy == 1) or (dx == 1 and dy == 2):
                return True
        for b in black_bishops:
            if path_clear_diagonal(b["x"], b["y"], x, y):
                return True
        for q in black_queens:
            if path_clear_straight(q["x"], q["y"], x, y) or path_clear_diagonal(q["x"], q["y"], x, y):
                return True
        for k in black_kings:
            if max(abs(k["x"] - x), abs(k["y"] - y)) == 1:
                return True
    return False


def is_in_check(side: str):
    king_pos = get_king_position(side)
    if king_pos is None:
        return False
    enemy_side = "black" if side == "white" else "white"
    return is_square_attacked_by(enemy_side, king_pos[0], king_pos[1])


def piece_entries_for_side(side: str):
    if side == "white":
        return [
            ("pawn_white", white_pawns),
            ("rook_white", white_rooks),
            ("knight_white", white_knights),
            ("bishop_white", white_bishops),
            ("queen_white", white_queens),
            ("king_white", white_kings),
        ]
    return [
        ("pawn_black", black_pawns),
        ("rook_black", black_rooks),
        ("knight_black", black_knights),
        ("bishop_black", black_bishops),
        ("queen_black", black_queens),
        ("king_black", black_kings),
    ]


def pseudo_legal_move(color: str, from_x: int, from_y: int, to_x: int, to_y: int):
    if to_x < 0 or to_x > 7 or to_y < 0 or to_y > 7:
        return False
    if from_x == to_x and from_y == to_y:
        return False

    target_piece = get_piece_at(to_x, to_y)

    if color.endswith("_white") and target_piece.endswith("_white"):
        return False
    if color.endswith("_black") and target_piece.endswith("_black"):
        return False
    if target_piece in ["king_white", "king_black"]:
        return False

    if color == "pawn_white":
        one = from_y - 1
        two = from_y - 2
        if to_x == from_x and to_y == one and target_piece == "":
            return True
        if to_x == from_x and from_y == 6 and to_y == two and target_piece == "" and not cell_occupied(from_x, one):
            return True
        if to_y == one and (to_x == from_x - 1 or to_x == from_x + 1) and target_piece != "" and target_piece.endswith("_black"):
            return True
        if (
            to_y == one
            and (to_x == from_x - 1 or to_x == from_x + 1)
            and target_piece == ""
            and en_passant["active"]
            and en_passant["by"] == "white"
            and en_passant["capture_x"] == to_x
            and en_passant["capture_y"] == to_y
        ):
            return True
        return False

    if color == "pawn_black":
        one = from_y + 1
        two = from_y + 2
        if to_x == from_x and to_y == one and target_piece == "":
            return True
        if to_x == from_x and from_y == 1 and to_y == two and target_piece == "" and not cell_occupied(from_x, one):
            return True
        if to_y == one and (to_x == from_x - 1 or to_x == from_x + 1) and target_piece != "" and target_piece.endswith("_white"):
            return True
        if (
            to_y == one
            and (to_x == from_x - 1 or to_x == from_x + 1)
            and target_piece == ""
            and en_passant["active"]
            and en_passant["by"] == "black"
            and en_passant["capture_x"] == to_x
            and en_passant["capture_y"] == to_y
        ):
            return True
        return False

    if color in ["rook_white", "rook_black"]:
        return path_clear_straight(from_x, from_y, to_x, to_y)

    if color in ["bishop_white", "bishop_black"]:
        return path_clear_diagonal(from_x, from_y, to_x, to_y)

    if color in ["queen_white", "queen_black"]:
        return path_clear_straight(from_x, from_y, to_x, to_y) or path_clear_diagonal(from_x, from_y, to_x, to_y)

    if color in ["knight_white", "knight_black"]:
        dx = abs(to_x - from_x)
        dy = abs(to_y - from_y)
        return (dx == 2 and dy == 1) or (dx == 1 and dy == 2)

    if color in ["king_white", "king_black"]:
        return max(abs(to_x - from_x), abs(to_y - from_y)) == 1

    return False


def move_piece_no_validation(color: str, from_x: int, from_y: int, to_x: int, to_y: int):
    target_piece = get_piece_at(to_x, to_y)
    if target_piece != "":
        remove_piece_at(to_x, to_y)

    if color == "pawn_white" and target_piece == "" and en_passant["active"] and en_passant["by"] == "white":
        if en_passant["capture_x"] == to_x and en_passant["capture_y"] == to_y:
            remove_piece_at(en_passant["pawn_x"], en_passant["pawn_y"])
    if color == "pawn_black" and target_piece == "" and en_passant["active"] and en_passant["by"] == "black":
        if en_passant["capture_x"] == to_x and en_passant["capture_y"] == to_y:
            remove_piece_at(en_passant["pawn_x"], en_passant["pawn_y"])

    if color == "pawn_white":
        idx = find_pawn_index(white_pawns, from_x, from_y)
        if idx != -1:
            white_pawns[idx]["x"] = to_x
            white_pawns[idx]["y"] = to_y
    elif color == "pawn_black":
        idx = find_pawn_index(black_pawns, from_x, from_y)
        if idx != -1:
            black_pawns[idx]["x"] = to_x
            black_pawns[idx]["y"] = to_y
    elif color == "rook_white":
        idx = find_rook_index(white_rooks, from_x, from_y)
        if idx != -1:
            white_rooks[idx]["x"] = to_x
            white_rooks[idx]["y"] = to_y
    elif color == "rook_black":
        idx = find_rook_index(black_rooks, from_x, from_y)
        if idx != -1:
            black_rooks[idx]["x"] = to_x
            black_rooks[idx]["y"] = to_y
    elif color == "knight_white":
        idx = find_knight_index(white_knights, from_x, from_y)
        if idx != -1:
            white_knights[idx]["x"] = to_x
            white_knights[idx]["y"] = to_y
    elif color == "knight_black":
        idx = find_knight_index(black_knights, from_x, from_y)
        if idx != -1:
            black_knights[idx]["x"] = to_x
            black_knights[idx]["y"] = to_y
    elif color == "bishop_white":
        idx = find_bishop_index(white_bishops, from_x, from_y)
        if idx != -1:
            white_bishops[idx]["x"] = to_x
            white_bishops[idx]["y"] = to_y
    elif color == "bishop_black":
        idx = find_bishop_index(black_bishops, from_x, from_y)
        if idx != -1:
            black_bishops[idx]["x"] = to_x
            black_bishops[idx]["y"] = to_y
    elif color == "queen_white":
        idx = find_queen_index(white_queens, from_x, from_y)
        if idx != -1:
            white_queens[idx]["x"] = to_x
            white_queens[idx]["y"] = to_y
    elif color == "queen_black":
        idx = find_queen_index(black_queens, from_x, from_y)
        if idx != -1:
            black_queens[idx]["x"] = to_x
            black_queens[idx]["y"] = to_y
    elif color == "king_white":
        idx = find_king_index(white_kings, from_x, from_y)
        if idx != -1:
            white_kings[idx]["x"] = to_x
            white_kings[idx]["y"] = to_y
    elif color == "king_black":
        idx = find_king_index(black_kings, from_x, from_y)
        if idx != -1:
            black_kings[idx]["x"] = to_x
            black_kings[idx]["y"] = to_y


def restore_snapshot(snapshot: dict):
    global black_pawns, white_pawns, black_rooks, white_rooks
    global black_knights, white_knights, black_bishops, white_bishops
    global black_queens, white_queens, black_kings, white_kings
    global en_passant

    black_pawns = [p.copy() for p in snapshot["black_pawns"]]
    white_pawns = [p.copy() for p in snapshot["white_pawns"]]
    black_rooks = [p.copy() for p in snapshot["black_rooks"]]
    white_rooks = [p.copy() for p in snapshot["white_rooks"]]
    black_knights = [p.copy() for p in snapshot["black_knights"]]
    white_knights = [p.copy() for p in snapshot["white_knights"]]
    black_bishops = [p.copy() for p in snapshot["black_bishops"]]
    white_bishops = [p.copy() for p in snapshot["white_bishops"]]
    black_queens = [p.copy() for p in snapshot["black_queens"]]
    white_queens = [p.copy() for p in snapshot["white_queens"]]
    black_kings = [p.copy() for p in snapshot["black_kings"]]
    white_kings = [p.copy() for p in snapshot["white_kings"]]
    en_passant = snapshot["en_passant"].copy()


def has_any_legal_move(side: str):
    for color, pieces in piece_entries_for_side(side):
        for p in pieces:
            from_x = p["x"]
            from_y = p["y"]
            for to_y in range(8):
                for to_x in range(8):
                    if not pseudo_legal_move(color, from_x, from_y, to_x, to_y):
                        continue
                    snapshot = {
                        "black_pawns": [q.copy() for q in black_pawns],
                        "white_pawns": [q.copy() for q in white_pawns],
                        "black_rooks": [q.copy() for q in black_rooks],
                        "white_rooks": [q.copy() for q in white_rooks],
                        "black_knights": [q.copy() for q in black_knights],
                        "white_knights": [q.copy() for q in white_knights],
                        "black_bishops": [q.copy() for q in black_bishops],
                        "white_bishops": [q.copy() for q in white_bishops],
                        "black_queens": [q.copy() for q in black_queens],
                        "white_queens": [q.copy() for q in white_queens],
                        "black_kings": [q.copy() for q in black_kings],
                        "white_kings": [q.copy() for q in white_kings],
                        "en_passant": en_passant.copy(),
                    }
                    move_piece_no_validation(color, from_x, from_y, to_x, to_y)
                    still_in_check = is_in_check(side)
                    restore_snapshot(snapshot)
                    if not still_in_check:
                        return True
    return False


def insufficient_material(side: str):
    if side == "white":
        if len(white_pawns) > 0 or len(white_rooks) > 0 or len(white_queens) > 0:
            return False
        return (len(white_bishops) + len(white_knights)) <= 1
    if len(black_pawns) > 0 or len(black_rooks) > 0 or len(black_queens) > 0:
        return False
    return (len(black_bishops) + len(black_knights)) <= 1


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
    global last_move
    global white_score
    global black_score
    global round_event
    global round_event_until
    global black_pawns
    global white_pawns
    global black_rooks
    global white_rooks
    global black_knights
    global white_knights
    global black_bishops
    global white_bishops
    global black_queens
    global white_queens
    global black_kings
    global white_kings
    global en_passant

    client_id = data["client_id"]
    color = data["color"]
    x = data["x"]
    y = data["y"]
    from_x = data.get("from_x")
    from_y = data.get("from_y")
    promotion = data.get("promotion", "")
    snapshot = {
        "black_pawns": [p.copy() for p in black_pawns],
        "white_pawns": [p.copy() for p in white_pawns],
        "black_rooks": [p.copy() for p in black_rooks],
        "white_rooks": [p.copy() for p in white_rooks],
        "black_knights": [p.copy() for p in black_knights],
        "white_knights": [p.copy() for p in white_knights],
        "black_bishops": [p.copy() for p in black_bishops],
        "white_bishops": [p.copy() for p in white_bishops],
        "black_queens": [p.copy() for p in black_queens],
        "white_queens": [p.copy() for p in white_queens],
        "black_kings": [p.copy() for p in black_kings],
        "white_kings": [p.copy() for p in white_kings],
        "en_passant": en_passant.copy(),
    }

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
    if current_turn == "white" and color not in ["pawn_white", "rook_white", "knight_white", "bishop_white", "queen_white", "king_white"]:
        message = "Weiß ist am Zug."
    elif current_turn == "black" and color not in ["pawn_black", "rook_black", "knight_black", "bishop_black", "queen_black", "king_black"]:
        message = "Schwarz ist am Zug."
    elif (color.endswith("_white") and get_piece_at(x, y) == "king_black") or (color.endswith("_black") and get_piece_at(x, y) == "king_white"):
        message = "Der König kann nicht geschlagen werden."

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
                    is_en_passant = (
                        target_piece == ""
                        and en_passant["active"]
                        and en_passant["by"] == "black"
                        and en_passant["capture_x"] == x
                        and en_passant["capture_y"] == y
                    )
                    if target_piece not in ["pawn_white", "rook_white", "knight_white", "bishop_white", "queen_white"] and not is_en_passant:
                        message = "Diagonal kann nur geschlagen werden, wenn dort eine weiße Figur steht."
                    else:
                        if is_en_passant:
                            remove_piece_at(en_passant["pawn_x"], en_passant["pawn_y"])
                        else:
                            remove_piece_at(x, y)
                        black_pawns[idx]["x"] = x
                        black_pawns[idx]["y"] = y
                        accepted = True
                        message = "Schwarzer Bauer hat geschlagen."
                else:
                    message = "Ungültiger Zug für schwarzen Bauern."

                if accepted and black_pawns[idx]["y"] == 7:
                    if promotion not in ["queen", "rook", "bishop", "knight"]:
                        accepted = False
                        message = "Bauernumwandlung benötigt: queen, rook, bishop oder knight."
                        restore_snapshot(snapshot)
                    else:
                        px = black_pawns[idx]["x"]
                        py = black_pawns[idx]["y"]
                        del black_pawns[idx]
                        if promotion == "queen":
                            black_queens.append({"x": px, "y": py})
                            message = "Schwarzer Bauer wurde in eine Dame umgewandelt."
                        elif promotion == "rook":
                            black_rooks.append({"x": px, "y": py})
                            message = "Schwarzer Bauer wurde in einen Turm umgewandelt."
                        elif promotion == "bishop":
                            black_bishops.append({"x": px, "y": py})
                            message = "Schwarzer Bauer wurde in einen Läufer umgewandelt."
                        elif promotion == "knight":
                            black_knights.append({"x": px, "y": py})
                            message = "Schwarzer Bauer wurde in ein Pferd umgewandelt."

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
                    is_en_passant = (
                        target_piece == ""
                        and en_passant["active"]
                        and en_passant["by"] == "white"
                        and en_passant["capture_x"] == x
                        and en_passant["capture_y"] == y
                    )
                    if target_piece not in ["pawn_black", "rook_black", "knight_black", "bishop_black", "queen_black"] and not is_en_passant:
                        message = "Diagonal kann nur geschlagen werden, wenn dort eine schwarze Figur steht."
                    else:
                        if is_en_passant:
                            remove_piece_at(en_passant["pawn_x"], en_passant["pawn_y"])
                        else:
                            remove_piece_at(x, y)
                        white_pawns[idx]["x"] = x
                        white_pawns[idx]["y"] = y
                        accepted = True
                        message = "Weißer Bauer hat geschlagen."
                else:
                    message = "Ungültiger Zug für weißen Bauern."

                if accepted and white_pawns[idx]["y"] == 0:
                    if promotion not in ["queen", "rook", "bishop", "knight"]:
                        accepted = False
                        message = "Bauernumwandlung benötigt: queen, rook, bishop oder knight."
                        restore_snapshot(snapshot)
                    else:
                        px = white_pawns[idx]["x"]
                        py = white_pawns[idx]["y"]
                        del white_pawns[idx]
                        if promotion == "queen":
                            white_queens.append({"x": px, "y": py})
                            message = "Weißer Bauer wurde in eine Dame umgewandelt."
                        elif promotion == "rook":
                            white_rooks.append({"x": px, "y": py})
                            message = "Weißer Bauer wurde in einen Turm umgewandelt."
                        elif promotion == "bishop":
                            white_bishops.append({"x": px, "y": py})
                            message = "Weißer Bauer wurde in einen Läufer umgewandelt."
                        elif promotion == "knight":
                            white_knights.append({"x": px, "y": py})
                            message = "Weißer Bauer wurde in ein Pferd umgewandelt."

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
                if target_piece in ["pawn_black", "rook_black", "knight_black", "bishop_black", "queen_black"]:
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
                if target_piece in ["pawn_white", "rook_white", "knight_white", "bishop_white", "queen_white"]:
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
                    if target_piece in ["pawn_black", "rook_black", "knight_black", "bishop_black", "queen_black"]:
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
                    if target_piece in ["pawn_white", "rook_white", "knight_white", "bishop_white", "queen_white"]:
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

    # Schwarzer Läufer: nur diagonal, darf nicht springen.
    elif color == "bishop_black":
        if client_id != black_player:
            message = "Nur der schwarze Spieler darf schwarze Läufer bewegen."
        elif from_x is None or from_y is None:
            message = "Quellfeld fehlt für schwarzen Läufer."
        else:
            idx = find_bishop_index(black_bishops, from_x, from_y)
            if idx == -1:
                message = "Schwarzer Läufer auf Quellfeld nicht gefunden."
            elif not path_clear_diagonal(from_x, from_y, x, y):
                message = "Läufer darf nur diagonal und nicht durch Figuren ziehen."
            else:
                target_piece = get_piece_at(x, y)
                if target_piece in ["pawn_black", "rook_black", "knight_black", "bishop_black", "queen_black"]:
                    message = "Eigene Figur blockiert das Zielfeld."
                else:
                    if target_piece != "":
                        remove_piece_at(x, y)
                        message = "Schwarzer Läufer hat geschlagen."
                    else:
                        message = "Schwarzer Läufer wurde bewegt."
                    black_bishops[idx]["x"] = x
                    black_bishops[idx]["y"] = y
                    accepted = True

    # Weißer Läufer: nur diagonal, darf nicht springen.
    elif color == "bishop_white":
        if client_id != white_player:
            message = "Nur der weiße Spieler darf weiße Läufer bewegen."
        elif from_x is None or from_y is None:
            message = "Quellfeld fehlt für weißen Läufer."
        else:
            idx = find_bishop_index(white_bishops, from_x, from_y)
            if idx == -1:
                message = "Weißer Läufer auf Quellfeld nicht gefunden."
            elif not path_clear_diagonal(from_x, from_y, x, y):
                message = "Läufer darf nur diagonal und nicht durch Figuren ziehen."
            else:
                target_piece = get_piece_at(x, y)
                if target_piece in ["pawn_white", "rook_white", "knight_white", "bishop_white", "queen_white"]:
                    message = "Eigene Figur blockiert das Zielfeld."
                else:
                    if target_piece != "":
                        remove_piece_at(x, y)
                        message = "Weißer Läufer hat geschlagen."
                    else:
                        message = "Weißer Läufer wurde bewegt."
                    white_bishops[idx]["x"] = x
                    white_bishops[idx]["y"] = y
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
                    if target_piece in ["pawn_black", "rook_black", "knight_black", "bishop_black", "queen_black"]:
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
                    if target_piece in ["pawn_white", "rook_white", "knight_white", "bishop_white", "queen_white"]:
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

    elif color == "king_black":
        if client_id != black_player:
            message = "Nur der schwarze Spieler darf den schwarzen König bewegen."
        elif from_x is None or from_y is None:
            message = "Quellfeld fehlt für schwarzen König."
        else:
            idx = find_king_index(black_kings, from_x, from_y)
            if idx == -1:
                message = "Schwarzer König auf Quellfeld nicht gefunden."
            elif max(abs(x - from_x), abs(y - from_y)) != 1:
                message = "König darf nur 1 Feld in jede Richtung ziehen."
            else:
                target_piece = get_piece_at(x, y)
                if target_piece in ["pawn_black", "rook_black", "knight_black", "bishop_black", "queen_black", "king_black"]:
                    message = "Eigene Figur blockiert das Zielfeld."
                else:
                    if target_piece != "":
                        remove_piece_at(x, y)
                        message = "Schwarzer König hat geschlagen."
                    else:
                        message = "Schwarzer König wurde bewegt."
                    black_kings[idx]["x"] = x
                    black_kings[idx]["y"] = y
                    accepted = True

    elif color == "king_white":
        if client_id != white_player:
            message = "Nur der weiße Spieler darf den weißen König bewegen."
        elif from_x is None or from_y is None:
            message = "Quellfeld fehlt für weißen König."
        else:
            idx = find_king_index(white_kings, from_x, from_y)
            if idx == -1:
                message = "Weißer König auf Quellfeld nicht gefunden."
            elif max(abs(x - from_x), abs(y - from_y)) != 1:
                message = "König darf nur 1 Feld in jede Richtung ziehen."
            else:
                target_piece = get_piece_at(x, y)
                if target_piece in ["pawn_white", "rook_white", "knight_white", "bishop_white", "queen_white", "king_white"]:
                    message = "Eigene Figur blockiert das Zielfeld."
                else:
                    if target_piece != "":
                        remove_piece_at(x, y)
                        message = "Weißer König hat geschlagen."
                    else:
                        message = "Weißer König wurde bewegt."
                    white_kings[idx]["x"] = x
                    white_kings[idx]["y"] = y
                    accepted = True

    else:
        message = "Unbekannte Figur."

    if accepted:
        mover_side = "white" if color.endswith("_white") else "black"
        enemy_side = "black" if mover_side == "white" else "white"
        if is_in_check(mover_side):
            restore_snapshot(snapshot)
            accepted = False
            message = "Ungültiger Zug: König würde im Schach stehen."
        else:
            # En-Passant-Fenster verwalten: nur direkt folgender Zug.
            if color == "pawn_black" and from_y is not None and y == from_y + 2:
                en_passant = {
                    "active": True,
                    "by": "white",
                    "capture_x": x,
                    "capture_y": from_y + 1,
                    "pawn_x": x,
                    "pawn_y": y,
                }
            elif color == "pawn_white" and from_y is not None and y == from_y - 2:
                en_passant = {
                    "active": True,
                    "by": "black",
                    "capture_x": x,
                    "capture_y": from_y - 1,
                    "pawn_x": x,
                    "pawn_y": y,
                }
            else:
                en_passant = {"active": False, "by": "", "capture_x": -1, "capture_y": -1, "pawn_x": -1, "pawn_y": -1}

            # Nach erfolgreichem legalen Zug Endbedingungen für Gegenseite prüfen.
            side_to_move = enemy_side
            if insufficient_material("white") and insufficient_material("black"):
                white_score += 0.5
                black_score += 0.5
                reset_positions()
                message = "Remis durch unzureichendes Material. Beide erhalten 0.5 Punkte."
            else:
                in_check = is_in_check(side_to_move)
                has_move = has_any_legal_move(side_to_move)
                if not has_move and in_check:
                    if side_to_move == "white":
                        black_score += 1
                    else:
                        white_score += 1
                    clear_all_players_and_reset()
                    winner = "Schwarz" if side_to_move == "white" else "Weiß"
                    message = f"Schachmatt. Punkt für {winner}."
                    round_event = "SCHACHMATT"
                    round_event_until = time.time() + 5.0
                elif not has_move and not in_check:
                    white_score += 0.5
                    black_score += 0.5
                    clear_all_players_and_reset()
                    message = "Patt. Beide erhalten 0.5 Punkte."
                    round_event = "PATT"
                    round_event_until = time.time() + 5.0

    if accepted:
        current_turn = "black" if current_turn == "white" else "white"
        if from_x is not None and from_y is not None:
            last_move = {
                "from_x": from_x,
                "from_y": from_y,
                "to_x": x,
                "to_y": y,
                "color": color,
            }

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
