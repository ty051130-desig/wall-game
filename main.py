import pygame
import sys
import random
from collections import deque


# =========================================================
# SETTINGS
# =========================================================

BOARD_SIZE = 9
CELL_SIZE = 70

BOARD_X = 70
BOARD_Y = 80

WINDOW_WIDTH = 850
WINDOW_HEIGHT = 850

FPS = 60

WALL_WIDTH = 12


# =========================================================
# COLORS
# =========================================================

BACKGROUND = (235, 235, 235)

WHITE = (250, 250, 250)
BLACK = (30, 30, 30)
GRID = (150, 150, 150)

BLUE = (50, 100, 220)
RED = (220, 60, 60)

GOAL_BLUE = (220, 230, 255)
GOAL_RED = (255, 225, 225)

MOVE_COLOR = (100, 210, 130)
MOVE_HOVER_COLOR = (70, 190, 100)

WALL_COLOR = (40, 40, 40)

PREVIEW_VALID = (60, 190, 90)
PREVIEW_INVALID = (220, 70, 70)

BUTTON_COLOR = (210, 210, 210)
BUTTON_HOVER = (180, 180, 180)


# =========================================================
# INITIALIZE
# =========================================================

pygame.init()

screen = pygame.display.set_mode(
    (WINDOW_WIDTH, WINDOW_HEIGHT)
)

pygame.display.set_caption(
    "9x9 WALL GAME"
)

clock = pygame.time.Clock()


# =========================================================
# FONT
# =========================================================

font = pygame.font.SysFont(
    "Arial",
    20
)

small_font = pygame.font.SysFont(
    "Arial",
    16
)

large_font = pygame.font.SysFont(
    "Arial",
    28,
    bold=True
)

title_font = pygame.font.SysFont(
    "Arial",
    32,
    bold=True
)


# =========================================================
# PLAYERS
# =========================================================

player1 = {
    "row": 0,
    "col": 4,
    "walls": 10,
    "goal": 8
}

player2 = {
    "row": 8,
    "col": 4,
    "walls": 10,
    "goal": 0
}


# =========================================================
# WALL DATA
# =========================================================

horizontal_walls = set()
vertical_walls = set()


# =========================================================
# GAME STATE
# =========================================================

turn = 1

game_over = False

mode = "move"

scene = "title"

cpu_mode = False

cpu_level = 1


# =========================================================
# CURRENT PLAYER
# =========================================================

def get_current_player():

    if turn == 1:
        return player1

    return player2


# =========================================================
# OPPONENT
# =========================================================

def get_opponent(player):

    if player is player1:
        return player2

    return player1


# =========================================================
# CELL POSITION
# =========================================================

def cell_position(row, col):

    x = BOARD_X + col * CELL_SIZE
    y = BOARD_Y + row * CELL_SIZE

    return x, y


# =========================================================
# MOUSE TO CELL
# =========================================================

def mouse_to_cell(mouse_x, mouse_y):

    col = (mouse_x - BOARD_X) // CELL_SIZE
    row = (mouse_y - BOARD_Y) // CELL_SIZE

    if (
        0 <= row < BOARD_SIZE
        and
        0 <= col < BOARD_SIZE
    ):

        return int(row), int(col)

    return None


# =========================================================
# WALL COLLISION
# =========================================================

def blocked(row1, col1, row2, col2):

    if row2 == row1 - 1:

        boundary_row = row2

        if (
            boundary_row,
            col1
        ) in horizontal_walls:

            return True

        if (
            boundary_row,
            col1 - 1
        ) in horizontal_walls:

            return True

    elif row2 == row1 + 1:

        boundary_row = row1

        if (
            boundary_row,
            col1
        ) in horizontal_walls:

            return True

        if (
            boundary_row,
            col1 - 1
        ) in horizontal_walls:

            return True

    elif col2 == col1 - 1:

        boundary_col = col2

        if (
            row1,
            boundary_col
        ) in vertical_walls:

            return True

        if (
            row1 - 1,
            boundary_col
        ) in vertical_walls:

            return True

    elif col2 == col1 + 1:

        boundary_col = col1

        if (
            row1,
            boundary_col
        ) in vertical_walls:

            return True

        if (
            row1 - 1,
            boundary_col
        ) in vertical_walls:

            return True

    return False


# =========================================================
# NORMAL NEIGHBORS
# =========================================================

def get_neighbors(row, col):

    result = []

    directions = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1)
    ]

    for dr, dc in directions:

        nr = row + dr
        nc = col + dc

        if not (
            0 <= nr < BOARD_SIZE
            and
            0 <= nc < BOARD_SIZE
        ):

            continue

        if blocked(
            row,
            col,
            nr,
            nc
        ):

            continue

        result.append(
            (nr, nc)
        )

    return result


# =========================================================
# LEGAL MOVES
# =========================================================

