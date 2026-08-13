import pygame
import sys


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

BUTTON_COLOR = (210, 210, 210)
BUTTON_HOVER = (180, 180, 180)


# =========================================================
# INITIALIZE PYGAME
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
# GAME STATE
# =========================================================

turn = 1
game_over = False


# =========================================================
# HELPER
# =========================================================

def get_current_player():

    if turn == 1:
        return player1

    return player2


# =========================================================
# BOARD POSITION
# =========================================================

def cell_position(row, col):

    x = (
        BOARD_X
        + col * CELL_SIZE
    )

    y = (
        BOARD_Y
        + row * CELL_SIZE
    )

    return x, y


# =========================================================
# MOUSE -> CELL
# =========================================================

def mouse_to_cell(mouse_x, mouse_y):

    col = (
        mouse_x - BOARD_X
    ) // CELL_SIZE

    row = (
        mouse_y - BOARD_Y
    ) // CELL_SIZE

    if (
        0 <= row < BOARD_SIZE
        and
        0 <= col < BOARD_SIZE
    ):

        return int(row), int(col)

    return None


# =========================================================
# GET LEGAL MOVES
# =========================================================

def get_legal_moves(player):

    row = player["row"]
    col = player["col"]

    moves = []

    directions = [
        (-1, 0),   # UP
        (1, 0),    # DOWN
        (0, -1),   # LEFT
        (0, 1)     # RIGHT
    ]

    for dr, dc in directions:

        new_row = row + dr
        new_col = col + dc

        # -------------------------------------------------
        # BOARD LIMIT
        # -------------------------------------------------

        if not (
            0 <= new_row < BOARD_SIZE
            and
            0 <= new_col < BOARD_SIZE
        ):

            continue

        # -------------------------------------------------
        # OPPONENT
        # -------------------------------------------------

        opponent = (
            player2
            if player is player1
            else player1
        )

        if (
            new_row == opponent["row"]
            and
            new_col == opponent["col"]
        ):

            # Jump will be implemented later.
            # For now, cannot move onto opponent.

            continue

        moves.append(
            (new_row, new_col)
        )

    return moves


# =========================================================
# CHECK WIN
# =========================================================

def check_win(player):

    if player["row"] == player["goal"]:

        return True

    return False


# =========================================================
# CHANGE TURN
# =========================================================

def change_turn():

    global turn

    if turn == 1:

        turn = 2

    else:

        turn = 1


# =========================================================
# RESET GAME
# =========================================================

def reset_game():

    global turn
    global game_over

    player1["row"] = 0
    player1["col"] = 4
    player1["walls"] = 10

    player2["row"] = 8
    player2["col"] = 4
    player2["walls"] = 10

    turn = 1

    game_over = False


# =========================================================
# MOVE PLAYER
# =========================================================

def move_player(row, col):

    global game_over

    if game_over:

        return

    player = get_current_player()

    legal_moves = get_legal_moves(
        player
    )

    # -----------------------------------------------------
    # INVALID MOVE
    # -----------------------------------------------------

    if (row, col) not in legal_moves:

        return

    # -----------------------------------------------------
    # MOVE
    # -----------------------------------------------------

    player["row"] = row
    player["col"] = col

    # -----------------------------------------------------
    # CHECK WIN
    # -----------------------------------------------------

    if check_win(player):

        game_over = True

        return

    # -----------------------------------------------------
    # CHANGE TURN
    # -----------------------------------------------------

    change_turn()


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
            # GOAL AREA
            # -------------------------------------------------

            if row == 0:

                color = GOAL_RED

            elif row == 8:

                color = GOAL_BLUE

            else:

                color = WHITE

            # -------------------------------------------------
            # CELL
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
            # GRID
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
    # LETTERS
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
            (x, y)
        )

    # -----------------------------------------------------
    # NUMBERS
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
            (x, y)
        )


# =========================================================
# DRAW LEGAL MOVES
# =========================================================

def draw_legal_moves():

    if game_over:

        return

    player = get_current_player()

    moves = get_legal_moves(
        player
    )

    mouse_position = pygame.mouse.get_pos()

    hovered_cell = mouse_to_cell(
        mouse_position[0],
        mouse_position[1]
    )

    for row, col in moves:

        x, y = cell_position(
            row,
            col
        )

        center_x = (
            x + CELL_SIZE // 2
        )

        center_y = (
            y + CELL_SIZE // 2
        )

        # -------------------------------------------------
        # HOVER
        # -------------------------------------------------

        if hovered_cell == (row, col):

            color = MOVE_HOVER_COLOR

        else:

            color = MOVE_COLOR

        # -------------------------------------------------
        # DRAW MOVE INDICATOR
        # -------------------------------------------------

        pygame.draw.circle(
            screen,
            color,
            (
                center_x,
                center_y
            ),
            10
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
        x + CELL_SIZE // 2
    )

    center_y = (
        y + CELL_SIZE // 2
    )

    # -----------------------------------------------------
    # SHADOW
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
    # PLAYER
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
    # OUTLINE
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
    # NUMBER
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
    # PLAYER 1 INFO
    # -----------------------------------------------------

    p1_position = (
        chr(
            ord("A")
            + player1["row"]
        )
        +
        str(
            player1["col"] + 1
        )
    )

    p1_text = (
        f"P1: {p1_position}   "
        f"Walls: {player1['walls']}"
    )

    p1_surface = font.render(
        p1_text,
        True,
        BLUE
    )

    screen.blit(
        p1_surface,
        (
            450,
            725
        )
    )

    # -----------------------------------------------------
    # PLAYER 2 INFO
    # -----------------------------------------------------

    p2_position = (
        chr(
            ord("A")
            + player2["row"]
        )
        +
        str(
            player2["col"] + 1
        )
    )

    p2_text = (
        f"P2: {p2_position}   "
        f"Walls: {player2['walls']}"
    )

    p2_surface = font.render(
        p2_text,
        True,
        RED
    )

    screen.blit(
        p2_surface,
        (
            450,
            755
        )
    )


# =========================================================
# DRAW RESET BUTTON
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
        # MOUSE CLICK
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
                # BOARD CLICK
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
