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

# CPUの思考時間
CPU_THINK_TIME = 500


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

menu_font = pygame.font.SysFont(
    "Arial",
    42,
    bold=True
)

option_font = pygame.font.SysFont(
    "Arial",
    28
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

# move / wall
mode = "move"

# title / game
scene = "title"

# False = PLAYER vs PLAYER
# True = PLAYER vs CPU
cpu_mode = False

# CPU LEVEL
# 1 = Easy
# 2 = Normal
# 3 = Hard
cpu_level = 1

# CPU THINKING
cpu_thinking = False
cpu_thinking_start = 0


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

    # =====================================================
    # DOWN
    # =====================================================

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

    # =====================================================
    # LEFT
    # =====================================================

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

    # =====================================================
    # RIGHT
    # =====================================================

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
# SHORTEST PATH
#
# CPUが実際の壁を考慮して
# ゴールまでの最短距離を計算する
# =========================================================

def get_shortest_path(player):

    start = (
        player["row"],
        player["col"]
    )

    goal_row = player["goal"]

    queue = deque()

    queue.append(
        (
            start,
            [start]
        )
    )

    visited = set()

    visited.add(start)

    while queue:

        current, path = queue.popleft()

        row, col = current

        # ゴール到達
        if row == goal_row:

            return path

        for nr, nc in get_neighbors(
            row,
            col
        ):

            next_position = (
                nr,
                nc
            )

            if next_position in visited:
                continue

            visited.add(
                next_position
            )

            new_path = path + [
                next_position
            ]

            queue.append(
                (
                    next_position,
                    new_path
                )
            )

    # 通常は到達不能にならない
    return None


# =========================================================
# SHORTEST DISTANCE
#
# ゴールまでの最短距離だけを返す
# =========================================================

def get_shortest_distance(player):

    path = get_shortest_path(
        player
    )

    if path is None:

        return 999

    # pathには現在地も含まれるため -1
    return len(path) - 1


# =========================================================
# PATH DIRECTION
#
# 最短経路の次のマスを取得
# =========================================================

def get_next_path_position(player):

    path = get_shortest_path(
        player
    )

    if path is None:
        return None

    if len(path) < 2:
        return None

    return path[1]


# =========================================================
# PATH INFORMATION
#
# CPUが現在の盤面を分析するための情報
# =========================================================

def analyze_position():

    cpu_distance = get_shortest_distance(
        player2
    )

    player_distance = get_shortest_distance(
        player1
    )

    cpu_next = get_next_path_position(
        player2
    )

    player_next = get_next_path_position(
        player1
    )

    return {
        "cpu_distance": cpu_distance,
        "player_distance": player_distance,
        "cpu_next": cpu_next,
        "player_next": player_next
    }


# =========================================================
# CPU ADVANTAGE
#
# CPU側がどれくらい有利か
# 数字が大きいほどCPU有利
# =========================================================

def get_cpu_advantage():

    cpu_distance = get_shortest_distance(
        player2
    )

    player_distance = get_shortest_distance(
        player1
    )

    return (
        player_distance
        -
        cpu_distance
    )

# =========================================================
# WALL VALIDATION
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
# WALL CAN PLACE
# =========================================================

def can_place_wall(kind, row, col):

    # =====================================================
    # HORIZONTAL WALL
    # =====================================================

    if kind == "H":

        if not (
            0 <= row < 8
            and
            0 <= col < 8
        ):

            return False

        # ---------------------------------------------
        # 同じ壁
        # ---------------------------------------------

        if (
            row,
            col
        ) in horizontal_walls:

            return False

        # ---------------------------------------------
        # 横方向の重なり
        # ---------------------------------------------

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

        # ---------------------------------------------
        # 縦壁との交差
        # ---------------------------------------------

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

        # ---------------------------------------------
        # 仮設置
        # ---------------------------------------------

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

        # ---------------------------------------------
        # 仮設置した壁を削除
        # ---------------------------------------------

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
    # VERTICAL WALL
    # =====================================================

    if kind == "V":

        if not (
            0 <= row < 8
            and
            0 <= col < 8
        ):

            return False

        # ---------------------------------------------
        # 同じ壁
        # ---------------------------------------------

        if (
            row,
            col
        ) in vertical_walls:

            return False

        # ---------------------------------------------
        # 縦方向の重なり
        # ---------------------------------------------

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

        # ---------------------------------------------
        # 横壁との交差
        # ---------------------------------------------

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

        # ---------------------------------------------
        # 仮設置
        # ---------------------------------------------

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

        # ---------------------------------------------
        # 仮設置した壁を削除
        # ---------------------------------------------

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
# SIMULATE WALL
#
# 壁を一時的に置いて、
# その結果を調べる
# =========================================================

def simulate_wall(kind, row, col):

    if not can_place_wall(
        kind,
        row,
        col
    ):

        return None

    # =====================================================
    # 壁を仮設置
    # =====================================================

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

    # =====================================================
    # 設置後の最短距離
    # =====================================================

    cpu_distance = get_shortest_distance(
        player2
    )

    player_distance = get_shortest_distance(
        player1
    )

    # =====================================================
    # 経路
    # =====================================================

    cpu_path = get_shortest_path(
        player2
    )

    player_path = get_shortest_path(
        player1
    )

    # =====================================================
    # 壁を元に戻す
    # =====================================================

    if kind == "H":

        horizontal_walls.remove(
            (
                row,
                col
            )
        )

    else:

        vertical_walls.remove(
            (
                row,
                col
            )
        )

    return {
        "cpu_distance": cpu_distance,
        "player_distance": player_distance,
        "cpu_path": cpu_path,
        "player_path": player_path
    }


# =========================================================
# WALL SCORE
#
# CPUがその壁を置く価値を評価する
# =========================================================

def evaluate_wall(
    kind,
    row,
    col
):

    result = simulate_wall(
        kind,
        row,
        col
    )

    if result is None:

        return None

    cpu_distance = result[
        "cpu_distance"
    ]

    player_distance = result[
        "player_distance"
    ]

    current_cpu_distance = get_shortest_distance(
        player2
    )

    current_player_distance = get_shortest_distance(
        player1
    )

    # =====================================================
    # 相手を遠ざけるほど高評価
    # =====================================================

    opponent_gain = (
        player_distance
        -
        current_player_distance
    )

    # =====================================================
    # 自分が不利になるほど減点
    # =====================================================

    cpu_loss = (
        cpu_distance
        -
        current_cpu_distance
    )

    # =====================================================
    # 基本スコア
    # =====================================================

    score = (
        opponent_gain * 10
        -
        cpu_loss * 6
    )

    return score


# =========================================================
# FIND BEST WALL
#
# 現在の盤面で最も価値の高い壁を探す
# =========================================================

def find_best_wall():

    best_wall = None

    best_score = -999999

    # =====================================================
    # 全候補を調査
    # =====================================================

    for row in range(8):

        for col in range(8):

            # ---------------------------------------------
            # 横壁
            # ---------------------------------------------

            score = evaluate_wall(
                "H",
                row,
                col
            )

            if score is not None:

                if score > best_score:

                    best_score = score

                    best_wall = (
                        "H",
                        row,
                        col
                    )

            # ---------------------------------------------
            # 縦壁
            # ---------------------------------------------

            score = evaluate_wall(
                "V",
                row,
                col
            )

            if score is not None:

                if score > best_score:

                    best_score = score

                    best_wall = (
                        "V",
                        row,
                        col
                    )

    return (
        best_wall,
        best_score
    )


# =========================================================
# APPLY WALL
# =========================================================

def apply_wall(
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

# =========================================================
# CPU MOVE SCORE
#
# CPUがそのマスへ移動した場合の評価
# =========================================================

def evaluate_cpu_move(
    row,
    col
):

    # =====================================================
    # 現在のCPU位置を保存
    # =====================================================

    old_row = player2["row"]
    old_col = player2["col"]

    # =====================================================
    # 仮移動
    # =====================================================

    player2["row"] = row
    player2["col"] = col

    # =====================================================
    # ゴールまでの距離
    # =====================================================

    distance = get_shortest_distance(
        player2
    )

    # =====================================================
    # 元に戻す
    # =====================================================

    player2["row"] = old_row
    player2["col"] = old_col

    # =====================================================
    # 距離が短いほど高評価
    # =====================================================

    score = (
        -distance * 10
    )

    # =====================================================
    # ゴール直前は大きく評価
    # =====================================================

    if row == player2["goal"]:

        score += 10000

    return score


# =========================================================
# FIND BEST MOVE
#
# CPUの合法手の中から
# 最もゴールに近づく手を選ぶ
# =========================================================

def find_best_move():

    legal_moves = get_legal_moves(
        player2
    )

    if not legal_moves:

        return None

    best_move = None

    best_score = -999999

    for row, col in legal_moves:

        score = evaluate_cpu_move(
            row,
            col
        )

        if score > best_score:

            best_score = score

            best_move = (
                row,
                col
            )

    return best_move


# =========================================================
# CPU MOVE
# =========================================================

def cpu_move():

    global game_over

    if game_over:

        return

    cpu = player2

    # =====================================================
    # 合法手
    # =====================================================

    legal_moves = get_legal_moves(
        cpu
    )

    if not legal_moves:

        return

    # =====================================================
    # LEVEL 1
    #
    # 基本的な最短距離優先
    # =====================================================

    if cpu_level == 1:

        best_move = find_best_move()

        if best_move is None:

            return

        cpu["row"] = best_move[0]
        cpu["col"] = best_move[1]

    # =====================================================
    # LEVEL 2
    #
    # 自分と相手の距離を比較
    # =====================================================

    elif cpu_level == 2:

        best_move = None

        best_score = -999999

        for row, col in legal_moves:

            old_row = cpu["row"]
            old_col = cpu["col"]

            # ---------------------------------------------
            # 仮移動
            # ---------------------------------------------

            cpu["row"] = row
            cpu["col"] = col

            cpu_distance = get_shortest_distance(
                cpu
            )

            player_distance = get_shortest_distance(
                player1
            )

            # ---------------------------------------------
            # 評価
            # ---------------------------------------------

            score = (
                player_distance * 5
                -
                cpu_distance * 10
            )

            # ---------------------------------------------
            # ゴール
            # ---------------------------------------------

            if row == cpu["goal"]:

                score += 10000

            # ---------------------------------------------
            # 元に戻す
            # ---------------------------------------------

            cpu["row"] = old_row
            cpu["col"] = old_col

            if score > best_score:

                best_score = score

                best_move = (
                    row,
                    col
                )

        if best_move is None:

            return

        cpu["row"] = best_move[0]
        cpu["col"] = best_move[1]

    # =====================================================
    # LEVEL 3
    #
    # 移動と壁の両方を比較する
    # =====================================================

    else:

        best_move = find_best_move()

        move_score = -999999

        if best_move is not None:

            move_score = evaluate_cpu_move(
                best_move[0],
                best_move[1]
            )

        # ---------------------------------------------
        # 壁を評価
        # ---------------------------------------------

        best_wall, wall_score = find_best_wall()

        if best_wall is None:

            wall_score = -999999

        # ---------------------------------------------
        # 壁の価値が十分高ければ壁
        # ---------------------------------------------

        if (
            cpu["walls"] > 0
            and
            best_wall is not None
            and
            wall_score > move_score + 5
        ):

            kind, row, col = best_wall

            apply_wall(
                kind,
                row,
                col
            )

            cpu["walls"] -= 1

        # ---------------------------------------------
        # それ以外は移動
        # ---------------------------------------------

        elif best_move is not None:

            cpu["row"] = best_move[0]
            cpu["col"] = best_move[1]

        else:

            return

    # =====================================================
    # 勝利判定
    # =====================================================

    if check_win(cpu):

        game_over = True

        return

    # =====================================================
    # PLAYER 1へ
    # =====================================================

    change_turn()


# =========================================================
# CPU WALL
#
# LEVEL 3で使用する補助関数
# =========================================================

def cpu_place_wall():

    global game_over

    if game_over:

        return

    cpu = player2

    if cpu["walls"] <= 0:

        return

    best_wall, best_score = find_best_wall()

    if best_wall is None:

        change_turn()

        return

    kind, row, col = best_wall

    apply_wall(
        kind,
        row,
        col
    )

    cpu["walls"] -= 1

    change_turn()


# =========================================================
# CPU TURN
# =========================================================

def cpu_turn():

    if not cpu_mode:

        return

    if game_over:

        return

    # =====================================================
    # CPU = PLAYER 2
    # =====================================================

    if turn != 2:

        return

    # =====================================================
    # CPU THINKING
    #
    # 0.5秒待ってからCPUが行動する
    # =====================================================

    global cpu_thinking
    global cpu_thinking_start

    if not cpu_thinking:

        cpu_thinking = True

        cpu_thinking_start = pygame.time.get_ticks()

        return

    current_time = pygame.time.get_ticks()

    elapsed = (
        current_time
        -
        cpu_thinking_start
    )

    if elapsed < CPU_THINK_TIME:

        return

    # =====================================================
    # 思考終了
    # =====================================================

    cpu_thinking = False

    # =====================================================
    # CPU行動
    # =====================================================

    cpu_move()


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
# FIND WALL FROM MOUSE
# =========================================================

def wall_from_mouse(
    mouse_x,
    mouse_y
):

    relative_x = (
        mouse_x
        -
        BOARD_X
    )

    relative_y = (
        mouse_y
        -
        BOARD_Y
    )

    # =====================================================
    # BOARD OUTSIDE
    # =====================================================

    if (
        relative_x < -20
        or
        relative_y < -20
        or
        relative_x >
        BOARD_SIZE * CELL_SIZE + 20
        or
        relative_y >
        BOARD_SIZE * CELL_SIZE + 20
    ):

        return None

    # =====================================================
    # VERTICAL GRID LINE
    # =====================================================

    vertical_line = round(
        relative_x / CELL_SIZE
    )

    vertical_distance = abs(
        relative_x
        -
        vertical_line * CELL_SIZE
    )

    # =====================================================
    # HORIZONTAL GRID LINE
    # =====================================================

    horizontal_line = round(
        relative_y / CELL_SIZE
    )

    horizontal_distance = abs(
        relative_y
        -
        horizontal_line * CELL_SIZE
    )

    # =====================================================
    # NOT NEAR WALL
    # =====================================================

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

        wall_row = (
            horizontal_line
            -
            1
        )

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

    wall_col = (
        vertical_line
        -
        1
    )

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

            # =================================================
            # GOAL AREA
            # =================================================

            if row == 0:

                color = GOAL_RED

            elif row == 8:

                color = GOAL_BLUE

            else:

                color = WHITE

            # =================================================
            # CELL
            # =================================================

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

            # =================================================
            # GRID
            # =================================================

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

    # =====================================================
    # ROW LETTERS
    # =====================================================

    for row in range(BOARD_SIZE):

        letter = chr(
            ord("A")
            +
            row
        )

        text = font.render(
            letter,
            True,
            BLACK
        )

        x = (
            BOARD_X
            -
            35
        )

        y = (
            BOARD_Y
            +
            row * CELL_SIZE
            +
            CELL_SIZE // 2
            -
            text.get_height() // 2
        )

        screen.blit(
            text,
            (
                x,
                y
            )
        )

    # =====================================================
    # COLUMN NUMBERS
    # =====================================================

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
            +
            col * CELL_SIZE
            +
            CELL_SIZE // 2
            -
            text.get_width() // 2
        )

        y = (
            BOARD_Y
            -
            35
        )

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
    # HORIZONTAL WALLS
    # =====================================================

    for row, col in horizontal_walls:

        x1 = (
            BOARD_X
            +
            col * CELL_SIZE
        )

        x2 = (
            BOARD_X
            +
            (col + 2) * CELL_SIZE
        )

        y = (
            BOARD_Y
            +
            (row + 1) * CELL_SIZE
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
    # VERTICAL WALLS
    # =====================================================

    for row, col in vertical_walls:

        x = (
            BOARD_X
            +
            (col + 1) * CELL_SIZE
        )

        y1 = (
            BOARD_Y
            +
            row * CELL_SIZE
        )

        y2 = (
            BOARD_Y
            +
            (row + 2) * CELL_SIZE
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
# DRAW LEGAL MOVES
# =========================================================

def draw_legal_moves():

    if game_over:

        return

    if mode != "move":

        return

    # CPUのターン中は表示しない
    if cpu_mode and turn == 2:

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
            +
            CELL_SIZE // 2
        )

        center_y = (
            y
            +
            CELL_SIZE // 2
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
        +
        CELL_SIZE // 2
    )

    center_y = (
        y
        +
        CELL_SIZE // 2
    )

    # =====================================================
    # SHADOW
    # =====================================================

    pygame.draw.circle(
        screen,
        (100, 100, 100),
        (
            center_x + 3,
            center_y + 3
        ),
        25
    )

    # =====================================================
    # PLAYER
    # =====================================================

    pygame.draw.circle(
        screen,
        color,
        (
            center_x,
            center_y
        ),
        24
    )

    # =====================================================
    # BORDER
    # =====================================================

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

    # =====================================================
    # NUMBER
    # =====================================================

    text = large_font.render(
        str(number),
        True,
        WHITE
    )

    text_x = (
        center_x
        -
        text.get_width() // 2
    )

    text_y = (
        center_y
        -
        text.get_height() // 2
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
            +
            player["row"]
        )
        +
        str(
            player["col"] + 1
        )
    )

# =========================================================
# DRAW WALL PREVIEW
# =========================================================

def draw_wall_preview():

    if game_over:

        return

    if mode != "wall":

        return

    # =====================================================
    # CPUターン中は表示しない
    # =====================================================

    if cpu_mode and turn == 2:

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

    # =====================================================
    # 設置可能か確認
    # =====================================================

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
            +
            col * CELL_SIZE
        )

        x2 = (
            BOARD_X
            +
            (col + 2) * CELL_SIZE
        )

        y = (
            BOARD_Y
            +
            (row + 1) * CELL_SIZE
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
            +
            (col + 1) * CELL_SIZE
        )

        y1 = (
            BOARD_Y
            +
            row * CELL_SIZE
        )

        y2 = (
            BOARD_Y
            +
            (row + 2) * CELL_SIZE
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
# DRAW INFORMATION
# =========================================================

def draw_information():

    # =====================================================
    # TITLE
    # =====================================================

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

    # =====================================================
    # TURN
    # =====================================================

    if game_over:

        if turn == 1:

            turn_text = "PLAYER 1 WINS!"

            turn_color = BLUE

        else:

            turn_text = "PLAYER 2 WINS!"

            turn_color = RED

    elif cpu_mode and turn == 2:

        turn_text = "CPU THINKING..."

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

    # =====================================================
    # PLAYER 1
    # =====================================================

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

    # =====================================================
    # PLAYER 2
    # =====================================================

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

    # =====================================================
    # CPU LEVEL
    # =====================================================

    if cpu_mode:

        level_text = (
            f"CPU LEVEL: {cpu_level}"
        )

        level_surface = small_font.render(
            level_text,
            True,
            BLACK
        )

        screen.blit(
            level_surface,
            (
                650,
                755
            )
        )

    # =====================================================
    # MODE
    # =====================================================

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

    # =====================================================
    # HOVER
    # =====================================================

    if button_rect.collidepoint(
        mouse_x,
        mouse_y
    ):

        color = BUTTON_HOVER

    else:

        color = BUTTON_COLOR

    # =====================================================
    # BUTTON
    # =====================================================

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

    # =====================================================
    # TEXT
    # =====================================================

    text = font.render(
        "RESET",
        True,
        BLACK
    )

    text_x = (
        button_rect.centerx
        -
        text.get_width() // 2
    )

    text_y = (
        button_rect.centery
        -
        text.get_height() // 2
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
# CHECK WIN
# =========================================================

def check_win(player):

    return (
        player["row"]
        ==
        player["goal"]
    )


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

    # =====================================================
    # CPUターン中は操作不可
    # =====================================================

    if cpu_mode and turn == 2:

        return

    player = get_current_player()

    legal_moves = get_legal_moves(
        player
    )

    # =====================================================
    # 不正な移動
    # =====================================================

    if (
        row,
        col
    ) not in legal_moves:

        return

    # =====================================================
    # 移動
    # =====================================================

    player["row"] = row
    player["col"] = col

    # =====================================================
    # 勝利判定
    # =====================================================

    if check_win(player):

        game_over = True

        return

    # =====================================================
    # ターン交代
    # =====================================================

    change_turn()


# =========================================================
# PLACE WALL
# =========================================================

def place_wall():

    if game_over:

        return

    if mode != "wall":

        return

    # =====================================================
    # CPUターン中は操作不可
    # =====================================================

    if cpu_mode and turn == 2:

        return

    player = get_current_player()

    # =====================================================
    # 壁が残っていない
    # =====================================================

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

    # =====================================================
    # 壁の設置可能判定
    # =====================================================

    if not can_place_wall(
        kind,
        row,
        col
    ):

        return

    # =====================================================
    # 実際に壁を設置
    # =====================================================

    apply_wall(
        kind,
        row,
        col
    )

    # =====================================================
    # 壁を1枚消費
    # =====================================================

    player["walls"] -= 1

    # =====================================================
    # ターン交代
    # =====================================================

    change_turn()


# =========================================================
# CHANGE TURN
# =========================================================

def change_turn():

    global turn
    global mode
    global cpu_thinking

    # =====================================================
    # PLAYER 1 → PLAYER 2
    # =====================================================

    if turn == 1:

        turn = 2

    # =====================================================
    # PLAYER 2 → PLAYER 1
    # =====================================================

    else:

        turn = 1

    # =====================================================
    # ターン交代時は移動モード
    # =====================================================

    mode = "move"

    # =====================================================
    # CPU思考状態をリセット
    # =====================================================

    cpu_thinking = False


# =========================================================
# APPLY WALL
# =========================================================

def apply_wall(
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


# =========================================================
# RESET GAME
# =========================================================

def reset_game():

    global turn
    global game_over
    global mode
    global cpu_thinking
    global cpu_thinking_start

    # =====================================================
    # PLAYER 1
    # =====================================================

    player1["row"] = 0
    player1["col"] = 4
    player1["walls"] = 10

    # =====================================================
    # PLAYER 2
    # =====================================================

    player2["row"] = 8
    player2["col"] = 4
    player2["walls"] = 10

    # =====================================================
    # WALLS
    # =====================================================

    horizontal_walls.clear()

    vertical_walls.clear()

    # =====================================================
    # GAME STATE
    # =====================================================

    turn = 1

    game_over = False

    mode = "move"

    # =====================================================
    # CPU STATE
    # =====================================================

    cpu_thinking = False

    cpu_thinking_start = 0


# =========================================================
# TITLE SCREEN
# =========================================================

def draw_title_screen():

    screen.fill(
        BACKGROUND
    )

    # =====================================================
    # TITLE
    # =====================================================

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

    # =====================================================
    # SUBTITLE
    # =====================================================

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

    # =====================================================
    # PLAYER VS PLAYER
    # =====================================================

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

    # =====================================================
    # PLAYER VS CPU
    # =====================================================

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

    # =====================================================
    # CONTROLS
    # =====================================================

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
# CPU LEVEL SELECT
# =========================================================

def draw_cpu_level_screen():

    screen.fill(
        BACKGROUND
    )

    # =====================================================
    # TITLE
    # =====================================================

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

    # =====================================================
    # LEVEL 1
    # =====================================================

    level1_button = pygame.Rect(
        250,
        270,
        350,
        70
    )

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

    # =====================================================
    # LEVEL 2
    # =====================================================

    level2_button = pygame.Rect(
        250,
        370,
        350,
        70
    )

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

    # =====================================================
    # LEVEL 3
    # =====================================================

    level3_button = pygame.Rect(
        250,
        470,
        350,
        70
    )

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

    # =====================================================
    # BACK
    # =====================================================

    back_button = pygame.Rect(
        330,
        590,
        190,
        50
    )

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
# CPU DISTANCE
# =========================================================

def get_goal_distance(
    player,
    row,
    col
):

    return abs(
        row
        -
        player["goal"]
    )


# =========================================================
# CPU MOVE SCORE
# =========================================================

def evaluate_cpu_move(
    row,
    col
):

    cpu = player2
    opponent = player1

    # =====================================================
    # ゴールまでの距離
    # =====================================================

    cpu_distance = get_goal_distance(
        cpu,
        row,
        col
    )

    # =====================================================
    # プレイヤーのゴールまでの距離
    # =====================================================

    opponent_distance = get_goal_distance(
        opponent,
        opponent["row"],
        opponent["col"]
    )

    # =====================================================
    # CPUが近づくほど高評価
    # =====================================================

    score = (
        -cpu_distance * 100
    )

    # =====================================================
    # 相手より先にゴールできそうなら加点
    # =====================================================

    if cpu_distance < opponent_distance:

        score += 30

    # =====================================================
    # ゴール直前を大きく評価
    # =====================================================

    if cpu_distance == 0:

        score += 10000

    elif cpu_distance == 1:

        score += 500

    return score


# =========================================================
# CPU PATH DISTANCE
# =========================================================

def get_shortest_path_distance(
    player
):

    start = (
        player["row"],
        player["col"]
    )

    goal_row = player["goal"]

    queue = deque()

    queue.append(
        (
            start,
            0
        )
    )

    visited = set()

    visited.add(
        start
    )

    while queue:

        (row, col), distance = queue.popleft()

        if row == goal_row:

            return distance

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
                        (
                            nr,
                            nc
                        ),
                        distance + 1
                    )
                )

    return 999


# =========================================================
# CPU MOVE EVALUATION
# =========================================================

def evaluate_cpu_move_advanced(
    row,
    col
):

    cpu = player2
    opponent = player1

    score = 0

    # =====================================================
    # CPUの現在位置からの距離
    # =====================================================

    current_distance = get_shortest_path_distance(
        cpu
    )

    # =====================================================
    # 仮にCPUを移動
    # =====================================================

    old_row = cpu["row"]
    old_col = cpu["col"]

    cpu["row"] = row
    cpu["col"] = col

    new_distance = get_shortest_path_distance(
        cpu
    )

    # =====================================================
    # 元に戻す
    # =====================================================

    cpu["row"] = old_row
    cpu["col"] = old_col

    # =====================================================
    # 距離が短くなったら高評価
    # =====================================================

    score += (
        current_distance
        -
        new_distance
    ) * 100

    # =====================================================
    # 相手のゴールまでの距離
    # =====================================================

    opponent_distance = get_shortest_path_distance(
        opponent
    )

    # =====================================================
    # 相手より先にゴールできるなら加点
    # =====================================================

    if new_distance < opponent_distance:

        score += 80

    elif new_distance == opponent_distance:

        score += 20

    else:

        score -= 30

    # =====================================================
    # ゴール到達
    # =====================================================

    if row == cpu["goal"]:

        score += 10000

    # =====================================================
    # 中央寄りのマスを少し評価
    # =====================================================

    center_distance = abs(
        col - 4
    )

    score += (
        4 - center_distance
    ) * 3

    return score


# =========================================================
# CPU SELECT BEST MOVE
# =========================================================

def cpu_select_best_move():

    cpu = player2

    legal_moves = get_legal_moves(
        cpu
    )

    if not legal_moves:

        return None

    # =====================================================
    # LEVEL 1
    # =====================================================

    if cpu_level == 1:

        best_move = random.choice(
            legal_moves
        )

        best_score = -999999

        for move in legal_moves:

            row, col = move

            score = evaluate_cpu_move(
                row,
                col
            )

            # 少しランダム性を残す
            score += random.randint(
                -20,
                20
            )

            if score > best_score:

                best_score = score

                best_move = move

        return best_move

    # =====================================================
    # LEVEL 2
    # =====================================================

    if cpu_level == 2:

        best_move = None

        best_score = -999999

        for move in legal_moves:

            row, col = move

            score = evaluate_cpu_move_advanced(
                row,
                col
            )

            score += random.randint(
                -8,
                8
            )

            if score > best_score:

                best_score = score

                best_move = move

        return best_move

    # =====================================================
    # LEVEL 3
    # =====================================================

    best_move = None

    best_score = -999999

    for move in legal_moves:

        row, col = move

        score = evaluate_cpu_move_advanced(
            row,
            col
        )

        # =================================================
        # 相手の次の手も考える
        # =================================================

        old_row = cpu["row"]
        old_col = cpu["col"]

        cpu["row"] = row
        cpu["col"] = col

        opponent_moves = get_legal_moves(
            player1
        )

        worst_reply = 0

        if opponent_moves:

            opponent_best = -999999

            for opponent_move in opponent_moves:

                opponent_row, opponent_col = opponent_move

                opponent_old_row = player1["row"]
                opponent_old_col = player1["col"]

                player1["row"] = opponent_row
                player1["col"] = opponent_col

                opponent_distance = get_shortest_path_distance(
                    player1
                )

                player1["row"] = opponent_old_row
                player1["col"] = opponent_old_col

                reply_score = (
                    -opponent_distance * 100
                )

                if opponent_distance == 0:

                    reply_score += 10000

                if reply_score > opponent_best:

                    opponent_best = reply_score

            worst_reply = opponent_best

        cpu["row"] = old_row
        cpu["col"] = old_col

        score -= worst_reply * 0.5

        score += random.randint(
            -3,
            3
        )

        if score > best_score:

            best_score = score

            best_move = move

    return best_move


# =========================================================
# CPU MOVE
# =========================================================

def cpu_move():

    global game_over

    if game_over:

        return

    cpu = player2

    # =====================================================
    # CPUの移動候補
    # =====================================================

    best_move = cpu_select_best_move()

    if best_move is None:

        change_turn()

        return

    # =====================================================
    # 移動
    # =====================================================

    cpu["row"] = best_move[0]

    cpu["col"] = best_move[1]

    # =====================================================
    # 勝利判定
    # =====================================================

    if check_win(cpu):

        game_over = True

        return

    # =====================================================
    # プレイヤー1へ
    # =====================================================

    change_turn()


# =========================================================
# CPU WALL EVALUATION
# =========================================================

def evaluate_cpu_wall(
    kind,
    row,
    col
):

    if not can_place_wall(
        kind,
        row,
        col
    ):

        return -999999

    cpu = player2
    opponent = player1

    # =====================================================
    # 壁を仮設置
    # =====================================================

    apply_wall(
        kind,
        row,
        col
    )

    cpu_distance = get_shortest_path_distance(
        cpu
    )

    opponent_distance = get_shortest_path_distance(
        opponent
    )

    # =====================================================
    # 壁を削除
    # =====================================================

    if kind == "H":

        horizontal_walls.remove(
            (
                row,
                col
            )
        )

    else:

        vertical_walls.remove(
            (
                row,
                col
            )
        )

    # =====================================================
    # 評価
    # =====================================================

    score = 0

    # 自分の道は短いほど良い
    score -= cpu_distance * 50

    # 相手の道は長いほど良い
    score += opponent_distance * 80

    # 相手を遅らせる効果
    score += (
        opponent_distance
        -
        cpu_distance
    ) * 20

    return score


# =========================================================
# CPU SELECT BEST WALL
# =========================================================

def cpu_select_best_wall():

    cpu = player2

    if cpu["walls"] <= 0:

        return None

    candidates = []

    # =====================================================
    # 全壁候補
    # =====================================================

    for row in range(8):

        for col in range(8):

            candidates.append(
                (
                    "H",
                    row,
                    col
                )
            )

            candidates.append(
                (
                    "V",
                    row,
                    col
                )
            )

    # =====================================================
    # LEVEL 1
    # =====================================================

    if cpu_level == 1:

        random.shuffle(
            candidates
        )

        for kind, row, col in candidates:

            if can_place_wall(
                kind,
                row,
                col
            ):

                # 簡単CPUは低確率で壁を使う

                if random.random() < 0.25:

                    return (
                        kind,
                        row,
                        col
                    )

        return None

    # =====================================================
    # LEVEL 2 / 3
    # =====================================================

    best_wall = None

    best_score = -999999

    for kind, row, col in candidates:

        score = evaluate_cpu_wall(
            kind,
            row,
            col
        )

        if score > best_score:

            best_score = score

            best_wall = (
                kind,
                row,
                col
            )

    return best_wall


# =========================================================
# CPU PLACE WALL
# =========================================================

def cpu_place_wall():

    global game_over

    if game_over:

        return

    cpu = player2

    if cpu["walls"] <= 0:

        return

    wall = cpu_select_best_wall()

    if wall is None:

        return

    kind, row, col = wall

    if not can_place_wall(
        kind,
        row,
        col
    ):

        return

    apply_wall(
        kind,
        row,
        col
    )

    cpu["walls"] -= 1


# =========================================================
# CPU DECISION
# =========================================================

def cpu_decide_action():

    cpu = player2

    if cpu["walls"] <= 0:

        return "move"

    # =====================================================
    # LEVEL 1
    # =====================================================

    if cpu_level == 1:

        if random.random() < 0.25:

            return "wall"

        return "move"

    # =====================================================
    # LEVEL 2
    # =====================================================

    if cpu_level == 2:

        cpu_distance = get_shortest_path_distance(
            cpu
        )

        opponent_distance = get_shortest_path_distance(
            player1
        )

        if (
            opponent_distance
            <=
            cpu_distance + 1
        ):

            return "wall"

        if random.random() < 0.25:

            return "wall"

        return "move"

    # =====================================================
    # LEVEL 3
    # =====================================================

    cpu_distance = get_shortest_path_distance(
        cpu
    )

    opponent_distance = get_shortest_path_distance(
        player1
    )

    # 相手がかなり近い場合
    if opponent_distance <= cpu_distance:

        return "wall"

    # 自分がゴール目前なら移動
    if cpu_distance <= 2:

        return "move"

    # それ以外は状況によって壁
    if opponent_distance <= cpu_distance + 2:

        return "wall"

    return "move"


# =========================================================
# CPU TURN
# =========================================================

def cpu_turn():

    global cpu_waiting
    global cpu_wait_start

    if not cpu_mode:

        return

    if game_over:

        return

    # =====================================================
    # CPU = PLAYER 2
    # =====================================================

    if turn != 2:

        return

    # =====================================================
    # CPUのターン開始
    # =====================================================

    if not cpu_waiting:

        cpu_waiting = True

        cpu_wait_start = pygame.time.get_ticks()

        return

    # =====================================================
    # 0.5秒待つ
    # =====================================================

    current_time = pygame.time.get_ticks()

    elapsed_time = (
        current_time
        -
        cpu_wait_start
    )

    if elapsed_time < 500:

        return

    # =====================================================
    # CPU行動
    # =====================================================

    cpu_waiting = False

    action = cpu_decide_action()

    # =====================================================
    # 移動
    # =====================================================

    if action == "move":

        cpu_move()

    # =====================================================
    # 壁
    # =====================================================

    elif action == "wall":

        cpu_place_wall()

        # 壁を置いたらターン交代
        change_turn()


# =========================================================
# INITIALIZE CPU TIMER
# =========================================================

cpu_waiting = False

cpu_wait_start = 0


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
            # TITLE SCREEN
            # =============================================

            if scene == "title":

                if event.key == pygame.K_ESCAPE:

                    running = False

                continue

            # =============================================
            # CPU LEVEL SELECT
            # =============================================

            if scene == "cpu_select":

                if event.key == pygame.K_ESCAPE:

                    scene = "title"

                continue

            # =============================================
            # GAME SCREEN
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

            # =================================================
            # TITLE SCREEN
            # =================================================

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

                # ---------------------------------------------
                # PLAYER vs PLAYER
                # ---------------------------------------------

                if pvp_button.collidepoint(
                    mouse_x,
                    mouse_y
                ):

                    cpu_mode = False

                    scene = "game"

                    reset_game()

                # ---------------------------------------------
                # PLAYER vs CPU
                # ---------------------------------------------

                elif cpu_button.collidepoint(
                    mouse_x,
                    mouse_y
                ):

                    cpu_mode = True

                    scene = "cpu_select"

                continue

            # =================================================
            # CPU LEVEL SELECT
            # =================================================

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

                # ---------------------------------------------
                # LEVEL 1
                # ---------------------------------------------

                if level1_button.collidepoint(
                    mouse_x,
                    mouse_y
                ):

                    cpu_level = 1

                    scene = "game"

                    reset_game()

                # ---------------------------------------------
                # LEVEL 2
                # ---------------------------------------------

                elif level2_button.collidepoint(
                    mouse_x,
                    mouse_y
                ):

                    cpu_level = 2

                    scene = "game"

                    reset_game()

                # ---------------------------------------------
                # LEVEL 3
                # ---------------------------------------------

                elif level3_button.collidepoint(
                    mouse_x,
                    mouse_y
                ):

                    cpu_level = 3

                    scene = "game"

                    reset_game()

                # ---------------------------------------------
                # BACK
                # ---------------------------------------------

                elif back_button.collidepoint(
                    mouse_x,
                    mouse_y
                ):

                    scene = "title"

                continue

            # =================================================
            # GAME SCREEN
            # =================================================

            # ---------------------------------------------
            # RESET BUTTON
            # ---------------------------------------------

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

            # ---------------------------------------------
            # GAME OVER
            # ---------------------------------------------

            if game_over:

                continue

            # ---------------------------------------------
            # CPU TURN
            # ---------------------------------------------

            if cpu_mode and turn == 2:

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

        # =================================================
        # GAME SCREEN
        # =================================================

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
    # DISPLAY UPDATE
    # =====================================================

    pygame.display.flip()

    clock.tick(FPS)


# =========================================================
# QUIT
# =========================================================

pygame.quit()

sys.exit()