def get_legal_moves(player):

    row = player["row"]
    col = player["col"]

    opponent = get_opponent(player)

    moves = []

    directions = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1)
    ]

    for dr, dc in directions:

        next_row = row + dr
        next_col = col + dc

        if not (
            0 <= next_row < BOARD_SIZE
            and
            0 <= next_col < BOARD_SIZE
        ):

            continue

        if blocked(
            row,
            col,
            next_row,
            next_col
        ):

            continue

        if not (
            next_row == opponent["row"]
            and
            next_col == opponent["col"]
        ):

            moves.append(
                (
                    next_row,
                    next_col
                )
            )

            continue

        jump_row = next_row + dr
        jump_col = next_col + dc

        if (
            0 <= jump_row < BOARD_SIZE
            and
            0 <= jump_col < BOARD_SIZE
        ):

            if not blocked(
                next_row,
                next_col,
                jump_row,
                jump_col
            ):

                moves.append(
                    (
                        jump_row,
                        jump_col
                    )
                )

                continue

        if dr != 0:

            side_positions = [
                (
                    next_row,
                    next_col - 1
                ),
                (
                    next_row,
                    next_col + 1
                )
            ]

        else:

            side_positions = [
                (
                    next_row - 1,
                    next_col
                ),
                (
                    next_row + 1,
                    next_col
                )
            ]

        for side_row, side_col in side_positions:

            if not (
                0 <= side_row < BOARD_SIZE
                and
                0 <= side_col < BOARD_SIZE
            ):

                continue

            if blocked(
                next_row,
                next_col,
                side_row,
                side_col
            ):

                continue

            if (
                side_row == opponent["row"]
                and
                side_col == opponent["col"]
            ):

                continue

            moves.append(
                (
                    side_row,
                    side_col
                )
            )

    return moves


# =========================================================
# PATH CHECK
# =========================================================

def has_path(player):

    start = (
        player["row"],
        player["col"]
    )

    goal_row = player["goal"]

    queue = deque()

    queue.append(start)

    visited = set()

    visited.add(start)

    while queue:

        row, col = queue.popleft()

        if row == goal_row:

            return True

        for nr, nc in get_neighbors(
            row,
            col
        ):

            if (
                nr,
                nc
            ) not in visited:

                visited.add(
                    (
                        nr,
                        nc
                    )
                )

                queue.append(
                    (
                        nr,
                        nc
                    )
                )

    return False


# =========================================================
# WALL VALIDATION
# =========================================================

def can_place_wall(kind, row, col):

    if kind == "H":

        if not (
            0 <= row < 8
            and
            0 <= col < 8
        ):

            return False

        if (
            row,
            col
        ) in horizontal_walls:

            return False

        if (
            row,
            col - 1
        ) in horizontal_walls:

            return False

        if (
            row,
            col + 1
        ) in horizontal_walls:

            return False

        if (
            row,
            col
        ) in vertical_walls:

            return False

        if (
            row,
            col + 1
        ) in vertical_walls:

            return False

        horizontal_walls.add(
            (
                row,
                col
            )
        )

        p1_ok = has_path(player1)
        p2_ok = has_path(player2)

        horizontal_walls.remove(
            (
                row,
                col
            )
        )

        return (
            p1_ok
            and
            p2_ok
        )

    if kind == "V":

        if not (
            0 <= row < 8
            and
            0 <= col < 8
        ):

            return False

        if (
            row,
            col
        ) in vertical_walls:

            return False

        if (
            row - 1,
            col
        ) in vertical_walls:

            return False

        if (
            row + 1,
            col
        ) in vertical_walls:

            return False

        if (
            row,
            col
        ) in horizontal_walls:

            return False

        if (
            row + 1,
            col
        ) in horizontal_walls:

            return False

        vertical_walls.add(
            (
                row,
                col
            )
        )

        p1_ok = has_path(player1)
        p2_ok = has_path(player2)

        vertical_walls.remove(
            (
                row,
                col
            )
        )

        return (
            p1_ok
            and
            p2_ok
        )

    return False

# =========================================================
# FIND WALL FROM MOUSE
# =========================================================

def wall_from_mouse(mouse_x, mouse_y):

    relative_x = mouse_x - BOARD_X
    relative_y = mouse_y - BOARD_Y

    # -----------------------------------------------------
    # 盤面外
    # -----------------------------------------------------

    if (
        relative_x < -20
        or
        relative_y < -20
        or
        relative_x > BOARD_SIZE * CELL_SIZE + 20
        or
        relative_y > BOARD_SIZE * CELL_SIZE + 20
    ):

        return None

    # -----------------------------------------------------
    # 縦のグリッド線
    # -----------------------------------------------------

    vertical_line = round(
        relative_x / CELL_SIZE
    )

    vertical_distance = abs(
        relative_x
        -
        vertical_line * CELL_SIZE
    )

    # -----------------------------------------------------
    # 横のグリッド線
    # -----------------------------------------------------

    horizontal_line = round(
        relative_y / CELL_SIZE
    )

    horizontal_distance = abs(
        relative_y
        -
        horizontal_line * CELL_SIZE
    )

    # -----------------------------------------------------
    # 壁の近くではない
    # -----------------------------------------------------

    if (
        vertical_distance > 18
        and
        horizontal_distance > 18
    ):

        return None

    # -----------------------------------------------------
    # HORIZONTAL WALL
    # -----------------------------------------------------

    if horizontal_distance <= vertical_distance:

        wall_row = horizontal_line - 1

        wall_col = int(
            relative_x // CELL_SIZE
        )

        if not (
            0 <= wall_row < 8
            and
            0 <= wall_col < 8
        ):

            return None

        return (
            "H",
            wall_row,
            wall_col
        )

    # -----------------------------------------------------
    # VERTICAL WALL
    # -----------------------------------------------------

    wall_row = int(
        relative_y // CELL_SIZE
    )

    wall_col = vertical_line - 1

    if not (
        0 <= wall_row < 8
        and
        0 <= wall_col < 8
    ):

        return None

    return (
        "V",
        wall_row,
        wall_col
    )


