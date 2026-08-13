import pygame
import sys
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
    "9x9 WALL GAME - Version 5"
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
#
# H(row,col)
#
# 横壁
#
# (row,col)       (row,col+1)       (row,col+2)
#        -----------------------
#
# H(3,3)なら
#
# D4     D5
# --------------
# E4     E5
#
#
# V(row,col)
#
# 縦壁
#
# (row,col)     (row,col+1)
#                  |
#                  |
# (row+1,col)   (row+1,col+1)
#
# V(3,3)なら
#
# D4 | D5
# E4 | E5
#
# =========================================================

horizontal_walls = set()
vertical_walls = set()


# =========================================================
# GAME STATE
# =========================================================

turn = 1

game_over = False

# move / wall
mode = "move"


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

    # =====================================================
    # UP
    # =====================================================

    if row2 == row1 - 1:

        boundary_row = row2

        # H(boundary_row, col1)
        if (
            boundary_row,
            col1
        ) in horizontal_walls:

            return True

        # H(boundary_row, col1 - 1)
        if (
            boundary_row,
            col1 - 1
        ) in horizontal_walls:

            return True

    # =====================================================
    # DOWN
    # =====================================================

    elif row2 == row1 + 1:

        boundary_row = row1

        # H(boundary_row, col1)
        if (
            boundary_row,
            col1
        ) in horizontal_walls:

            return True

        # H(boundary_row, col1 - 1)
        if (
            boundary_row,
            col1 - 1
        ) in horizontal_walls:

            return True

    # =====================================================
    # LEFT
    # =====================================================

    elif col2 == col1 - 1:

        boundary_col = col2

        # V(row1, boundary_col)
        if (
            row1,
            boundary_col
        ) in vertical_walls:

            return True

        # V(row1 - 1, boundary_col)
        if (
            row1 - 1,
            boundary_col
        ) in vertical_walls:

            return True

    # =====================================================
    # RIGHT
    # =====================================================

    elif col2 == col1 + 1:

        boundary_col = col1

        # V(row1, boundary_col)
        if (
            row1,
            boundary_col
        ) in vertical_walls:

            return True

        # V(row1 - 1, boundary_col)
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

        # -------------------------------------------------
        # BOARD LIMIT
        # -------------------------------------------------

        if not (
            0 <= next_row < BOARD_SIZE
            and
            0 <= next_col < BOARD_SIZE
        ):

            continue

        # -------------------------------------------------
        # WALL
        # -------------------------------------------------

        if blocked(
            row,
            col,
            next_row,
            next_col
        ):

            continue

        # =================================================
        # NORMAL MOVE
        # =================================================

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

        # =================================================
        # OPPONENT IS NEXT
        # =================================================

        jump_row = next_row + dr
        jump_col = next_col + dc

        # =================================================
        # STRAIGHT JUMP
        # =================================================

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

        # =================================================
        # SIDEWAYS
        # =================================================

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

def can_place_wall(
    kind,
    row,
    col
):

    # =====================================================
    # HORIZONTAL
    # =====================================================

    if kind == "H":

        if not (
            0 <= row < 8
            and
            0 <= col < 8
        ):

            return False

        # Same wall
        if (
            row,
            col
        ) in horizontal_walls:

            return False

        # Adjacent horizontal wall
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

        # Crossing vertical wall
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

        # Temporary placement
        horizontal_walls.add(
            (
                row,
                col
            )
        )

        p1_ok = has_path(
            player1
        )

        p2_ok = has_path(
            player2
        )

        # Remove temporary wall
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

    # =====================================================
    # VERTICAL
    # =====================================================

    if kind == "V":

        if not (
            0 <= row < 8
            and
            0 <= col < 8
        ):

            return False

        # Same wall
        if (
            row,
            col
        ) in vertical_walls:

            return False

        # Adjacent vertical wall
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

        # Crossing horizontal wall
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

        # Temporary placement
        vertical_walls.add(
            (
                row,
                col
            )
        )

        p1_ok = has_path(
            player1
        )

        p2_ok = has_path(
            player2
        )

        # Remove temporary wall
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
#
# マウスに最も近い壁を探す
# =========================================================

