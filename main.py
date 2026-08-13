import pygame
import sys


# =========================================================
# SETTINGS
# =========================================================

BOARD_SIZE = 9
CELL_SIZE = 70

BOARD_X = 50
BOARD_Y = 50

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800

FPS = 60


# =========================================================
# COLORS
# =========================================================

WHITE = (245, 245, 245)
BLACK = (30, 30, 30)
GRID = (150, 150, 150)

BLUE = (50, 100, 220)
RED = (220, 60, 60)

GOAL_BLUE = (220, 230, 255)
GOAL_RED = (255, 225, 225)


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

large_font = pygame.font.SysFont(
    "Arial",
    28,
    bold=True
)


# =========================================================
# PLAYERS
# =========================================================

player1 = {
    "row": 0,
    "col": 4,
    "walls": 10
}

player2 = {
    "row": 8,
    "col": 4,
    "walls": 10
}


# =========================================================
# GAME STATE
# =========================================================

turn = 1


# =========================================================
# DRAW BOARD
# =========================================================

def draw_board():

    for row in range(BOARD_SIZE):

        for col in range(BOARD_SIZE):

            x = BOARD_X + col * CELL_SIZE
            y = BOARD_Y + row * CELL_SIZE

            # ---------------------------------------------
            # Goal areas
            # ---------------------------------------------

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

    # -----------------------------------------------------
    # Letters A-I
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

        x = BOARD_X - 30
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
    # Numbers 1-9
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

        y = BOARD_Y - 30

        screen.blit(
            text,
            (x, y)
        )


# =========================================================
# DRAW PLAYER
# =========================================================

def draw_player(
    player,
    color
):

    row = player["row"]
    col = player["col"]

    x = (
        BOARD_X
        + col * CELL_SIZE
        + CELL_SIZE // 2
    )

    y = (
        BOARD_Y
        + row * CELL_SIZE
        + CELL_SIZE // 2
    )

    pygame.draw.circle(
        screen,
        color,
        (x, y),
        23
    )

    pygame.draw.circle(
        screen,
        BLACK,
        (x, y),
        23,
        2
    )


# =========================================================
# DRAW INFORMATION
# =========================================================

def draw_information():

    turn_text = f"PLAYER {turn} TURN"

    turn_surface = large_font.render(
        turn_text,
        True,
        BLACK
    )

    screen.blit(
        turn_surface,
        (BOARD_X, 700)
    )

    p1_text = (
        f"PLAYER 1   "
        f"Walls: {player1['walls']}"
    )

    p2_text = (
        f"PLAYER 2   "
        f"Walls: {player2['walls']}"
    )

    p1_surface = font.render(
        p1_text,
        True,
        BLUE
    )

    p2_surface = font.render(
        p2_text,
        True,
        RED
    )

    screen.blit(
        p1_surface,
        (500, 690)
    )

    screen.blit(
        p2_surface,
        (500, 720)
    )


# =========================================================
# MAIN LOOP
# =========================================================

running = True

while running:

    # =====================================================
    # EVENTS
    # =====================================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

    # =====================================================
    # DRAW
    # =====================================================

    screen.fill(
        (235, 235, 235)
    )

    draw_board()

    draw_coordinates()

    draw_player(
        player1,
        BLUE
    )

    draw_player(
        player2,
        RED
    )

    draw_information()

    pygame.display.flip()

    clock.tick(FPS)


# =========================================================
# QUIT
# =========================================================

pygame.quit()

sys.exit()