# =========================================================
# DRAW BOARD
# =========================================================

def draw_board():

    for row in range(BOARD_SIZE):

        for col in range(BOARD_SIZE):

            x, y = cell_position(
                row,
                col
            )

            # -------------------------------------------------
            # ゴールエリア
            # -------------------------------------------------

            if row == 0:

                color = GOAL_RED

            elif row == 8:

                color = GOAL_BLUE

            else:

                color = WHITE

            # -------------------------------------------------
            # マス
            # -------------------------------------------------

            pygame.draw.rect(
                screen,
                color,
                (
                    x,
                    y,
                    CELL_SIZE,
                    CELL_SIZE
                )
            )

            # -------------------------------------------------
            # グリッド
            # -------------------------------------------------

            pygame.draw.rect(
                screen,
                GRID,
                (
                    x,
                    y,
                    CELL_SIZE,
                    CELL_SIZE
                ),
                1
            )


# =========================================================
# DRAW COORDINATES
# =========================================================

def draw_coordinates():

    # -----------------------------------------------------
    # ROW LETTERS
    # -----------------------------------------------------

    for row in range(BOARD_SIZE):

        letter = chr(
            ord("A") + row
        )

        text = font.render(
            letter,
            True,
            BLACK
        )

        x = BOARD_X - 35

        y = (
            BOARD_Y
            + row * CELL_SIZE
            + CELL_SIZE // 2
            - text.get_height() // 2
        )

        screen.blit(
            text,
            (
                x,
                y
            )
        )

    # -----------------------------------------------------
    # COLUMN NUMBERS
    # -----------------------------------------------------

    for col in range(BOARD_SIZE):

        number = str(
            col + 1
        )

        text = font.render(
            number,
            True,
            BLACK
        )

        x = (
            BOARD_X
            + col * CELL_SIZE
            + CELL_SIZE // 2
            - text.get_width() // 2
        )

        y = BOARD_Y - 35

        screen.blit(
            text,
            (
                x,
                y
            )
        )


# =========================================================
# DRAW WALLS
# =========================================================

def draw_walls():

    # -----------------------------------------------------
    # HORIZONTAL WALLS
    # -----------------------------------------------------

    for row, col in horizontal_walls:

        x1 = (
            BOARD_X
            + col * CELL_SIZE
        )

        x2 = (
            BOARD_X
            + (col + 2) * CELL_SIZE
        )

        y = (
            BOARD_Y
            + (row + 1) * CELL_SIZE
        )

        pygame.draw.line(
            screen,
            WALL_COLOR,
            (
                x1,
                y
            ),
            (
                x2,
                y
            ),
            WALL_WIDTH
        )

    # -----------------------------------------------------
    # VERTICAL WALLS
    # -----------------------------------------------------

    for row, col in vertical_walls:

        x = (
            BOARD_X
            + (col + 1) * CELL_SIZE
        )

        y1 = (
            BOARD_Y
            + row * CELL_SIZE
        )

        y2 = (
            BOARD_Y
            + (row + 2) * CELL_SIZE
        )

        pygame.draw.line(
            screen,
            WALL_COLOR,
            (
                x,
                y1
            ),
            (
                x,
                y2
            ),
            WALL_WIDTH
        )


# =========================================================
# DRAW WALL PREVIEW
# =========================================================

def draw_wall_preview():

    if game_over:

        return

    if mode != "wall":

        return

    player = get_current_player()

    if player["walls"] <= 0:

        return

    mouse_x, mouse_y = pygame.mouse.get_pos()

    wall = wall_from_mouse(
        mouse_x,
        mouse_y
    )

    if wall is None:

        return

    kind, row, col = wall

    # -----------------------------------------------------
    # 設置可能か確認
    # -----------------------------------------------------

    valid = can_place_wall(
        kind,
        row,
        col
    )

    if valid:

        color = PREVIEW_VALID

    else:

        color = PREVIEW_INVALID

    # -----------------------------------------------------
    # HORIZONTAL PREVIEW
    # -----------------------------------------------------

    if kind == "H":

        x1 = (
            BOARD_X
            + col * CELL_SIZE
        )

        x2 = (
            BOARD_X
            + (col + 2) * CELL_SIZE
        )

        y = (
            BOARD_Y
            + (row + 1) * CELL_SIZE
        )

        pygame.draw.line(
            screen,
            color,
            (
                x1,
                y
            ),
            (
                x2,
                y
            ),
            WALL_WIDTH
        )

    # -----------------------------------------------------
    # VERTICAL PREVIEW
    # -----------------------------------------------------

    else:

        x = (
            BOARD_X
            + (col + 1) * CELL_SIZE
        )

        y1 = (
            BOARD_Y
            + row * CELL_SIZE
        )

        y2 = (
            BOARD_Y
            + (row + 2) * CELL_SIZE
        )

        pygame.draw.line(
            screen,
            color,
            (
                x,
                y1
            ),
            (
                x,
                y2
            ),
            WALL_WIDTH
        )