def wall_from_mouse(mouse_x, mouse_y):

    # 盤面からの相対位置

    relative_x = mouse_x - BOARD_X
    relative_y = mouse_y - BOARD_Y

    # 盤面外
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
    # 最も近い縦のグリッド線
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
    # 最も近い横のグリッド線
    # -----------------------------------------------------

    horizontal_line = round(
        relative_y / CELL_SIZE
    )

    horizontal_distance = abs(
        relative_y
        -
        horizontal_line * CELL_SIZE
    )

    # 壁の近くでない
    if (
        vertical_distance > 18
        and
        horizontal_distance > 18
    ):

        return None

    # =====================================================
    # HORIZONTAL WALL
    # =====================================================

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

    # =====================================================
    # VERTICAL WALL
    # =====================================================

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

            # Goal area

            if row == 0:

                color = GOAL_RED

            elif row == 8:

                color = GOAL_BLUE

            else:

                color = WHITE

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

    # Rows

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

    # Columns

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

    # =====================================================
    # HORIZONTAL
    # =====================================================

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

    # =====================================================
    # VERTICAL
    # =====================================================

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

    valid = can_place_wall(
        kind,
        row,
        col
    )

    if valid:

        color = PREVIEW_VALID

    else:

        color = PREVIEW_INVALID

    # =====================================================
    # HORIZONTAL PREVIEW
    # =====================================================

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

    # =====================================================
    # VERTICAL PREVIEW
    # =====================================================

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

    pygame.draw.circle(
        screen,
        (100, 100, 100),
        (
            center_x + 3,
            center_y + 3
        ),
        25
    )

    pygame.draw.circle(
        screen,
        color,
        (
            center_x,
            center_y
        ),
        24
    )

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
    # P1
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
    # P2
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

def move_player(
    row,
    col
):

    global game_over

    if game_over:

        return

    if mode != "move":

        return

    player = get_current_player()

    legal_moves = get_legal_moves(
        player
    )

    if (
        row,
        col
    ) not in legal_moves:

        return

    player["row"] = row
    player["col"] = col

    # -----------------------------------------------------
    # WIN
    # -----------------------------------------------------

    if check_win(player):

        game_over = True

        return

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
    # VALIDATION
    # -----------------------------------------------------

    if not can_place_wall(
        kind,
        row,
        col
    ):

        return

    # -----------------------------------------------------
    # ACTUAL PLACEMENT
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
    # USE ONE WALL
    # -----------------------------------------------------

    player["walls"] -= 1

    # -----------------------------------------------------
    # CHANGE TURN
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

    mode = "move"


# =========================================================
# RESET
# =========================================================

def reset_game():

    global turn
    global game_over
    global mode

    player1["row"] = 0
    player1["col"] = 4
    player1["walls"] = 10

    player2["row"] = 8
    player2["col"] = 4
    player2["walls"] = 10

    horizontal_walls.clear()
    vertical_walls.clear()

    turn = 1

    game_over = False

    mode = "move"


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
        # CLOSE
        # -------------------------------------------------

        if event.type == pygame.QUIT:

            running = False

        # -------------------------------------------------
        # KEYBOARD
        # -------------------------------------------------

        elif event.type == pygame.KEYDOWN:

            # ---------------------------------------------
            # MOVE MODE
            # ---------------------------------------------

            if event.key == pygame.K_m:

                mode = "move"

            # ---------------------------------------------
            # WALL MODE
            # ---------------------------------------------

            elif event.key == pygame.K_w:

                if (
                    not game_over
                    and
                    get_current_player()["walls"] > 0
                ):

                    mode = "wall"

            # ---------------------------------------------
            # RESET
            # ---------------------------------------------

            elif event.key == pygame.K_r:

                reset_game()

        # -------------------------------------------------
        # MOUSE
        # -------------------------------------------------

        elif event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                mouse_x = event.pos[0]
                mouse_y = event.pos[1]

                # -----------------------------------------
                # RESET BUTTON
                # -----------------------------------------

                reset_button = pygame.Rect(
                    680,
                    20,
                    110,
                    40
                )

                if reset_button.collidepoint(
                    mouse_x,
                    mouse_y
                ):

                    reset_game()

                    continue

                # -----------------------------------------
                # GAME OVER
                # -----------------------------------------

                if game_over:

                    continue

                # -----------------------------------------
                # WALL MODE
                # -----------------------------------------

                if mode == "wall":

                    place_wall()

                    continue

                # -----------------------------------------
                # MOVE MODE
                # -----------------------------------------

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
    # DRAW
    # =====================================================

    screen.fill(
        BACKGROUND
    )

    draw_board()

    draw_coordinates()

    draw_walls()

    # 壁プレビュー
    draw_wall_preview()

    # 移動可能マス
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

    pygame.display.flip()

    clock.tick(FPS)


# =========================================================
# QUIT
# =========================================================

pygame.quit()

sys.exit()