# =========================================================
# DRAW LEGAL MOVES
# =========================================================

def draw_legal_moves():

    if game_over:

        return

    if mode != "move":

        return

    player = get_current_player()

    moves = get_legal_moves(
        player
    )

    mouse_x, mouse_y = pygame.mouse.get_pos()

    hovered_cell = mouse_to_cell(
        mouse_x,
        mouse_y
    )

    for row, col in moves:

        x, y = cell_position(
            row,
            col
        )

        center_x = (
            x
            + CELL_SIZE // 2
        )

        center_y = (
            y
            + CELL_SIZE // 2
        )

        if hovered_cell == (
            row,
            col
        ):

            color = MOVE_HOVER_COLOR

        else:

            color = MOVE_COLOR

        pygame.draw.circle(
            screen,
            color,
            (
                center_x,
                center_y
            ),
            11
        )


# =========================================================
# DRAW PLAYER
# =========================================================

def draw_player(
    player,
    color,
    number
):

    row = player["row"]
    col = player["col"]

    x, y = cell_position(
        row,
        col
    )

    center_x = (
        x
        + CELL_SIZE // 2
    )

    center_y = (
        y
        + CELL_SIZE // 2
    )

    # -----------------------------------------------------
    # Shadow
    # -----------------------------------------------------

    pygame.draw.circle(
        screen,
        (100, 100, 100),
        (
            center_x + 3,
            center_y + 3
        ),
        25
    )

    # -----------------------------------------------------
    # Player
    # -----------------------------------------------------

    pygame.draw.circle(
        screen,
        color,
        (
            center_x,
            center_y
        ),
        24
    )

    # -----------------------------------------------------
    # Border
    # -----------------------------------------------------

    pygame.draw.circle(
        screen,
        BLACK,
        (
            center_x,
            center_y
        ),
        24,
        2
    )

    # -----------------------------------------------------
    # Number
    # -----------------------------------------------------

    text = large_font.render(
        str(number),
        True,
        WHITE
    )

    text_x = (
        center_x
        - text.get_width() // 2
    )

    text_y = (
        center_y
        - text.get_height() // 2
    )

    screen.blit(
        text,
        (
            text_x,
            text_y
        )
    )


# =========================================================
# POSITION TEXT
# =========================================================

def position_text(player):

    return (
        chr(
            ord("A")
            + player["row"]
        )
        +
        str(
            player["col"] + 1
        )
    )


# =========================================================
# DRAW INFORMATION
# =========================================================

def draw_information():

    # -----------------------------------------------------
    # TITLE
    # -----------------------------------------------------

    title = title_font.render(
        "9x9 WALL GAME",
        True,
        BLACK
    )

    screen.blit(
        title,
        (
            BOARD_X,
            20
        )
    )

    # -----------------------------------------------------
    # TURN
    # -----------------------------------------------------

    if game_over:

        if turn == 1:

            turn_text = "PLAYER 1 WINS!"

            turn_color = BLUE

        else:

            turn_text = "PLAYER 2 WINS!"

            turn_color = RED

    else:

        turn_text = (
            f"PLAYER {turn} TURN"
        )

        if turn == 1:

            turn_color = BLUE

        else:

            turn_color = RED

    turn_surface = large_font.render(
        turn_text,
        True,
        turn_color
    )

    screen.blit(
        turn_surface,
        (
            BOARD_X,
            725
        )
    )

    # -----------------------------------------------------
    # PLAYER 1 INFORMATION
    # -----------------------------------------------------

    p1_text = (
        f"P1: {position_text(player1)}"
        f"   Walls: {player1['walls']}"
    )

    p1_surface = font.render(
        p1_text,
        True,
        BLUE
    )

    screen.blit(
        p1_surface,
        (
            400,
            725
        )
    )

    # -----------------------------------------------------
    # PLAYER 2 INFORMATION
    # -----------------------------------------------------

    p2_text = (
        f"P2: {position_text(player2)}"
        f"   Walls: {player2['walls']}"
    )

    p2_surface = font.render(
        p2_text,
        True,
        RED
    )

    screen.blit(
        p2_surface,
        (
            400,
            755
        )
    )

    # -----------------------------------------------------
    # MODE
    # -----------------------------------------------------

    if mode == "move":

        mode_text = (
            "MOVE MODE  |  W: Wall Mode"
        )

    else:

        mode_text = (
            "WALL MODE  |  M: Move Mode"
        )

    mode_surface = small_font.render(
        mode_text,
        True,
        BLACK
    )

    screen.blit(
        mode_surface,
        (
            BOARD_X,
            790
        )
    )


# =========================================================
# RESET BUTTON
# =========================================================

def draw_reset_button():

    mouse_x, mouse_y = pygame.mouse.get_pos()

    button_rect = pygame.Rect(
        680,
        20,
        110,
        40
    )

    if button_rect.collidepoint(
        mouse_x,
        mouse_y
    ):

        color = BUTTON_HOVER

    else:

        color = BUTTON_COLOR

    pygame.draw.rect(
        screen,
        color,
        button_rect,
        border_radius=6
    )

    pygame.draw.rect(
        screen,
        BLACK,
        button_rect,
        2,
        border_radius=6
    )

    text = font.render(
        "RESET",
        True,
        BLACK
    )

    text_x = (
        button_rect.centerx
        - text.get_width() // 2
    )

    text_y = (
        button_rect.centery
        - text.get_height() // 2
    )

    screen.blit(
        text,
        (
            text_x,
            text_y
        )
    )

    return button_rect

# =========================================================
# MOVE PLAYER
# =========================================================

def move_player(row, col):

    global game_over

    if game_over:
        return

    if mode != "move":
        return

    player = get_current_player()

    legal_moves = get_legal_moves(player)

    if (row, col) not in legal_moves:
        return

    # -----------------------------------------------------
    # 移動
    # -----------------------------------------------------

    player["row"] = row
    player["col"] = col

    # -----------------------------------------------------
    # 勝利判定
    # -----------------------------------------------------

    if check_win(player):

        game_over = True

        return

    # -----------------------------------------------------
    # ターン交代
    # -----------------------------------------------------

    change_turn()


# =========================================================
# CHECK WIN
# =========================================================

def check_win(player):

    return (
        player["row"]
        ==
        player["goal"]
    )


# =========================================================
# PLACE WALL
# =========================================================

def place_wall():

    if game_over:
        return

    if mode != "wall":
        return

    player = get_current_player()

    if player["walls"] <= 0:
        return

    mouse_x, mouse_y = pygame.mouse.get_pos()

    wall = wall_from_mouse(
        mouse_x,
        mouse_y
    )

    if wall is None:
        return

    kind, row, col = wall

    # -----------------------------------------------------
    # 壁を置けるか確認
    # -----------------------------------------------------

    if not can_place_wall(
        kind,
        row,
        col
    ):

        return

    # -----------------------------------------------------
    # 実際に壁を設置
    # -----------------------------------------------------

    if kind == "H":

        horizontal_walls.add(
            (
                row,
                col
            )
        )

    else:

        vertical_walls.add(
            (
                row,
                col
            )
        )

    # -----------------------------------------------------
    # 壁を1枚消費
    # -----------------------------------------------------

    player["walls"] -= 1

    # -----------------------------------------------------
    # ターン交代
    # -----------------------------------------------------

    change_turn()


# =========================================================
# CHANGE TURN
# =========================================================

def change_turn():

    global turn
    global mode

    if turn == 1:

        turn = 2

    else:

        turn = 1

    # ターン交代時は移動モード

    mode = "move"


# =========================================================
# RESET GAME
# =========================================================

def reset_game():

    global turn
    global game_over
    global mode

    # -----------------------------------------------------
    # PLAYER 1
    # -----------------------------------------------------

    player1["row"] = 0
    player1["col"] = 4
    player1["walls"] = 10

    # -----------------------------------------------------
    # PLAYER 2
    # -----------------------------------------------------

    player2["row"] = 8
    player2["col"] = 4
    player2["walls"] = 10

    # -----------------------------------------------------
    # WALLS
    # -----------------------------------------------------

    horizontal_walls.clear()
    vertical_walls.clear()

    # -----------------------------------------------------
    # GAME STATE
    # -----------------------------------------------------

    turn = 1
    game_over = False
    mode = "move"


# =========================================================
# TITLE SCREEN
# =========================================================

def draw_title_screen():

    screen.fill(
        BACKGROUND
    )

    # -----------------------------------------------------
    # TITLE
    # -----------------------------------------------------

    title = title_font.render(
        "9x9 WALL GAME",
        True,
        BLACK
    )

    title_x = (
        WINDOW_WIDTH // 2
        -
        title.get_width() // 2
    )

    screen.blit(
        title,
        (
            title_x,
            150
        )
    )

    # -----------------------------------------------------
    # SUBTITLE
    # -----------------------------------------------------

    subtitle = font.render(
        "Choose Game Mode",
        True,
        BLACK
    )

    subtitle_x = (
        WINDOW_WIDTH // 2
        -
        subtitle.get_width() // 2
    )

    screen.blit(
        subtitle,
        (
            subtitle_x,
            220
        )
    )

    mouse_x, mouse_y = pygame.mouse.get_pos()

    # -----------------------------------------------------
    # PLAYER VS PLAYER
    # -----------------------------------------------------

    pvp_button = pygame.Rect(
        250,
        320,
        350,
        70
    )

    if pvp_button.collidepoint(
        mouse_x,
        mouse_y
    ):

        color = BUTTON_HOVER

    else:

        color = BUTTON_COLOR

    pygame.draw.rect(
        screen,
        color,
        pvp_button,
        border_radius=10
    )

    pygame.draw.rect(
        screen,
        BLACK,
        pvp_button,
        2,
        border_radius=10
    )

    pvp_text = font.render(
        "PLAYER vs PLAYER",
        True,
        BLACK
    )

    screen.blit(
        pvp_text,
        (
            pvp_button.centerx
            -
            pvp_text.get_width() // 2,
            pvp_button.centery
            -
            pvp_text.get_height() // 2
        )
    )

    # -----------------------------------------------------
    # PLAYER VS CPU
    # -----------------------------------------------------

    cpu_button = pygame.Rect(
        250,
        430,
        350,
        70
    )

    if cpu_button.collidepoint(
        mouse_x,
        mouse_y
    ):

        color = BUTTON_HOVER

    else:

        color = BUTTON_COLOR

    pygame.draw.rect(
        screen,
        color,
        cpu_button,
        border_radius=10
    )

    pygame.draw.rect(
        screen,
        BLACK,
        cpu_button,
        2,
        border_radius=10
    )

    cpu_text = font.render(
        "PLAYER vs CPU",
        True,
        BLACK
    )

    screen.blit(
        cpu_text,
        (
            cpu_button.centerx
            -
            cpu_text.get_width() // 2,
            cpu_button.centery
            -
            cpu_text.get_height() // 2
        )
    )

    # -----------------------------------------------------
    # CONTROLS
    # -----------------------------------------------------

    control_text = small_font.render(
        "Move: Click a green circle   |   Wall: W",
        True,
        BLACK
    )

    screen.blit(
        control_text,
        (
            WINDOW_WIDTH // 2
            -
            control_text.get_width() // 2,
            560
        )
    )

    return (
        pvp_button,
        cpu_button
    )


# =========================================================
# CPU LEVEL SCREEN
# =========================================================

def draw_cpu_level_screen():

    screen.fill(
        BACKGROUND
    )

    # -----------------------------------------------------
    # TITLE
    # -----------------------------------------------------

    title = title_font.render(
        "SELECT CPU LEVEL",
        True,
        BLACK
    )

    title_x = (
        WINDOW_WIDTH // 2
        -
        title.get_width() // 2
    )

    screen.blit(
        title,
        (
            title_x,
            150
        )
    )

    mouse_x, mouse_y = pygame.mouse.get_pos()

    # -----------------------------------------------------
    # BUTTONS
    # -----------------------------------------------------

    level1_button = pygame.Rect(
        250,
        270,
        350,
        70
    )

    level2_button = pygame.Rect(
        250,
        370,
        350,
        70
    )

    level3_button = pygame.Rect(
        250,
        470,
        350,
        70
    )

    back_button = pygame.Rect(
        330,
        590,
        190,
        50
    )

    # -----------------------------------------------------
    # LEVEL 1
    # -----------------------------------------------------

    if level1_button.collidepoint(
        mouse_x,
        mouse_y
    ):

        color = BUTTON_HOVER

    else:

        color = BUTTON_COLOR

    pygame.draw.rect(
        screen,
        color,
        level1_button,
        border_radius=10
    )

    pygame.draw.rect(
        screen,
        BLACK,
        level1_button,
        2,
        border_radius=10
    )

    level1_text = font.render(
        "LEVEL 1 - EASY",
        True,
        BLACK
    )

    screen.blit(
        level1_text,
        (
            level1_button.centerx
            -
            level1_text.get_width() // 2,
            level1_button.centery
            -
            level1_text.get_height() // 2
        )
    )

    # -----------------------------------------------------
    # LEVEL 2
    # -----------------------------------------------------

    if level2_button.collidepoint(
        mouse_x,
        mouse_y
    ):

        color = BUTTON_HOVER

    else:

        color = BUTTON_COLOR

    pygame.draw.rect(
        screen,
        color,
        level2_button,
        border_radius=10
    )

    pygame.draw.rect(
        screen,
        BLACK,
        level2_button,
        2,
        border_radius=10
    )

    level2_text = font.render(
        "LEVEL 2 - NORMAL",
        True,
        BLACK
    )

    screen.blit(
        level2_text,
        (
            level2_button.centerx
            -
            level2_text.get_width() // 2,
            level2_button.centery
            -
            level2_text.get_height() // 2
        )
    )

    # -----------------------------------------------------
    # LEVEL 3
    # -----------------------------------------------------

    if level3_button.collidepoint(
        mouse_x,
        mouse_y
    ):

        color = BUTTON_HOVER

    else:

        color = BUTTON_COLOR

    pygame.draw.rect(
        screen,
        color,
        level3_button,
        border_radius=10
    )

    pygame.draw.rect(
        screen,
        BLACK,
        level3_button,
        2,
        border_radius=10
    )

    level3_text = font.render(
        "LEVEL 3 - HARD",
        True,
        BLACK
    )

    screen.blit(
        level3_text,
        (
            level3_button.centerx
            -
            level3_text.get_width() // 2,
            level3_button.centery
            -
            level3_text.get_height() // 2
        )
    )

    # -----------------------------------------------------
    # BACK
    # -----------------------------------------------------

    if back_button.collidepoint(
        mouse_x,
        mouse_y
    ):

        color = BUTTON_HOVER

    else:

        color = BUTTON_COLOR

    pygame.draw.rect(
        screen,
        color,
        back_button,
        border_radius=8
    )

    pygame.draw.rect(
        screen,
        BLACK,
        back_button,
        2,
        border_radius=8
    )

    back_text = small_font.render(
        "BACK",
        True,
        BLACK
    )

    screen.blit(
        back_text,
        (
            back_button.centerx
            -
            back_text.get_width() // 2,
            back_button.centery
            -
            back_text.get_height() // 2
        )
    )

    return (
        level1_button,
        level2_button,
        level3_button,
        back_button
    )


# =========================================================
# CPU MOVE
# =========================================================

def cpu_move():

    global game_over

    if game_over:
        return

    cpu = player2

    legal_moves = get_legal_moves(
        cpu
    )

    if not legal_moves:
        return

    # -----------------------------------------------------
    # LEVEL 1
    # ランダム
    # -----------------------------------------------------

    if cpu_level == 1:

        best_move = random.choice(
            legal_moves
        )

    # -----------------------------------------------------
    # LEVEL 2
    # ゴールまでの距離を優先
    # -----------------------------------------------------

    elif cpu_level == 2:

        best_move = min(
            legal_moves,
            key=lambda move: abs(
                move[0] - cpu["goal"]
            )
        )

    # -----------------------------------------------------
    # LEVEL 3
    # 最短経路を考える
    # -----------------------------------------------------

    else:

        best_move = get_best_cpu_move()

    # -----------------------------------------------------
    # 移動
    # -----------------------------------------------------

    if best_move is not None:

        cpu["row"] = best_move[0]
        cpu["col"] = best_move[1]

    # -----------------------------------------------------
    # 勝利判定
    # -----------------------------------------------------

    if check_win(cpu):

        game_over = True

        return

    change_turn()


# =========================================================
# CPU BEST MOVE
# =========================================================

def get_best_cpu_move():

    cpu = player2

    legal_moves = get_legal_moves(
        cpu
    )

    if not legal_moves:
        return None

    best_move = None
    best_distance = 999

    for move in legal_moves:

        row, col = move

        distance = bfs_distance(
            row,
            col,
            cpu["goal"]
        )

        if distance < best_distance:

            best_distance = distance
            best_move = move

    return best_move


# =========================================================
# BFS DISTANCE
# =========================================================

def bfs_distance(
    start_row,
    start_col,
    goal_row
):

    queue = deque()

    queue.append(
        (
            start_row,
            start_col,
            0
        )
    )

    visited = set()

    visited.add(
        (
            start_row,
            start_col
        )
    )

    while queue:

        row, col, distance = queue.popleft()

        if row == goal_row:

            return distance

        for nr, nc in get_neighbors(
            row,
            col
        ):

            if (
                nr,
                nc
            ) in visited:

                continue

            visited.add(
                (
                    nr,
                    nc
                )
            )

            queue.append(
                (
                    nr,
                    nc,
                    distance + 1
                )
            )

    return 999


# =========================================================
# CPU WALL
# =========================================================

def cpu_place_wall():

    cpu = player2

    if cpu["walls"] <= 0:
        return False

    candidates = []

    for row in range(8):

        for col in range(8):

            candidates.append(
                ("H", row, col)
            )

            candidates.append(
                ("V", row, col)
            )

    random.shuffle(
        candidates
    )

    for kind, row, col in candidates:

        if can_place_wall(
            kind,
            row,
            col
        ):

            if kind == "H":

                horizontal_walls.add(
                    (
                        row,
                        col
                    )
                )

            else:

                vertical_walls.add(
                    (
                        row,
                        col
                    )
                )

            cpu["walls"] -= 1

            return True

    return False


# =========================================================
# CPU TURN
# =========================================================

def cpu_turn():

    if not cpu_mode:
        return

    if game_over:
        return

    if turn != 2:
        return

    # -----------------------------------------------------
    # LEVEL 1
    # 移動だけ
    # -----------------------------------------------------

    if cpu_level == 1:

        cpu_move()

        return

    # -----------------------------------------------------
    # LEVEL 2
    # 基本は移動
    # -----------------------------------------------------

    if cpu_level == 2:

        cpu_move()

        return

    # -----------------------------------------------------
    # LEVEL 3
    # ときどき壁を置く
    # -----------------------------------------------------

    if cpu_level == 3:

        # 壁を置くかどうか

        if (
            player2["walls"] > 0
            and
            random.random() < 0.25
        ):

            if cpu_place_wall():

                change_turn()

                return

        cpu_move()


# =========================================================
# MAIN LOOP
# =========================================================

running = True

while running:

    # =====================================================
    # EVENTS
    # =====================================================

    for event in pygame.event.get():

        # -------------------------------------------------
        # WINDOW CLOSE
        # -------------------------------------------------

        if event.type == pygame.QUIT:

            running = False

        # -------------------------------------------------
        # KEYBOARD
        # -------------------------------------------------

        elif event.type == pygame.KEYDOWN:

            # =============================================
            # TITLE
            # =============================================

            if scene == "title":

                if event.key == pygame.K_ESCAPE:

                    running = False

                continue

            # =============================================
            # CPU SELECT
            # =============================================

            if scene == "cpu_select":

                if event.key == pygame.K_ESCAPE:

                    scene = "title"

                continue

            # =============================================
            # GAME
            # =============================================

            # -------------------------------------------------
            # MOVE MODE
            # -------------------------------------------------

            if event.key == pygame.K_m:

                if not game_over:

                    mode = "move"

            # -------------------------------------------------
            # WALL MODE
            # -------------------------------------------------

            elif event.key == pygame.K_w:

                if (
                    not game_over
                    and
                    turn == 1
                    and
                    player1["walls"] > 0
                ):

                    mode = "wall"

            # -------------------------------------------------
            # RESET
            # -------------------------------------------------

            elif event.key == pygame.K_r:

                reset_game()

            # -------------------------------------------------
            # ESC
            # -------------------------------------------------

            elif event.key == pygame.K_ESCAPE:

                scene = "title"

                reset_game()

        # -------------------------------------------------
        # MOUSE
        # -------------------------------------------------

        elif event.type == pygame.MOUSEBUTTONDOWN:

            if event.button != 1:

                continue

            mouse_x = event.pos[0]
            mouse_y = event.pos[1]

            # =============================================
            # TITLE SCREEN
            # =============================================

            if scene == "title":

                pvp_button = pygame.Rect(
                    250,
                    320,
                    350,
                    70
                )

                cpu_button = pygame.Rect(
                    250,
                    430,
                    350,
                    70
                )

                # -----------------------------------------
                # PLAYER VS PLAYER
                # -----------------------------------------

                if pvp_button.collidepoint(
                    mouse_x,
                    mouse_y
                ):

                    cpu_mode = False

                    scene = "game"

                    reset_game()

                # -----------------------------------------
                # PLAYER VS CPU
                # -----------------------------------------

                elif cpu_button.collidepoint(
                    mouse_x,
                    mouse_y
                ):

                    cpu_mode = True

                    scene = "cpu_select"

                continue

            # =============================================
            # CPU LEVEL SELECT
            # =============================================

            if scene == "cpu_select":

                level1_button = pygame.Rect(
                    250,
                    270,
                    350,
                    70
                )

                level2_button = pygame.Rect(
                    250,
                    370,
                    350,
                    70
                )

                level3_button = pygame.Rect(
                    250,
                    470,
                    350,
                    70
                )

                back_button = pygame.Rect(
                    330,
                    590,
                    190,
                    50
                )

                # -----------------------------------------
                # LEVEL 1
                # -----------------------------------------

                if level1_button.collidepoint(
                    mouse_x,
                    mouse_y
                ):

                    cpu_level = 1

                    scene = "game"

                    reset_game()

                # -----------------------------------------
                # LEVEL 2
                # -----------------------------------------

                elif level2_button.collidepoint(
                    mouse_x,
                    mouse_y
                ):

                    cpu_level = 2

                    scene = "game"

                    reset_game()

                # -----------------------------------------
                # LEVEL 3
                # -----------------------------------------

                elif level3_button.collidepoint(
                    mouse_x,
                    mouse_y
                ):

                    cpu_level = 3

                    scene = "game"

                    reset_game()

                # -----------------------------------------
                # BACK
                # -----------------------------------------

                elif back_button.collidepoint(
                    mouse_x,
                    mouse_y
                ):

                    scene = "title"

                continue

            # =============================================
            # GAME SCREEN
            # =============================================

            reset_button = pygame.Rect(
                680,
                20,
                110,
                40
            )

            # ---------------------------------------------
            # RESET
            # ---------------------------------------------

            if reset_button.collidepoint(
                mouse_x,
                mouse_y
            ):

                reset_game()

                continue

            # ---------------------------------------------
            # GAME OVER
            # ---------------------------------------------

            if game_over:

                continue

            # ---------------------------------------------
            # CPU TURN
            # ---------------------------------------------

            if (
                cpu_mode
                and
                turn == 2
            ):

                continue

            # ---------------------------------------------
            # WALL MODE
            # ---------------------------------------------

            if mode == "wall":

                place_wall()

                continue

            # ---------------------------------------------
            # MOVE MODE
            # ---------------------------------------------

            cell = mouse_to_cell(
                mouse_x,
                mouse_y
            )

            if cell is not None:

                row, col = cell

                move_player(
                    row,
                    col
                )

    # =====================================================
    # CPU
    # =====================================================

    if (
        scene == "game"
        and
        cpu_mode
        and
        turn == 2
        and
        not game_over
    ):

        cpu_turn()

    # =====================================================
    # DRAW
    # =====================================================

    if scene == "title":

        draw_title_screen()

    elif scene == "cpu_select":

        draw_cpu_level_screen()

    else:

        screen.fill(
            BACKGROUND
        )

        draw_board()

        draw_coordinates()

        draw_walls()

        draw_wall_preview()

        draw_legal_moves()

        draw_player(
            player1,
            BLUE,
            1
        )

        draw_player(
            player2,
            RED,
            2
        )

        draw_information()

        draw_reset_button()

    # =====================================================
    # UPDATE
    # =====================================================

    pygame.display.flip()

    clock.tick(FPS)


# =========================================================
# QUIT
# =========================================================

pygame.quit()

sys.exit()