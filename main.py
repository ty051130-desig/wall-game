import pygame
import sys
import random
import asyncio
from collections import deque


# =========================================================
# WEB
# =========================================================

IS_WEB = (
    sys.platform == "emscripten"
)


# =========================================================
# SETTINGS
# =========================================================

BOARD_SIZE = 9
CELL_SIZE = 70

BOARD_X = 70
BOARD_Y = 80

WINDOW_WIDTH = 850
WINDOW_HEIGHT = 950

FPS = 60

WALL_WIDTH = 12

# CPUの思考時間
CPU_THINK_TIME = 500


# =========================================================
# MOBILE / TOUCH SETTINGS
# =========================================================

MOBILE_BUTTON_Y = 840
MOBILE_BUTTON_HEIGHT = 75

# 壁をタップするときの判定範囲
# PCのマウスより少し広め
WALL_TOUCH_RANGE = 28


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
    (
        WINDOW_WIDTH,
        WINDOW_HEIGHT
    )
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

win_font = pygame.font.SysFont(
    "Arial",
    72,
    bold=True
)

win_sub_font = pygame.font.SysFont(
    "Arial",
    26,
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
# WALL PREVIEW STATE
# =========================================================

# 現在選択している向き
# "H" = 横
# "V" = 縦
wall_selected_kind = "H"

# 仮置き中の壁
# ("H", row, col)
# ("V", row, col)
# None
wall_preview_candidate = None


# =========================================================
# WALL OPTION BUTTONS
# =========================================================

WALL_OPTION_Y = 755
WALL_OPTION_HEIGHT = 58


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
# WALL DRAG STATE
# =========================================================

wall_dragging = False

wall_drag_start_x = 0
wall_drag_start_y = 0

wall_drag_x = 0
wall_drag_y = 0

# "H" / "V" / None
wall_drag_kind = None

# ("H", row, col) / ("V", row, col) / None
wall_drag_candidate = None


# =========================================================
# CPU POSITION HISTORY
#
# LEVEL3の往復防止用
# =========================================================

cpu_position_history = [
    (
        player2["row"],
        player2["col"]
    )
]

CPU_POSITION_HISTORY_LIMIT = 8


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

def cell_position(
    row,
    col
):

    x = (
        BOARD_X
        +
        col * CELL_SIZE
    )

    y = (
        BOARD_Y
        +
        row * CELL_SIZE
    )

    return x, y


# =========================================================
# MOUSE TO CELL
# =========================================================

def mouse_to_cell(
    mouse_x,
    mouse_y
):

    col = (
        mouse_x
        -
        BOARD_X
    ) // CELL_SIZE

    row = (
        mouse_y
        -
        BOARD_Y
    ) // CELL_SIZE

    if (
        0 <= row < BOARD_SIZE
        and
        0 <= col < BOARD_SIZE
    ):

        return (
            int(row),
            int(col)
        )

    return None


# =========================================================
# WALL COLLISION
# =========================================================

def blocked(
    row1,
    col1,
    row2,
    col2
):

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

def get_neighbors(
    row,
    col
):

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
            (
                nr,
                nc
            )
        )

    return result


# =========================================================
# SHORTEST PATH
#
# CPUが実際の壁を考慮して
# ゴールまでの最短距離を計算する
# =========================================================

def get_shortest_path(
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
            [start]
        )
    )

    visited = set()

    visited.add(
        start
    )

    while queue:

        current, path = queue.popleft()

        row, col = current

        # =================================================
        # ゴール到達
        # =================================================

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

def get_shortest_distance(
    player
):

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

def get_next_path_position(
    player
):

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

def has_path(
    player
):

    start = (
        player["row"],
        player["col"]
    )

    goal_row = player["goal"]

    queue = deque()

    queue.append(
        start
    )

    visited = set()

    visited.add(
        start
    )

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
                    nc
                )
            )

    return False


# =========================================================
# WALL CAN PLACE
#
# 壁を設置できるか判定する
# =========================================================

def can_place_wall(
    kind,
    row,
    col
):

    # =====================================================
    # 座標範囲
    # =====================================================

    if not (
        0 <= row < 8
        and
        0 <= col < 8
    ):

        return False


    # =====================================================
    # HORIZONTAL WALL
    # =====================================================

    if kind == "H":

        # -------------------------------------------------
        # 同じ壁
        # -------------------------------------------------

        if (
            row,
            col
        ) in horizontal_walls:

            return False

        # -------------------------------------------------
        # 横方向に重なる壁
        # -------------------------------------------------

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

        # -------------------------------------------------
        # 垂直壁との交差
        #
        # H(row,col) と V(row,col) が交差
        # -------------------------------------------------

        if (
            row,
            col
        ) in vertical_walls:

            return False

        # -------------------------------------------------
        # 仮設置
        # -------------------------------------------------

        horizontal_walls.add(
            (
                row,
                col
            )
        )

        # -------------------------------------------------
        # 両プレイヤーの経路確認
        # -------------------------------------------------

        p1_ok = has_path(
            player1
        )

        p2_ok = has_path(
            player2
        )

        # -------------------------------------------------
        # 仮設置した壁を削除
        # -------------------------------------------------

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

        # -------------------------------------------------
        # 同じ壁
        # -------------------------------------------------

        if (
            row,
            col
        ) in vertical_walls:

            return False

        # -------------------------------------------------
        # 縦方向に重なる壁
        # -------------------------------------------------

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

        # -------------------------------------------------
        # 水平壁との交差
        #
        # V(row,col) と H(row,col) が交差
        # -------------------------------------------------

        if (
            row,
            col
        ) in horizontal_walls:

            return False

        # -------------------------------------------------
        # 仮設置
        # -------------------------------------------------

        vertical_walls.add(
            (
                row,
                col
            )
        )

        # -------------------------------------------------
        # 両プレイヤーの経路確認
        # -------------------------------------------------

        p1_ok = has_path(
            player1
        )

        p2_ok = has_path(
            player2
        )

        # -------------------------------------------------
        # 仮設置した壁を削除
        # -------------------------------------------------

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


    # =====================================================
    # 不正な種類
    # =====================================================

    return False


# =========================================================
# SIMULATE WALL
#
# 壁を一時的に置いて、
# その結果を調べる
# =========================================================

def simulate_wall(
    kind,
    row,
    col
):

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

    # =====================================================
    # 情報を返す
    # =====================================================

    return {
        "cpu_distance": cpu_distance,
        "player_distance": player_distance,
        "cpu_path": cpu_path,
        "player_path": player_path
    }


# =========================================================
# WALL EFFECT
#
# 壁を置く前と置いた後で
# 距離がどれだけ変化したかを調べる
# =========================================================

def evaluate_wall_effect(
    kind,
    row,
    col
):

    before_cpu = get_shortest_distance(
        player2
    )

    before_player = get_shortest_distance(
        player1
    )

    result = simulate_wall(
        kind,
        row,
        col
    )

    if result is None:

        return None

    after_cpu = result[
        "cpu_distance"
    ]

    after_player = result[
        "player_distance"
    ]

    cpu_loss = (
        after_cpu
        -
        before_cpu
    )

    opponent_gain = (
        after_player
        -
        before_player
    )

    return {
        "cpu_before": before_cpu,
        "cpu_after": after_cpu,
        "player_before": before_player,
        "player_after": after_player,
        "cpu_loss": cpu_loss,
        "opponent_gain": opponent_gain
    }


# =========================================================
# ALL LEGAL WALLS
#
# 現在設置可能な壁をすべて取得
# =========================================================

def get_all_legal_walls():

    walls = []

    for row in range(8):

        for col in range(8):

            # -------------------------------------------------
            # HORIZONTAL
            # -------------------------------------------------

            if can_place_wall(
                "H",
                row,
                col
            ):

                walls.append(
                    (
                        "H",
                        row,
                        col
                    )
                )

            # -------------------------------------------------
            # VERTICAL
            # -------------------------------------------------

            if can_place_wall(
                "V",
                row,
                col
            ):

                walls.append(
                    (
                        "V",
                        row,
                        col
                    )
                )

    return walls


# =========================================================
# WALL DISTANCE GAIN
#
# 壁によって相手の最短距離が
# どれだけ伸びるかを調べる
# =========================================================

def get_wall_distance_gain(
    wall
):

    kind, row, col = wall

    result = evaluate_wall_effect(
        kind,
        row,
        col
    )

    if result is None:

        return None

    return result


# =========================================================
# LEGAL MOVES
#
# プレイヤーが現在移動できるマスを取得
#
# ・通常移動
# ・相手を飛び越えるジャンプ
# ・ジャンプできない場合の斜め移動
# =========================================================

def get_legal_moves(
    player
):

    row = player["row"]
    col = player["col"]

    opponent = get_opponent(
        player
    )

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

        # =================================================
        # 盤面外
        # =================================================

        if not (
            0 <= next_row < BOARD_SIZE
            and
            0 <= next_col < BOARD_SIZE
        ):

            continue

        # =================================================
        # 壁で遮られている
        # =================================================

        if blocked(
            row,
            col,
            next_row,
            next_col
        ):

            continue

        # =================================================
        # 通常移動
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
        # 相手が隣にいる
        #
        # まず直線ジャンプを確認
        # =================================================

        jump_row = (
            next_row
            +
            dr
        )

        jump_col = (
            next_col
            +
            dc
        )

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
        # 直線ジャンプできない場合
        #
        # 相手の横へ回り込む
        # =================================================

        if dr != 0:

            # 上下方向で相手と接している
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

            # 左右方向で相手と接している
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

            # =============================================
            # 盤面外
            # =============================================

            if not (
                0 <= side_row < BOARD_SIZE
                and
                0 <= side_col < BOARD_SIZE
            ):

                continue

            # =============================================
            # 相手位置から横へ移動できるか
            # =============================================

            if blocked(
                next_row,
                next_col,
                side_row,
                side_col
            ):

                continue

            # =============================================
            # 念のため相手自身の位置は除外
            # =============================================

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

    # =====================================================
    # 重複除去
    #
    # 順番は維持する
    # =====================================================

    unique_moves = []

    seen = set()

    for move in moves:

        if move in seen:

            continue

        seen.add(
            move
        )

        unique_moves.append(
            move
        )

    return unique_moves


# =========================================================
# SAVE GAME STATE
#
# AIが仮想的に何手も読むときに、
# 現在の盤面を完全に保存する
# =========================================================

def save_game_state():

    return {
        "player1_row": player1["row"],
        "player1_col": player1["col"],
        "player1_walls": player1["walls"],

        "player2_row": player2["row"],
        "player2_col": player2["col"],
        "player2_walls": player2["walls"],

        "horizontal_walls": set(
            horizontal_walls
        ),

        "vertical_walls": set(
            vertical_walls
        )
    }


# =========================================================
# RESTORE GAME STATE
#
# AIの仮想手をすべて元に戻す
# =========================================================

def restore_game_state(
    state
):

    # =====================================================
    # PLAYER 1
    # =====================================================

    player1["row"] = state[
        "player1_row"
    ]

    player1["col"] = state[
        "player1_col"
    ]

    player1["walls"] = state[
        "player1_walls"
    ]

    # =====================================================
    # PLAYER 2
    # =====================================================

    player2["row"] = state[
        "player2_row"
    ]

    player2["col"] = state[
        "player2_col"
    ]

    player2["walls"] = state[
        "player2_walls"
    ]

    # =====================================================
    # WALLS
    # =====================================================

    horizontal_walls.clear()

    horizontal_walls.update(
        state[
            "horizontal_walls"
        ]
    )

    vertical_walls.clear()

    vertical_walls.update(
        state[
            "vertical_walls"
        ]
    )


# =========================================================
# WALLS THAT BLOCK AN EDGE
#
# 最短経路上の
#
# (row1,col1) → (row2,col2)
#
# を遮る可能性がある壁を求める
# =========================================================

def get_walls_for_edge(
    row1,
    col1,
    row2,
    col2
):

    candidates = []

    # =====================================================
    # 上下移動を防ぐ水平壁
    # =====================================================

    if col1 == col2:

        boundary_row = min(
            row1,
            row2
        )

        # -------------------------------------------------
        # 対象マスの右側を起点にする壁
        # -------------------------------------------------

        if (
            0 <= boundary_row < 8
            and
            0 <= col1 < 8
        ):

            candidates.append(
                (
                    "H",
                    boundary_row,
                    col1
                )
            )

        # -------------------------------------------------
        # 対象マスの左側を起点にする壁
        # -------------------------------------------------

        if (
            0 <= boundary_row < 8
            and
            0 <= col1 - 1 < 8
        ):

            candidates.append(
                (
                    "H",
                    boundary_row,
                    col1 - 1
                )
            )

    # =====================================================
    # 左右移動を防ぐ垂直壁
    # =====================================================

    elif row1 == row2:

        boundary_col = min(
            col1,
            col2
        )

        # -------------------------------------------------
        # 対象マスの下側を起点にする壁
        # -------------------------------------------------

        if (
            0 <= row1 < 8
            and
            0 <= boundary_col < 8
        ):

            candidates.append(
                (
                    "V",
                    row1,
                    boundary_col
                )
            )

        # -------------------------------------------------
        # 対象マスの上側を起点にする壁
        # -------------------------------------------------

        if (
            0 <= row1 - 1 < 8
            and
            0 <= boundary_col < 8
        ):

            candidates.append(
                (
                    "V",
                    row1 - 1,
                    boundary_col
                )
            )

    return candidates


# =========================================================
# WALL EFFECT FOR PLAYER
#
# wall_player が壁を置いた場合に
#
# target_playerをどれくらい遅らせられるか
#
# を評価する
# =========================================================

def evaluate_wall_for_player(
    wall_player,
    target_player,
    kind,
    row,
    col
):

    # =====================================================
    # 設置できない壁
    # =====================================================

    if not can_place_wall(
        kind,
        row,
        col
    ):

        return None

    # =====================================================
    # 現在の距離
    # =====================================================

    before_self = get_shortest_distance(
        wall_player
    )

    before_target = get_shortest_distance(
        target_player
    )

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
    # 壁設置後
    # =====================================================

    after_self = get_shortest_distance(
        wall_player
    )

    after_target = get_shortest_distance(
        target_player
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
    # 変化量
    # =====================================================

    target_gain = (
        after_target
        -
        before_target
    )

    self_loss = (
        after_self
        -
        before_self
    )

    # =====================================================
    # 評価
    #
    # 相手の距離を伸ばす → 高評価
    # 自分の距離を伸ばす → 減点
    # =====================================================

    score = (
        target_gain * 120
        -
        self_loss * 90
    )

    return {
        "score": score,
        "target_gain": target_gain,
        "self_loss": self_loss,
        "self_distance": after_self,
        "target_distance": after_target
    }


# =========================================================
# PATH WALL CANDIDATES
#
# target_player の最短経路上にある
# 有力な壁だけを候補にする
#
# 全128候補を毎回調査しないことで
# LEVEL 3の計算量爆発を防ぐ
# =========================================================

def get_path_wall_candidates(
    wall_player,
    target_player,
    limit=8
):

    if wall_player["walls"] <= 0:

        return []

    path = get_shortest_path(
        target_player
    )

    if path is None:

        return []

    if len(path) < 2:

        return []

    raw_candidates = []

    seen = set()

    # =====================================================
    # 最短経路の前半を中心に調べる
    #
    # ゴールまで全て見ると候補数が増えるため
    # 最大6辺まで
    # =====================================================

    edge_count = min(
        len(path) - 1,
        6
    )

    for index in range(
        edge_count
    ):

        row1, col1 = path[
            index
        ]

        row2, col2 = path[
            index + 1
        ]

        edge_walls = get_walls_for_edge(
            row1,
            col1,
            row2,
            col2
        )

        for wall in edge_walls:

            if wall in seen:

                continue

            seen.add(
                wall
            )

            raw_candidates.append(
                wall
            )

    # =====================================================
    # 経路周辺の候補が少ない場合に備えて、
    # 相手の現在地付近も追加
    # =====================================================

    target_row = target_player[
        "row"
    ]

    target_col = target_player[
        "col"
    ]

    for row_offset in (
        -1,
        0
    ):

        for col_offset in (
            -1,
            0
        ):

            wall_row = (
                target_row
                +
                row_offset
            )

            wall_col = (
                target_col
                +
                col_offset
            )

            for kind in (
                "H",
                "V"
            ):

                wall = (
                    kind,
                    wall_row,
                    wall_col
                )

                if wall in seen:

                    continue

                if not (
                    0 <= wall_row < 8
                    and
                    0 <= wall_col < 8
                ):

                    continue

                seen.add(
                    wall
                )

                raw_candidates.append(
                    wall
                )

    # =====================================================
    # 各候補を評価
    # =====================================================

    scored_candidates = []

    for kind, row, col in raw_candidates:

        result = evaluate_wall_for_player(
            wall_player,
            target_player,
            kind,
            row,
            col
        )

        if result is None:

            continue

        # =================================================
        # 明らかに自分だけを苦しめる壁は除外
        # =================================================

        if (
            result["target_gain"] <= 0
            and
            result["self_loss"] > 0
        ):

            continue

        score = result[
            "score"
        ]

        # =================================================
        # 相手の経路を実際に伸ばす壁には追加点
        # =================================================

        if result["target_gain"] > 0:

            score += (
                result["target_gain"]
                *
                80
            )

        # =================================================
        # 自分の道を悪化させない壁を少し優遇
        # =================================================

        if result["self_loss"] == 0:

            score += 15

        scored_candidates.append(
            (
                score,
                kind,
                row,
                col
            )
        )

    # =====================================================
    # 強い順に並べる
    # =====================================================

    scored_candidates.sort(
        key=lambda item: item[0],
        reverse=True
    )

    return scored_candidates[
        :limit
    ]


# =========================================================
# CPU PROMISING WALLS
#
# CPU用の有力壁候補
#
# 戻り値は必ず
#
# (score, kind, row, col)
#
# に統一する
# =========================================================

def get_cpu_promising_walls(
    limit=8
):

    return get_path_wall_candidates(
        player2,
        player1,
        limit
    )


# =========================================================
# PLAYER PROMISING WALLS
#
# LEVEL 3が
# 「プレイヤーならどの壁を置くか」
# を予測するために使用
#
# 戻り値は同じく
#
# (score, kind, row, col)
# =========================================================

def get_player_promising_walls(
    limit=6
):

    return get_path_wall_candidates(
        player1,
        player2,
        limit
    )


# =========================================================
# POSITION EVALUATION
#
# CPU側から見た現在の盤面評価
#
# 高いほどCPU有利
# =========================================================

def evaluate_position_for_cpu():

    # =====================================================
    # 勝敗
    # =====================================================

    if player2["row"] == player2["goal"]:

        return 1000000

    if player1["row"] == player1["goal"]:

        return -1000000

    # =====================================================
    # 最短距離
    # =====================================================

    cpu_distance = get_shortest_distance(
        player2
    )

    player_distance = get_shortest_distance(
        player1
    )

    # =====================================================
    # 基本評価
    #
    # 相手が遠いほど良い
    # 自分が近いほど良い
    # =====================================================

    score = (
        player_distance
        -
        cpu_distance
    ) * 120

    # =====================================================
    # 壁の残数
    # =====================================================

    wall_difference = (
        player2["walls"]
        -
        player1["walls"]
    )

    score += (
        wall_difference
        *
        8
    )

    # =====================================================
    # ゴール目前
    # =====================================================

    if cpu_distance == 1:

        score += 500

    elif cpu_distance == 2:

        score += 180

    if player_distance == 1:

        score -= 700

    elif player_distance == 2:

        score -= 250

    # =====================================================
    # 移動可能方向の多さ
    # =====================================================

    cpu_mobility = len(
        get_legal_moves(
            player2
        )
    )

    player_mobility = len(
        get_legal_moves(
            player1
        )
    )

    score += (
        cpu_mobility
        -
        player_mobility
    ) * 4

    return score



# =========================================================
# AI ACTION FORMAT
#
# 移動:
# ("M", row, col)
#
# 壁:
# ("W", kind, row, col)
# =========================================================


# =========================================================
# CREATE MOVE ACTION
# =========================================================

def make_move_action(
    row,
    col
):

    return (
        "M",
        row,
        col
    )


# =========================================================
# CREATE WALL ACTION
# =========================================================

def make_wall_action(
    kind,
    row,
    col
):

    return (
        "W",
        kind,
        row,
        col
    )


# =========================================================
# APPLY AI ACTION
#
# AI探索用
#
# True  = 実行成功
# False = 実行不可
# =========================================================

def apply_ai_action(
    player,
    action
):

    if action is None:

        return False

    action_type = action[0]

    # =====================================================
    # MOVE
    # =====================================================

    if action_type == "M":

        if len(action) != 3:

            return False

        row = action[1]
        col = action[2]

        legal_moves = get_legal_moves(
            player
        )

        if (
            row,
            col
        ) not in legal_moves:

            return False

        player["row"] = row
        player["col"] = col

        return True

    # =====================================================
    # WALL
    # =====================================================

    if action_type == "W":

        if len(action) != 4:

            return False

        if player["walls"] <= 0:

            return False

        kind = action[1]
        row = action[2]
        col = action[3]

        if not can_place_wall(
            kind,
            row,
            col
        ):

            return False

        apply_wall(
            kind,
            row,
            col
        )

        player["walls"] -= 1

        return True

    return False


# =========================================================
# CPU MOVE ACTION SCORE
#
# CPUが1マス移動した場合の評価
# =========================================================

def evaluate_cpu_move_action(
    row,
    col
):

    state = save_game_state()

    action = make_move_action(
        row,
        col
    )

    success = apply_ai_action(
        player2,
        action
    )

    if not success:

        restore_game_state(
            state
        )

        return -9999999

    # =====================================================
    # ゴールなら最優先
    # =====================================================

    if player2["row"] == player2["goal"]:

        score = 1000000

        restore_game_state(
            state
        )

        return score

    # =====================================================
    # 通常評価
    # =====================================================

    score = evaluate_position_for_cpu()

    # =====================================================
    # ゴール方向へ前進した場合は少し加点
    # =====================================================

    old_distance = abs(
        state["player2_row"]
        -
        player2["goal"]
    )

    new_distance = abs(
        player2["row"]
        -
        player2["goal"]
    )

    if new_distance < old_distance:

        score += 30

    elif new_distance > old_distance:

        score -= 25

    # =====================================================
    # 中央付近をわずかに評価
    # =====================================================

    center_distance = abs(
        player2["col"]
        -
        4
    )

    score += (
        4
        -
        center_distance
    ) * 2

    restore_game_state(
        state
    )

    return score


# =========================================================
# CPU WALL ACTION SCORE
#
# CPUが壁を置いた場合の評価
# =========================================================

def evaluate_cpu_wall_action(
    kind,
    row,
    col
):

    if player2["walls"] <= 0:

        return -9999999

    # =====================================================
    # 壁単体の効果
    # =====================================================

    effect = evaluate_wall_for_player(
        player2,
        player1,
        kind,
        row,
        col
    )

    if effect is None:

        return -9999999

    state = save_game_state()

    action = make_wall_action(
        kind,
        row,
        col
    )

    success = apply_ai_action(
        player2,
        action
    )

    if not success:

        restore_game_state(
            state
        )

        return -9999999

    # =====================================================
    # 盤面全体評価
    # =====================================================

    score = evaluate_position_for_cpu()

    # =====================================================
    # 壁そのものの効果
    # =====================================================

    score += (
        effect["target_gain"]
        *
        130
    )

    score -= (
        effect["self_loss"]
        *
        110
    )

    # =====================================================
    # 自分の道を悪化させない壁を評価
    # =====================================================

    if effect["self_loss"] == 0:

        score += 25

    # =====================================================
    # 相手を1以上遅らせる
    # =====================================================

    if effect["target_gain"] >= 1:

        score += 80

    # =====================================================
    # 相手を2以上遅らせる強い壁
    # =====================================================

    if effect["target_gain"] >= 2:

        score += 150

    # =====================================================
    # 残り壁が少ない場合は節約
    # =====================================================

    if state["player2_walls"] <= 3:

        score -= 50

    if state["player2_walls"] <= 1:

        score -= 100

    restore_game_state(
        state
    )

    return score


# =========================================================
# BEST CPU MOVE ACTION
#
# 現在の合法移動の中で
# 最も評価の高い移動
# =========================================================

def get_best_cpu_move_action(
    randomness=0
):

    legal_moves = get_legal_moves(
        player2
    )

    if not legal_moves:

        return (
            None,
            -9999999
        )

    best_action = None
    best_score = -9999999

    for row, col in legal_moves:

        score = evaluate_cpu_move_action(
            row,
            col
        )

        # =================================================
        # LEVELによって少しランダム性を入れる
        # =================================================

        if randomness > 0:

            score += random.randint(
                -randomness,
                randomness
            )

        if score > best_score:

            best_score = score

            best_action = make_move_action(
                row,
                col
            )

    return (
        best_action,
        best_score
    )


# =========================================================
# BEST CPU WALL ACTION
#
# PART3で絞った有力壁から
# 最善の壁を探す
# =========================================================

def get_best_cpu_wall_action(
    limit=8,
    randomness=0
):

    if player2["walls"] <= 0:

        return (
            None,
            -9999999
        )

    candidates = get_cpu_promising_walls(
        limit
    )

    if not candidates:

        return (
            None,
            -9999999
        )

    best_action = None
    best_score = -9999999

    for (
        candidate_score,
        kind,
        row,
        col
    ) in candidates:

        score = evaluate_cpu_wall_action(
            kind,
            row,
            col
        )

        # =================================================
        # 候補生成時の評価も少し加える
        # =================================================

        score += (
            candidate_score
            *
            0.35
        )

        if randomness > 0:

            score += random.randint(
                -randomness,
                randomness
            )

        if score > best_score:

            best_score = score

            best_action = make_wall_action(
                kind,
                row,
                col
            )

    return (
        best_action,
        best_score
    )


# =========================================================
# LEVEL 1 AI
#
# EASY
#
# ・基本は前進
# ・多少判断を間違える
# ・たまに壁を置く
# =========================================================

def select_level1_action():

    # =====================================================
    # 即ゴールできる場合は必ずゴール
    # =====================================================

    legal_moves = get_legal_moves(
        player2
    )

    for row, col in legal_moves:

        if row == player2["goal"]:

            return make_move_action(
                row,
                col
            )

    # =====================================================
    # 基本の移動
    # =====================================================

    move_action, move_score = (
        get_best_cpu_move_action(
            randomness=35
        )
    )

    # =====================================================
    # 壁がない
    # =====================================================

    if player2["walls"] <= 0:

        return move_action

    # =====================================================
    # EASYでは壁を使う確率は低い
    # =====================================================

    if random.random() > 0.20:

        return move_action

    # =====================================================
    # 有力な壁がある場合だけ壁を検討
    # =====================================================

    wall_action, wall_score = (
        get_best_cpu_wall_action(
            limit=4,
            randomness=20
        )
    )

    if wall_action is None:

        return move_action

    # =====================================================
    # あまりに悪い壁なら置かない
    # =====================================================

    if wall_score < move_score - 100:

        return move_action

    return wall_action


# =========================================================
# LEVEL 2 MOVE SCORE
#
# LEVEL2では
# 相手の次の最善移動まで少し読む
# =========================================================

def evaluate_level2_move_action(
    action
):

    state = save_game_state()

    success = apply_ai_action(
        player2,
        action
    )

    if not success:

        restore_game_state(
            state
        )

        return -9999999

    # =====================================================
    # CPU即勝利
    # =====================================================

    if player2["row"] == player2["goal"]:

        restore_game_state(
            state
        )

        return 1000000

    # =====================================================
    # CPU移動後の基本評価
    # =====================================================

    base_score = evaluate_position_for_cpu()

    # =====================================================
    # 相手の合法手
    # =====================================================

    opponent_moves = get_legal_moves(
        player1
    )

    if not opponent_moves:

        restore_game_state(
            state
        )

        return base_score

    # =====================================================
    # 相手は自分に最も不利な手を選ぶものとする
    # =====================================================

    worst_score = 9999999

    opponent_state = save_game_state()

    for row, col in opponent_moves:

        restore_game_state(
            opponent_state
        )

        opponent_action = make_move_action(
            row,
            col
        )

        success = apply_ai_action(
            player1,
            opponent_action
        )

        if not success:

            continue

        # =================================================
        # 相手が即ゴール
        # =================================================

        if player1["row"] == player1["goal"]:

            score = -1000000

        else:

            score = evaluate_position_for_cpu()

        if score < worst_score:

            worst_score = score

    restore_game_state(
        state
    )

    # =====================================================
    # 今の評価と相手最善手後の評価を混ぜる
    # =====================================================

    return (
        base_score * 0.35
        +
        worst_score * 0.65
    )


# =========================================================
# LEVEL 2 WALL SCORE
#
# 壁を置いた後に
# 相手が最善の「移動」をしたところまで読む
# =========================================================

def evaluate_level2_wall_action(
    action
):

    state = save_game_state()

    success = apply_ai_action(
        player2,
        action
    )

    if not success:

        restore_game_state(
            state
        )

        return -9999999

    # =====================================================
    # 壁直後の評価
    # =====================================================

    base_score = evaluate_position_for_cpu()

    opponent_moves = get_legal_moves(
        player1
    )

    # =====================================================
    # 相手の移動がない場合
    # =====================================================

    if not opponent_moves:

        restore_game_state(
            state
        )

        return base_score

    worst_score = 9999999

    opponent_state = save_game_state()

    for row, col in opponent_moves:

        restore_game_state(
            opponent_state
        )

        opponent_action = make_move_action(
            row,
            col
        )

        success = apply_ai_action(
            player1,
            opponent_action
        )

        if not success:

            continue

        if player1["row"] == player1["goal"]:

            score = -1000000

        else:

            score = evaluate_position_for_cpu()

        if score < worst_score:

            worst_score = score

    restore_game_state(
        state
    )

    return (
        base_score * 0.40
        +
        worst_score * 0.60
    )


# =========================================================
# LEVEL 2 AI
#
# NORMAL
#
# ・最善移動
# ・有力な壁
# ・相手の次の移動
#
# まで考える
# =========================================================

def select_level2_action():

    # =====================================================
    # 即ゴール
    # =====================================================

    legal_moves = get_legal_moves(
        player2
    )

    for row, col in legal_moves:

        if row == player2["goal"]:

            return make_move_action(
                row,
                col
            )

    # =====================================================
    # MOVE候補
    # =====================================================

    best_move = None
    best_move_score = -9999999

    for row, col in legal_moves:

        action = make_move_action(
            row,
            col
        )

        score = evaluate_level2_move_action(
            action
        )

        # =================================================
        # LEVEL2にはごく小さいランダム性
        # =================================================

        score += random.randint(
            -3,
            3
        )

        if score > best_move_score:

            best_move_score = score
            best_move = action

    # =====================================================
    # 壁なしなら移動
    # =====================================================

    if player2["walls"] <= 0:

        return best_move

    # =====================================================
    # WALL候補
    # =====================================================

    wall_candidates = get_cpu_promising_walls(
        limit=6
    )

    best_wall = None
    best_wall_score = -9999999

    for (
        candidate_score,
        kind,
        row,
        col
    ) in wall_candidates:

        action = make_wall_action(
            kind,
            row,
            col
        )

        score = evaluate_level2_wall_action(
            action
        )

        # =================================================
        # 壁自体の妨害能力
        # =================================================

        score += (
            candidate_score
            *
            0.30
        )

        score += random.randint(
            -3,
            3
        )

        if score > best_wall_score:

            best_wall_score = score
            best_wall = action

    # =====================================================
    # 有力な壁がない
    # =====================================================

    if best_wall is None:

        return best_move

    # =====================================================
    # 現在の距離
    # =====================================================

    cpu_distance = get_shortest_distance(
        player2
    )

    opponent_distance = get_shortest_distance(
        player1
    )

    # =====================================================
    # CPUがゴール目前
    #
    # 基本的には進む
    # =====================================================

    if cpu_distance <= 2:

        if (
            opponent_distance
            >
            1
        ):

            return best_move

    # =====================================================
    # 相手がゴール目前
    #
    # 壁を優先する
    # =====================================================

    if opponent_distance <= 2:

        if (
            best_wall_score
            >
            best_move_score - 250
        ):

            return best_wall

    # =====================================================
    # 相手がCPUより近い
    #
    # 防御的に壁を使いやすくする
    # =====================================================

    if opponent_distance < cpu_distance:

        if (
            best_wall_score
            >=
            best_move_score - 100
        ):

            return best_wall

    # =====================================================
    # CPUがかなり先行している場合
    #
    # 壁を節約して進む
    # =====================================================

    if (
        cpu_distance + 3
        <
        opponent_distance
    ):

        return best_move

    # =====================================================
    # 通常時
    #
    # 壁の方が明確に強い場合のみ壁
    # =====================================================

    if (
        best_wall_score
        >
        best_move_score + 30
    ):

        return best_wall

    return best_move


# =========================================================
# LEVEL 3
# AI ACTION GENERATION
#
# Minimaxで使う行動候補を生成する
#
# MOVEは全合法手
# WALLは最短経路付近の有力候補だけ
#
# これによって探索量を抑える
# =========================================================

def generate_ai_actions(
    player,
    wall_limit=4
):

    actions = []

    # =====================================================
    # MOVE ACTIONS
    # =====================================================

    legal_moves = get_legal_moves(
        player
    )

    for row, col in legal_moves:

        actions.append(
            make_move_action(
                row,
                col
            )
        )

    # =====================================================
    # 壁がない場合
    # =====================================================

    if player["walls"] <= 0:

        return actions

    # =====================================================
    # CPU
    # =====================================================

    if player is player2:

        wall_candidates = (
            get_cpu_promising_walls(
                wall_limit
            )
        )

    # =====================================================
    # PLAYER 1
    # =====================================================

    else:

        wall_candidates = (
            get_player_promising_walls(
                wall_limit
            )
        )

    # =====================================================
    # WALL ACTIONS
    # =====================================================

    for (
        score,
        kind,
        row,
        col
    ) in wall_candidates:

        actions.append(
            make_wall_action(
                kind,
                row,
                col
            )
        )

    return actions


# =========================================================
# STATIC ACTION SCORE
#
# Alpha-Betaの効率を上げるため、
# 良さそうな手から先に探索する
#
# CPU   → 高い順
# PLAYER→ 低い順
# =========================================================

def get_static_action_score(
    player,
    action
):

    state = save_game_state()

    success = apply_ai_action(
        player,
        action
    )

    if not success:

        restore_game_state(
            state
        )

        if player is player2:

            return -9999999

        return 9999999

    score = evaluate_position_for_cpu()

    # =====================================================
    # 即勝利をさらに優先
    # =====================================================

    if player2["row"] == player2["goal"]:

        score += 1000000

    if player1["row"] == player1["goal"]:

        score -= 1000000

    restore_game_state(
        state
    )

    return score


# =========================================================
# ORDER AI ACTIONS
#
# Alpha-Betaは強そうな手から調べるほど
# 枝刈りが効きやすい
# =========================================================

def order_ai_actions(
    player,
    actions
):

    scored_actions = []

    for action in actions:

        score = get_static_action_score(
            player,
            action
        )

        scored_actions.append(
            (
                score,
                action
            )
        )

    # =====================================================
    # CPUは高い評価から
    # =====================================================

    if player is player2:

        scored_actions.sort(
            key=lambda item: item[0],
            reverse=True
        )

    # =====================================================
    # PLAYER1はCPUにとって低い評価から
    # =====================================================

    else:

        scored_actions.sort(
            key=lambda item: item[0]
        )

    return [
        action
        for score, action
        in scored_actions
    ]


# =========================================================
# TERMINAL POSITION
#
# ゲーム終了状態か
# =========================================================

def is_terminal_position():

    if (
        player1["row"]
        ==
        player1["goal"]
    ):

        return True

    if (
        player2["row"]
        ==
        player2["goal"]
    ):

        return True

    return False


# =========================================================
# LEVEL 3 MINIMAX
#
# CPU = 最大化
# P1  = 最小化
#
# Alpha-Beta枝刈り付き
# =========================================================

def alpha_beta_minimax(
    depth,
    current_player,
    alpha,
    beta
):

    # =====================================================
    # 終端
    # =====================================================

    if (
        depth <= 0
        or
        is_terminal_position()
    ):

        return evaluate_position_for_cpu()

    # =====================================================
    # 探索する壁候補数
    #
    # 深い層ほど少なくする
    # =====================================================

    if current_player is player1:

        wall_limit = 4

    else:

        wall_limit = 3

    actions = generate_ai_actions(
        current_player,
        wall_limit=wall_limit
    )

    # =====================================================
    # 行動不能
    # =====================================================

    if not actions:

        return evaluate_position_for_cpu()

    # =====================================================
    # 良さそうな手から探索
    # =====================================================

    actions = order_ai_actions(
        current_player,
        actions
    )

    # =====================================================
    # CPU TURN
    #
    # MAX
    # =====================================================

    if current_player is player2:

        best_score = -99999999

        for action in actions:

            state = save_game_state()

            success = apply_ai_action(
                player2,
                action
            )

            if not success:

                restore_game_state(
                    state
                )

                continue

            # =============================================
            # CPU勝利
            # =============================================

            if (
                player2["row"]
                ==
                player2["goal"]
            ):

                score = (
                    1000000
                    +
                    depth * 1000
                )

            else:

                score = alpha_beta_minimax(
                    depth - 1,
                    player1,
                    alpha,
                    beta
                )

            restore_game_state(
                state
            )

            if score > best_score:

                best_score = score

            if best_score > alpha:

                alpha = best_score

            # =============================================
            # BETA CUT
            # =============================================

            if beta <= alpha:

                break

        return best_score

    # =====================================================
    # PLAYER 1 TURN
    #
    # MIN
    # =====================================================

    best_score = 99999999

    for action in actions:

        state = save_game_state()

        success = apply_ai_action(
            player1,
            action
        )

        if not success:

            restore_game_state(
                state
            )

            continue

        # =================================================
        # PLAYER 1勝利
        # =================================================

        if (
            player1["row"]
            ==
            player1["goal"]
        ):

            score = (
                -1000000
                -
                depth * 1000
            )

        else:

            score = alpha_beta_minimax(
                depth - 1,
                player2,
                alpha,
                beta
            )

        restore_game_state(
            state
        )

        if score < best_score:

            best_score = score

        if best_score < beta:

            beta = best_score

        # =================================================
        # ALPHA CUT
        # =================================================

        if beta <= alpha:

            break

    return best_score


# =========================================================
# LEVEL 3 ROOT MOVE BONUS
#
# LEVEL3の最終的な手選択を補正する
#
# ・ゴールへ近づく
# ・最短経路を短くする
# ・同じ場所への往復を避ける
# =========================================================

def get_level3_root_bonus(
    action
):

    if action is None:

        return 0

    # =====================================================
    # MOVE
    # =====================================================

    if action[0] == "M":

        row = action[1]
        col = action[2]

        bonus = 0

        target_position = (
            row,
            col
        )

        # =================================================
        # 現在の最短距離
        # =================================================

        current_distance = get_shortest_distance(
            player2
        )

        # =================================================
        # 仮移動して移動後の最短距離を調べる
        # =================================================

        state = save_game_state()

        success = apply_ai_action(
            player2,
            action
        )

        if success:

            new_distance = get_shortest_distance(
                player2
            )

        else:

            new_distance = 999

        restore_game_state(
            state
        )

        # =================================================
        # 最短経路が短くなれば大きく評価
        # =================================================

        distance_change = (
            current_distance
            -
            new_distance
        )

        bonus += (
            distance_change
            *
            90
        )

        # =================================================
        # ゴール方向への単純な前進も少し評価
        # =================================================

        current_goal_distance = abs(
            player2["row"]
            -
            player2["goal"]
        )

        new_goal_distance = abs(
            row
            -
            player2["goal"]
        )

        if (
            new_goal_distance
            <
            current_goal_distance
        ):

            bonus += 20

        elif (
            new_goal_distance
            >
            current_goal_distance
        ):

            bonus -= 20

        # =================================================
        # 2マス周期
        # A → B → A
        # =================================================

        if len(
            cpu_position_history
        ) >= 2:

            if (
                target_position
                ==
                cpu_position_history[-2]
            ):

                bonus -= 5000


        # =================================================
        # 3マス周期
        # A → B → C → A
        # =================================================

        if len(
            cpu_position_history
        ) >= 3:

            if (
                target_position
                ==
                cpu_position_history[-3]
            ):

                bonus -= 4000

        # =================================================
        # 最近訪れたマスへの再訪も減点
        # =================================================

        recent_positions = (
            cpu_position_history[-6:]
        )

        visit_count = (
            recent_positions.count(
                target_position
            )
        )

        if visit_count > 0:

            bonus -= (
                visit_count
                *
                140
            )

        # =================================================
        # 3手以内での再訪はさらに減点
        # =================================================

        if (
            target_position
            in
            cpu_position_history[-3:]
        ):

            bonus -= 120

        # =================================================
        # 中央寄りをほんの少し評価
        # =================================================

        bonus += (
            4
            -
            abs(
                col - 4
            )
        ) * 2

        return bonus

    # =====================================================
    # WALL
    # =====================================================

    if action[0] == "W":

        kind = action[1]
        row = action[2]
        col = action[3]

        result = evaluate_wall_for_player(
            player2,
            player1,
            kind,
            row,
            col
        )

        if result is None:

            return -10000

        bonus = 0

        # =================================================
        # 相手を遅らせる
        # =================================================

        bonus += (
            result["target_gain"]
            *
            45
        )

        # =================================================
        # 自分の道を悪化させる
        # =================================================

        bonus -= (
            result["self_loss"]
            *
            40
        )

        # =================================================
        # 相手だけを遅らせる良い壁
        # =================================================

        if (
            result["target_gain"] > 0
            and
            result["self_loss"] == 0
        ):

            bonus += 25

        # =================================================
        # 効果ゼロの壁
        # =================================================

        if (
            result["target_gain"]
            <=
            0
        ):

            bonus -= 35

        # =================================================
        # 壁残数が少ない
        # =================================================

        if player2["walls"] <= 2:

            bonus -= 25

        return bonus

    return 0


# =========================================================
# CPU DISTANCE AFTER MOVE
#
# 指定したマスへ移動した後の
# CPUの最短距離を調べる
# =========================================================

def get_cpu_distance_after_move(
    row,
    col
):

    state = save_game_state()

    action = make_move_action(
        row,
        col
    )

    success = apply_ai_action(
        player2,
        action
    )

    if not success:

        restore_game_state(
            state
        )

        return 999

    distance = get_shortest_distance(
        player2
    )

    restore_game_state(
        state
    )

    return distance


# =========================================================
# CPU CYCLE CHECK
#
# 戻り値
#
# 0 = 周期ではない
# 2 = A → B → A
# 3 = A → B → C → A
# =========================================================

def get_cpu_cycle_length(
    row,
    col
):

    target = (
        row,
        col
    )

    history = cpu_position_history

    # =====================================================
    # 2マス往復
    #
    # A → B → A
    # =====================================================

    if len(history) >= 2:

        if (
            target
            ==
            history[-2]
        ):

            return 2

    # =====================================================
    # 3マス周期
    #
    # A → B → C → A
    # =====================================================

    if len(history) >= 3:

        if (
            target
            ==
            history[-3]
        ):

            return 3

    return 0


# =========================================================
# FILTER LEVEL 3 MOVES
#
# LEVEL3の無意味なループを候補から除外する
#
# ただし、
# ループする手しかない場合には完全禁止しない
# =========================================================

def filter_level3_move_actions(
    move_actions
):

    if not move_actions:

        return []

    current_distance = get_shortest_distance(
        player2
    )

    move_information = []

    # =====================================================
    # 各移動候補を調査
    # =====================================================

    for action in move_actions:

        row = action[1]
        col = action[2]

        target = (
            row,
            col
        )

        # =================================================
        # 即ゴールは絶対に残す
        # =================================================

        if row == player2["goal"]:

            return [
                action
            ]

        new_distance = get_cpu_distance_after_move(
            row,
            col
        )

        cycle_length = get_cpu_cycle_length(
            row,
            col
        )

        recent_count = (
            cpu_position_history[-6:]
            .count(
                target
            )
        )

        move_information.append(
            {
                "action": action,
                "distance": new_distance,
                "cycle": cycle_length,
                "recent_count": recent_count
            }
        )

    # =====================================================
    # 最も良い最短距離
    # =====================================================

    best_distance = min(
        info["distance"]
        for info in move_information
    )

    # =====================================================
    # 周期ではない移動を探す
    # =====================================================

    safe_moves = []

    for info in move_information:

        # =================================================
        # 2周期・3周期は除外
        # =================================================

        if info["cycle"] in (
            2,
            3
        ):

            continue

        # =================================================
        # 最近何度も訪問した場所
        #
        # しかも距離が改善しないなら除外
        # =================================================

        if (
            info["recent_count"] >= 1
            and
            info["distance"]
            >=
            current_distance
        ):

            continue

        # =================================================
        # 最善経路より極端に悪い手も除外
        #
        # +1までの迂回は許す
        # =================================================

        if (
            info["distance"]
            >
            best_distance + 1
        ):

            continue

        safe_moves.append(
            info["action"]
        )

    # =====================================================
    # 安全な候補があるなら、
    # 周期手をLEVEL3の候補から完全除外
    # =====================================================

    if safe_moves:

        return safe_moves

    # =====================================================
    # 全部除外されてしまった場合
    #
    # 行動不能防止のため元の候補を返す
    # =====================================================

    return move_actions


# =========================================================
# LEVEL 3 ROOT ACTIONS
#
# LEVEL3が実際に検討する候補
#
# MOVE
#   ↓
# 周期ループを除去
#
# WALL
#   ↓
# 有力な最大6候補
# =========================================================

def get_level3_root_actions():

    actions = []

    move_actions = []

    # =====================================================
    # MOVE
    # =====================================================

    legal_moves = get_legal_moves(
        player2
    )

    for row, col in legal_moves:

        move_actions.append(
            make_move_action(
                row,
                col
            )
        )

    # =====================================================
    # LEVEL3専用
    #
    # 2マス・3マス周期を除去
    # =====================================================

    move_actions = (
        filter_level3_move_actions(
            move_actions
        )
    )

    actions.extend(
        move_actions
    )

    # =====================================================
    # WALL
    # =====================================================

    if player2["walls"] > 0:

        wall_candidates = (
            get_cpu_promising_walls(
                limit=6
            )
        )

        for (
            candidate_score,
            kind,
            row,
            col
        ) in wall_candidates:

            actions.append(
                make_wall_action(
                    kind,
                    row,
                    col
                )
            )

    return actions


# =========================================================
# LEVEL 3 IMMEDIATE WIN
#
# 1手でゴールできるなら
# Minimaxを行わず即ゴール
# =========================================================

def get_cpu_immediate_win():

    legal_moves = get_legal_moves(
        player2
    )

    for row, col in legal_moves:

        if (
            row
            ==
            player2["goal"]
        ):

            return make_move_action(
                row,
                col
            )

    return None


# =========================================================
# LEVEL 3 EMERGENCY DEFENSE
#
# 相手が次の1手でゴールできる場合、
# 特に壁を重視する
# =========================================================

def player_can_win_next_move():

    legal_moves = get_legal_moves(
        player1
    )

    for row, col in legal_moves:

        if (
            row
            ==
            player1["goal"]
        ):

            return True

    return False


# =========================================================
# LEVEL 3 AI
#
# HARD
#
# CPUの行動
# ↓
# PLAYER1の最善行動
# ↓
# CPUの次の最善行動
# ↓
# 盤面評価
#
# まで読む
# =========================================================

def select_level3_action():

    # =====================================================
    # 即勝ち
    # =====================================================

    winning_action = (
        get_cpu_immediate_win()
    )

    if winning_action is not None:

        return winning_action

    # =====================================================
    # ROOT候補
    # =====================================================

    root_actions = (
        get_level3_root_actions()
    )

    if not root_actions:

        return None

    # =====================================================
    # 良い順に並べる
    # =====================================================

    root_actions = order_ai_actions(
        player2,
        root_actions
    )

    best_action = None

    best_score = -99999999

    alpha = -99999999
    beta = 99999999

    # =====================================================
    # 相手が次で勝てるか
    # =====================================================

    opponent_emergency = (
        player_can_win_next_move()
    )

    # =====================================================
    # ROOT SEARCH
    # =====================================================

    for action in root_actions:

        state = save_game_state()

        # =================================================
        # CPUの候補手
        # =================================================

        success = apply_ai_action(
            player2,
            action
        )

        if not success:

            restore_game_state(
                state
            )

            continue

        # =================================================
        # 即勝利
        # =================================================

        if (
            player2["row"]
            ==
            player2["goal"]
        ):

            restore_game_state(
                state
            )

            return action

        # =================================================
        # MINIMAX
        #
        # depth = 2
        #
        # CPU候補手はすでに実行済みなので、
        #
        # depth2:
        # PLAYER1
        #
        # depth1:
        # CPU
        #
        # depth0:
        # 評価
        #
        # となる
        # =================================================

        score = alpha_beta_minimax(
            depth=2,
            current_player=player1,
            alpha=alpha,
            beta=beta
        )

        # =================================================
        # 元に戻す
        # =================================================

        restore_game_state(
            state
        )

        # =================================================
        # ROOT補助評価
        # =================================================

        score += get_level3_root_bonus(
            action
        )

        # =================================================
        # 相手が次で勝てる危険状態
        #
        # 有効な壁には追加評価
        # =================================================

        if (
            opponent_emergency
            and
            action[0] == "W"
        ):

            kind = action[1]
            row = action[2]
            col = action[3]

            result = evaluate_wall_for_player(
                player2,
                player1,
                kind,
                row,
                col
            )

            if (
                result is not None
                and
                result["target_gain"] > 0
            ):

                score += 400

        # =================================================
        # 最善手更新
        # =================================================

        if score > best_score:

            best_score = score

            best_action = action

        if best_score > alpha:

            alpha = best_score

    return best_action


# =========================================================
# CPU SELECT ACTION
#
# LEVEL 1 / 2 / 3
# をここで一本化
# =========================================================

def select_cpu_action():

    # =====================================================
    # LEVEL 1
    # =====================================================

    if cpu_level == 1:

        return select_level1_action()

    # =====================================================
    # LEVEL 2
    # =====================================================

    if cpu_level == 2:

        return select_level2_action()

    # =====================================================
    # LEVEL 3
    # =====================================================

    return select_level3_action()


# =========================================================
# CPU FALLBACK MOVE
#
# AIが何らかの理由で手を選べなかった場合に、
# 必ず合法な移動を行うための予備処理
# =========================================================

def get_cpu_fallback_move():

    legal_moves = get_legal_moves(
        player2
    )

    if not legal_moves:

        return None

    best_move = None
    best_distance = 999999

    # =====================================================
    # 最短距離になる移動を選ぶ
    # =====================================================

    for row, col in legal_moves:

        old_row = player2["row"]
        old_col = player2["col"]

        player2["row"] = row
        player2["col"] = col

        distance = get_shortest_distance(
            player2
        )

        player2["row"] = old_row
        player2["col"] = old_col

        if distance < best_distance:

            best_distance = distance

            best_move = (
                row,
                col
            )

    # =====================================================
    # 念のため
    # =====================================================

    if best_move is None:

        best_move = random.choice(
            legal_moves
        )

    return make_move_action(
        best_move[0],
        best_move[1]
    )


# =========================================================
# EXECUTE CPU MOVE
#
# CPUの移動を実際の盤面に反映
# =========================================================

def execute_cpu_move(
    row,
    col
):

    global game_over

    # =====================================================
    # 合法手を確認
    # =====================================================

    legal_moves = get_legal_moves(
        player2
    )

    if (
        row,
        col
    ) not in legal_moves:

        return False

    # =====================================================
    # 移動
    # =====================================================

    player2["row"] = row
    player2["col"] = col

    # =====================================================
    # 実際に移動した場所を記録
    # =====================================================

    cpu_position_history.append(
        (
            row,
            col
        )
    )

    # 履歴が増えすぎないようにする
    if (
        len(cpu_position_history)
        >
        CPU_POSITION_HISTORY_LIMIT
    ):

        cpu_position_history.pop(
            0
        )

    # =====================================================
    # 勝利
    # =====================================================

    if check_win(
        player2
    ):

        game_over = True

        return True

    # =====================================================
    # PLAYER1へ
    # =====================================================

    change_turn()

    return True


# =========================================================
# EXECUTE CPU WALL
#
# CPUの壁を実際の盤面に反映
# =========================================================

def execute_cpu_wall(
    kind,
    row,
    col
):

    # =====================================================
    # 壁が残っていない
    # =====================================================

    if player2["walls"] <= 0:

        return False

    # =====================================================
    # 念のため最終確認
    # =====================================================

    if not can_place_wall(
        kind,
        row,
        col
    ):

        return False

    # =====================================================
    # 壁を設置
    # =====================================================

    apply_wall(
        kind,
        row,
        col
    )

    # =====================================================
    # 壁を1枚消費
    # =====================================================

    player2["walls"] -= 1

    # =====================================================
    # PLAYER1へ
    # =====================================================

    change_turn()

    return True


# =========================================================
# EXECUTE CPU ACTION
#
# select_cpu_action() で選ばれた
#
# ("M", row, col)
#
# または
#
# ("W", kind, row, col)
#
# を実行する
# =========================================================

def execute_cpu_action(
    action
):

    if action is None:

        return False

    action_type = action[0]

    # =====================================================
    # MOVE
    # =====================================================

    if action_type == "M":

        if len(action) != 3:

            return False

        row = action[1]
        col = action[2]

        return execute_cpu_move(
            row,
            col
        )

    # =====================================================
    # WALL
    # =====================================================

    if action_type == "W":

        if len(action) != 4:

            return False

        kind = action[1]
        row = action[2]
        col = action[3]

        return execute_cpu_wall(
            kind,
            row,
            col
        )

    return False


# =========================================================
# CPU ACT
#
# CPUの思考結果を取得して
# 実際に1回行動する
# =========================================================

def cpu_act():

    global game_over

    # =====================================================
    # CPU戦ではない
    # =====================================================

    if not cpu_mode:

        return

    # =====================================================
    # ゲーム終了済み
    # =====================================================

    if game_over:

        return

    # =====================================================
    # CPU = PLAYER2
    # =====================================================

    if turn != 2:

        return

    # =====================================================
    # CPUの手を決定
    # =====================================================

    action = select_cpu_action()

    # =====================================================
    # AIが手を返せなかった場合
    # =====================================================

    if action is None:

        action = get_cpu_fallback_move()

    # =====================================================
    # それでも行動不能
    # =====================================================

    if action is None:

        change_turn()

        return

    # =====================================================
    # 実行
    # =====================================================

    success = execute_cpu_action(
        action
    )

    # =====================================================
    # 万一、選択した手を実行できなかった場合
    #
    # 壁候補などの最終確認で失敗した場合も
    # CPUターンが停止しないようにする
    # =====================================================

    if not success:

        fallback = get_cpu_fallback_move()

        if fallback is not None:

            success = execute_cpu_action(
                fallback
            )

    # =====================================================
    # 最後の安全策
    #
    # 行動できなくてもターンを止めない
    # =====================================================

    if (
        not success
        and
        not game_over
        and
        turn == 2
    ):

        change_turn()


# =========================================================
# CPU TURN UPDATE
#
# 毎フレーム呼び出す
#
# time.sleep() は使わない
#
# Pygameの描画を止めずに
# 500msだけCPU THINKING...を表示する
# =========================================================

def update_cpu_turn():

    global cpu_thinking
    global cpu_thinking_start

    # =====================================================
    # CPU戦ではない
    # =====================================================

    if not cpu_mode:

        cpu_thinking = False

        return

    # =====================================================
    # ゲーム終了
    # =====================================================

    if game_over:

        cpu_thinking = False

        return

    # =====================================================
    # ゲーム画面ではない
    # =====================================================

    if scene != "game":

        cpu_thinking = False

        return

    # =====================================================
    # PLAYER1のターン
    # =====================================================

    if turn != 2:

        cpu_thinking = False

        return

    # =====================================================
    # CPUターン開始
    #
    # 最初のフレームでは行動せず、
    # タイマーだけ開始する
    # =====================================================

    if not cpu_thinking:

        cpu_thinking = True

        cpu_thinking_start = (
            pygame.time.get_ticks()
        )

        return

    # =====================================================
    # 経過時間
    # =====================================================

    current_time = (
        pygame.time.get_ticks()
    )

    elapsed_time = (
        current_time
        -
        cpu_thinking_start
    )

    # =====================================================
    # 500ms未満
    # =====================================================

    if (
        elapsed_time
        <
        CPU_THINK_TIME
    ):

        return

    # =====================================================
    # 思考表示終了
    #
    # cpu_act() 内の change_turn() でも
    # Falseになるが、先に解除しておく
    # =====================================================

    cpu_thinking = False

    # =====================================================
    # CPUが1回だけ行動
    # =====================================================

    cpu_act()


# =========================================================
# CPU MOVE COMPATIBILITY
#
# 以前のコードで cpu_move() を呼んでいた箇所が
# 残っていても問題が起きないようにしておく
#
# 実際にはPART8のメインループでは
# update_cpu_turn() を使用する
# =========================================================

def cpu_move():

    if not cpu_mode:

        return

    if game_over:

        return

    if turn != 2:

        return

    # =====================================================
    # 移動だけを行う予備処理
    # =====================================================

    action = get_cpu_fallback_move()

    if action is None:

        change_turn()

        return

    execute_cpu_action(
        action
    )


# =========================================================
# WALL FROM TOUCH
#
# スマホでは細い線を正確に押さなくても
# 一番近い壁位置へ自動スナップする
# =========================================================

def wall_from_touch(
    touch_x,
    touch_y
):

    relative_x = (
        touch_x
        -
        BOARD_X
    )

    relative_y = (
        touch_y
        -
        BOARD_Y
    )

    # =====================================================
    # BOARD OUTSIDE
    # =====================================================

    if (
        relative_x < 0
        or
        relative_y < 0
        or
        relative_x
        >
        BOARD_SIZE * CELL_SIZE
        or
        relative_y
        >
        BOARD_SIZE * CELL_SIZE
    ):

        return None

    # =====================================================
    # 一番近い縦線・横線
    # =====================================================

    vertical_line = round(
        relative_x
        /
        CELL_SIZE
    )

    horizontal_line = round(
        relative_y
        /
        CELL_SIZE
    )

    vertical_distance = abs(
        relative_x
        -
        vertical_line * CELL_SIZE
    )

    horizontal_distance = abs(
        relative_y
        -
        horizontal_line * CELL_SIZE
    )

    # =====================================================
    # 横線に近い
    # → 横壁
    # =====================================================

    if (
        horizontal_distance
        <=
        vertical_distance
    ):

        row = (
            horizontal_line
            -
            1
        )

        # タップ位置が
        # 壁の中央になるようにスナップ
        col = (
            round(
                relative_x
                /
                CELL_SIZE
            )
            -
            1
        )

        row = max(
            0,
            min(
                7,
                row
            )
        )

        col = max(
            0,
            min(
                7,
                col
            )
        )

        return (
            "H",
            row,
            col
        )

    # =====================================================
    # 縦線に近い
    # → 縦壁
    # =====================================================

    else:

        col = (
            vertical_line
            -
            1
        )

        row = (
            round(
                relative_y
                /
                CELL_SIZE
            )
            -
            1
        )

        row = max(
            0,
            min(
                7,
                row
            )
        )

        col = max(
            0,
            min(
                7,
                col
            )
        )

        return (
            "V",
            row,
            col
        )


# =========================================================
# PLACE TOUCH WALL
# =========================================================

def place_touch_wall(
    touch_x,
    touch_y
):

    wall = wall_from_touch(
        touch_x,
        touch_y
    )

    if wall is None:

        return False

    kind, row, col = wall

    # 以前作った
    # place_specific_wall をそのまま利用
    return place_specific_wall(
        kind,
        row,
        col
    )


# =========================================================
# WALL FROM MOUSE
#
# マウス位置から
# 設置しようとしている壁を取得
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
        relative_x
        >
        BOARD_SIZE * CELL_SIZE + 20
        or
        relative_y
        >
        BOARD_SIZE * CELL_SIZE + 20
    ):

        return None

    # =====================================================
    # VERTICAL GRID LINE
    # =====================================================

    vertical_line = round(
        relative_x
        /
        CELL_SIZE
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
        relative_y
        /
        CELL_SIZE
    )

    horizontal_distance = abs(
        relative_y
        -
        horizontal_line * CELL_SIZE
    )

    # =====================================================
    # 壁の近くではない
    # =====================================================

    if (
        vertical_distance > WALL_TOUCH_RANGE
        and
        horizontal_distance > WALL_TOUCH_RANGE
    ):

        return None

    # =====================================================
    # HORIZONTAL WALL
    # =====================================================

    if (
        horizontal_distance
        <=
        vertical_distance
    ):

        wall_row = (
            horizontal_line
            -
            1
        )

        wall_col = int(
            relative_x
            //
            CELL_SIZE
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
        relative_y
        //
        CELL_SIZE
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

    elif kind == "V":

        vertical_walls.add(
            (
                row,
                col
            )
        )


# =========================================================
# CHECK WIN
# =========================================================

def check_win(
    player
):

    return (
        player["row"]
        ==
        player["goal"]
    )


# =========================================================
# CHANGE TURN
# =========================================================

def change_turn():

    global turn
    global mode
    global cpu_thinking
    global cpu_thinking_start
    global wall_dragging
    global wall_preview_candidate

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
    # ターン変更後は移動モード
    # =====================================================

    mode = "move"

    wall_preview_candidate = None

    # =====================================================
    # CPUタイマーをリセット
    # =====================================================

    cpu_thinking = False

    cpu_thinking_start = 0

    wall_dragging = False


# =========================================================
# RESET GAME
# =========================================================

def reset_game():

    global turn
    global game_over
    global mode
    global cpu_thinking
    global cpu_thinking_start

    global wall_dragging
    global wall_drag_x
    global wall_drag_y

    global wall_drag_kind
    global wall_drag_candidate

    global wall_selected_kind
    global wall_preview_candidate

    # =====================================================
    # PLAYER POSITION
    # =====================================================

    wall_selected_kind = "H"

    wall_preview_candidate = None

    if cpu_mode:

        # =================================================
        # CPU MODE
        #
        # CPU = 上側
        # HUMAN = 下側
        # =================================================

        player1["row"] = 8
        player1["col"] = 4
        player1["walls"] = 10
        player1["goal"] = 0

        player2["row"] = 0
        player2["col"] = 4
        player2["walls"] = 10
        player2["goal"] = 8

    else:

        # =================================================
        # PLAYER vs PLAYER
        #
        # 従来通り
        # =================================================

        player1["row"] = 0
        player1["col"] = 4
        player1["walls"] = 10
        player1["goal"] = 8

        player2["row"] = 8
        player2["col"] = 4
        player2["walls"] = 10
        player2["goal"] = 0

    # =====================================================
    # WALLS
    # =====================================================

    horizontal_walls.clear()
    vertical_walls.clear()

    # =====================================================
    # GAME
    # =====================================================

    turn = 1
    game_over = False
    mode = "move"

    # =====================================================
    # CPU
    # =====================================================

    cpu_thinking = False
    cpu_thinking_start = 0

    # =====================================================
    # WALL DRAG
    # =====================================================

    wall_dragging = False

    wall_drag_x = 0
    wall_drag_y = 0

    wall_drag_kind = None

    wall_drag_candidate = None

    # =====================================================
    # CPU HISTORY
    # =====================================================

    cpu_position_history.clear()

    cpu_position_history.append(
        (
            player2["row"],
            player2["col"]
        )
    )



# =========================================================
# HUMAN MOVE
# =========================================================

def move_player(
    row,
    col
):

    global game_over

    # =====================================================
    # GAME OVER
    # =====================================================

    if game_over:

        return False

    # =====================================================
    # MOVE MODEのみ
    # =====================================================

    if mode != "move":

        return False

    # =====================================================
    # CPUターンでは人間操作禁止
    # =====================================================

    if (
        cpu_mode
        and
        turn == 2
    ):

        return False

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

        return False

    # =====================================================
    # 移動
    # =====================================================

    player["row"] = row
    player["col"] = col

    # =====================================================
    # 勝利
    # =====================================================

    if check_win(
        player
    ):

        game_over = True

        return True

    # =====================================================
    # ターン交代
    # =====================================================

    change_turn()

    return True


# =========================================================
# HUMAN PLACE WALL
#
# PC:
# マウス位置を使用
#
# MOBILE:
# タップイベントの座標を直接使用
# =========================================================

def place_wall(
    mouse_x=None,
    mouse_y=None
):

    if game_over:

        return False

    if mode != "wall":

        return False

    # =====================================================
    # CPUターンでは操作禁止
    # =====================================================

    if (
        cpu_mode
        and
        turn == 2
    ):

        return False

    player = get_current_player()

    # =====================================================
    # 壁なし
    # =====================================================

    if player["walls"] <= 0:

        return False

    # =====================================================
    # 座標が指定されていない場合
    # PCのマウス位置を使用
    # =====================================================

    if (
        mouse_x is None
        or
        mouse_y is None
    ):

        mouse_x, mouse_y = (
            pygame.mouse.get_pos()
        )

    # =====================================================
    # 壁位置取得
    # =====================================================

    wall = wall_from_mouse(
        mouse_x,
        mouse_y
    )

    if wall is None:

        return False

    kind, row, col = wall

    # =====================================================
    # 壁設置可能判定
    # =====================================================

    if not can_place_wall(
        kind,
        row,
        col
    ):

        return False

    # =====================================================
    # 設置
    # =====================================================

    apply_wall(
        kind,
        row,
        col
    )

    player["walls"] -= 1

    change_turn()

    return True


# =========================================================
# DRAW BOARD
# =========================================================

def draw_board():

    for row in range(
        BOARD_SIZE
    ):

        for col in range(
            BOARD_SIZE
        ):

            x, y = cell_position(
                row,
                col
            )

            # =================================================
            # GOAL AREA
            # =================================================

            if cpu_mode:

                # HUMAN(P1)のゴール
                if row == 0:

                    color = GOAL_BLUE

                # CPU(P2)のゴール
                elif row == 8:

                    color = GOAL_RED

                else:

                    color = WHITE

            else:

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

    # =====================================================
    # ROW LETTERS
    # =====================================================

    for row in range(
        BOARD_SIZE
    ):

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

    for col in range(
        BOARD_SIZE
    ):

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

    # =====================================================
    # CPUターン中は表示しない
    # =====================================================

    if (
        cpu_mode
        and
        turn == 2
    ):

        return

    player = get_current_player()

    moves = get_legal_moves(
        player
    )

    mouse_x, mouse_y = (
        pygame.mouse.get_pos()
    )

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

        # =================================================
        # HOVER
        # =================================================

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
        (
            100,
            100,
            100
        ),
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

def position_text(
    player
):

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
# BOARD TOUCH AREA
# =========================================================

def is_inside_board_area(
    x,
    y
):

    return (
        BOARD_X - 25
        <=
        x
        <=
        BOARD_X
        +
        BOARD_SIZE * CELL_SIZE
        +
        25

        and

        BOARD_Y - 25
        <=
        y
        <=
        BOARD_Y
        +
        BOARD_SIZE * CELL_SIZE
        +
        25
    )


# =========================================================
# SNAP WALL
#
# 指の位置に最も近い壁位置へ
# 自動的にスナップする
# =========================================================

def get_snapped_wall(
    kind,
    x,
    y
):

    # =====================================================
    # 壁の中心は格子点
    # =====================================================

    col = round(
        (
            x - BOARD_X
        )
        /
        CELL_SIZE
        -
        1
    )

    row = round(
        (
            y - BOARD_Y
        )
        /
        CELL_SIZE
        -
        1
    )

    # =====================================================
    # 0～7に制限
    # =====================================================

    row = max(
        0,
        min(
            7,
            row
        )
    )

    col = max(
        0,
        min(
            7,
            col
        )
    )

    return (
        kind,
        int(row),
        int(col)
    )


# =========================================================
# PLACE SPECIFIC WALL
#
# 指を離した時に
# 「表示されている候補」をそのまま設置する
# =========================================================

def place_specific_wall(
    kind,
    row,
    col
):

    if game_over:

        return False

    if mode != "wall":

        return False

    if (
        cpu_mode
        and
        turn == 2
    ):

        return False

    player = get_current_player()

    if player["walls"] <= 0:

        return False

    # =====================================================
    # 最終合法判定
    # =====================================================

    if not can_place_wall(
        kind,
        row,
        col
    ):

        return False

    # =====================================================
    # 設置
    # =====================================================

    apply_wall(
        kind,
        row,
        col
    )

    player["walls"] -= 1

    change_turn()

    return True


# =========================================================
# START WALL DRAG
# =========================================================

def start_wall_drag(
    x,
    y
):

    global wall_dragging

    global wall_drag_start_x
    global wall_drag_start_y

    global wall_drag_x
    global wall_drag_y

    global wall_drag_kind
    global wall_drag_candidate

    if game_over:

        return False

    if mode != "wall":

        return False

    if (
        cpu_mode
        and
        turn == 2
    ):

        return False

    player = get_current_player()

    if player["walls"] <= 0:

        return False

    if not is_inside_board_area(
        x,
        y
    ):

        return False

    # =====================================================
    # DRAG START
    # =====================================================

    wall_dragging = True

    wall_drag_start_x = x
    wall_drag_start_y = y

    wall_drag_x = x
    wall_drag_y = y

    wall_drag_kind = None

    wall_drag_candidate = None

    return True


# =========================================================
# UPDATE WALL DRAG
#
# 横ドラッグ → H
# 縦ドラッグ → V
# =========================================================

def update_wall_drag(
    x,
    y
):

    global wall_drag_x
    global wall_drag_y

    global wall_drag_kind
    global wall_drag_candidate

    if not wall_dragging:

        return

    wall_drag_x = x
    wall_drag_y = y

    # =====================================================
    # 最初の位置との差
    # =====================================================

    dx = (
        x
        -
        wall_drag_start_x
    )

    dy = (
        y
        -
        wall_drag_start_y
    )

    # =====================================================
    # 少し動かすまでは方向を決定しない
    # =====================================================

    if wall_drag_kind is None:

        if max(
            abs(dx),
            abs(dy)
        ) < 15:

            return

        # =================================================
        # 横へドラッグ
        # =================================================

        if abs(dx) >= abs(dy):

            wall_drag_kind = "H"

        # =================================================
        # 縦へドラッグ
        # =================================================

        else:

            wall_drag_kind = "V"

    # =====================================================
    # 指の現在位置に壁をスナップ
    # =====================================================

    wall_drag_candidate = (
        get_snapped_wall(
            wall_drag_kind,
            x,
            y
        )
    )


# =========================================================
# FINISH WALL DRAG
#
# 表示している候補をそのまま設置
# =========================================================

def finish_wall_drag(
    x,
    y
):

    global wall_dragging
    global wall_drag_kind
    global wall_drag_candidate

    if not wall_dragging:

        return False

    # =====================================================
    # 離した瞬間の位置まで反映
    # =====================================================

    update_wall_drag(
        x,
        y
    )

    candidate = (
        wall_drag_candidate
    )

    # =====================================================
    # 先にドラッグ状態解除
    # =====================================================

    wall_dragging = False

    wall_drag_kind = None

    wall_drag_candidate = None

    # =====================================================
    # 候補なし
    # =====================================================

    if candidate is None:

        return False

    kind, row, col = candidate

    # =====================================================
    # 表示されていた壁をそのまま設置
    # =====================================================

    return place_specific_wall(
        kind,
        row,
        col
    )


# =========================================================
# CANCEL WALL DRAG
# =========================================================

def cancel_wall_drag():

    global wall_dragging
    global wall_drag_kind
    global wall_drag_candidate

    wall_dragging = False

    wall_drag_kind = None

    wall_drag_candidate = None


# =========================================================
# DRAW WALL PREVIEW
# =========================================================

def draw_wall_preview():

    if game_over:

        return

    if mode != "wall":

        return

    if (
        cpu_mode
        and
        turn == 2
    ):

        return

    player = get_current_player()

    if player["walls"] <= 0:

        return

    # =====================================================
    # WEB
    #
    # タップで決めた仮置き壁を表示
    # =====================================================

    if IS_WEB:

        if wall_preview_candidate is None:

            return

        wall = wall_preview_candidate

    # =====================================================
    # PC
    #
    # 従来通りマウス位置をプレビュー
    # =====================================================

    else:

        mouse_x, mouse_y = (
            pygame.mouse.get_pos()
        )

        wall = wall_from_mouse(
            mouse_x,
            mouse_y
        )

        if wall is None:

            return

    kind, row, col = wall

    # =====================================================
    # 合法判定
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

    preview_width = (
        WALL_WIDTH + 7
    )

    # =====================================================
    # HORIZONTAL
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
            preview_width
        )

    # =====================================================
    # VERTICAL
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
            preview_width
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
    # TURN / WINNER
    # =====================================================

    if game_over:

        if (
            player1["row"]
            ==
            player1["goal"]
        ):

            turn_text = (
                "PLAYER 1 WINS!"
            )

            turn_color = BLUE

        elif (
            player2["row"]
            ==
            player2["goal"]
        ):

            if cpu_mode:

                turn_text = (
                    "CPU WINS!"
                )

            else:

                turn_text = (
                    "PLAYER 2 WINS!"
                )

            turn_color = RED

        else:

            turn_text = "GAME OVER"

            turn_color = BLACK

    elif (
        cpu_mode
        and
        turn == 2
    ):

        turn_text = (
            "CPU THINKING..."
        )

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
    # PLAYER 1 INFO
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
    # PLAYER 2 / CPU INFO
    # =====================================================

    if cpu_mode:

        p2_name = "CPU"

    else:

        p2_name = "P2"

    p2_text = (
        f"{p2_name}: "
        f"{position_text(player2)}"
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
            "MOVE MODE"
        )

    else:

        mode_text = (
            "WALL MODE"
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

    mouse_x, mouse_y = (
        pygame.mouse.get_pos()
    )

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
# MOBILE CONTROL RECTS
#
# MOVE / WALL / MENU
# =========================================================

def get_mobile_control_rects():

    move_button = pygame.Rect(
        70,
        MOBILE_BUTTON_Y,
        220,
        MOBILE_BUTTON_HEIGHT
    )

    wall_button = pygame.Rect(
        315,
        MOBILE_BUTTON_Y,
        220,
        MOBILE_BUTTON_HEIGHT
    )

    menu_button = pygame.Rect(
        560,
        MOBILE_BUTTON_Y,
        220,
        MOBILE_BUTTON_HEIGHT
    )

    return (
        move_button,
        wall_button,
        menu_button
    )


# =========================================================
# WALL OPTION RECTS
# =========================================================

def get_wall_option_rects():

    horizontal_button = pygame.Rect(
        70,
        WALL_OPTION_Y,
        220,
        WALL_OPTION_HEIGHT
    )

    vertical_button = pygame.Rect(
        315,
        WALL_OPTION_Y,
        220,
        WALL_OPTION_HEIGHT
    )

    place_button = pygame.Rect(
        560,
        WALL_OPTION_Y,
        220,
        WALL_OPTION_HEIGHT
    )

    return (
        horizontal_button,
        vertical_button,
        place_button
    )


# =========================================================
# SELECT WALL KIND
# =========================================================

def select_wall_kind(
    kind
):

    global wall_selected_kind
    global wall_preview_candidate

    wall_selected_kind = kind

    # 向きを変更したら
    # 前の仮置きは一旦消す
    wall_preview_candidate = None


# =========================================================
# SNAP WALL
#
# タップ位置に最も近い
# 2マス分の壁位置へ吸着
# =========================================================

def get_snapped_wall(
    kind,
    x,
    y
):

    relative_x = (
        x
        -
        BOARD_X
    )

    relative_y = (
        y
        -
        BOARD_Y
    )

    # =====================================================
    # 盤面外
    # =====================================================

    if (
        relative_x < 0
        or
        relative_y < 0
        or
        relative_x > BOARD_SIZE * CELL_SIZE
        or
        relative_y > BOARD_SIZE * CELL_SIZE
    ):

        return None

    # =====================================================
    # 壁の中心位置から
    # row / col を計算
    # =====================================================

    col = round(
        relative_x / CELL_SIZE
        -
        1
    )

    row = round(
        relative_y / CELL_SIZE
        -
        1
    )

    # =====================================================
    # 壁の開始位置は0～7
    # =====================================================

    row = max(
        0,
        min(
            7,
            row
        )
    )

    col = max(
        0,
        min(
            7,
            col
        )
    )

    return (
        kind,
        int(row),
        int(col)
    )


# =========================================================
# SET WALL PREVIEW
#
# 盤面タップでは設置しない
# 仮置きするだけ
# =========================================================

def set_wall_preview(
    x,
    y
):

    global wall_preview_candidate

    if game_over:

        return False

    if mode != "wall":

        return False

    if (
        cpu_mode
        and
        turn == 2
    ):

        return False

    player = get_current_player()

    if player["walls"] <= 0:

        return False

    candidate = get_snapped_wall(
        wall_selected_kind,
        x,
        y
    )

    if candidate is None:

        return False

    wall_preview_candidate = candidate

    return True


# =========================================================
# CONFIRM WALL
#
# PLACEボタンを押した時だけ実際に設置
# =========================================================

def confirm_wall_preview():

    global wall_preview_candidate

    if wall_preview_candidate is None:

        return False

    if game_over:

        return False

    if mode != "wall":

        return False

    if (
        cpu_mode
        and
        turn == 2
    ):

        return False

    player = get_current_player()

    if player["walls"] <= 0:

        return False

    kind, row, col = (
        wall_preview_candidate
    )

    # =====================================================
    # 赤い壁なら設置しない
    # =====================================================

    if not can_place_wall(
        kind,
        row,
        col
    ):

        return False

    # =====================================================
    # 本設置
    # =====================================================

    apply_wall(
        kind,
        row,
        col
    )

    player["walls"] -= 1

    wall_preview_candidate = None

    change_turn()

    return True


# =========================================================
# DRAW WALL OPTION CONTROLS
# =========================================================

def draw_wall_option_controls():


    # =====================================================
    # WEB版だけ表示
    # =====================================================

    if not IS_WEB:
        return

    if mode != "wall":

        return

    if game_over:

        return

    if (
        cpu_mode
        and
        turn == 2
    ):

        return

    (
        horizontal_button,
        vertical_button,
        place_button
    ) = get_wall_option_rects()

    normal_color = (
        235,
        235,
        235
    )

    selected_color = (
        190,
        235,
        190
    )

    # =====================================================
    # HORIZONTAL
    # =====================================================

    if wall_selected_kind == "H":

        h_color = selected_color

    else:

        h_color = normal_color

    pygame.draw.rect(
        screen,
        h_color,
        horizontal_button,
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        BLACK,
        horizontal_button,
        3,
        border_radius=12
    )

    text = small_font.render(
        "HORIZONTAL",
        True,
        BLACK
    )

    screen.blit(
        text,
        (
            horizontal_button.centerx
            -
            text.get_width() // 2,

            horizontal_button.centery
            -
            text.get_height() // 2
        )
    )

    # =====================================================
    # VERTICAL
    # =====================================================

    if wall_selected_kind == "V":

        v_color = selected_color

    else:

        v_color = normal_color

    pygame.draw.rect(
        screen,
        v_color,
        vertical_button,
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        BLACK,
        vertical_button,
        3,
        border_radius=12
    )

    text = small_font.render(
        "VERTICAL",
        True,
        BLACK
    )

    screen.blit(
        text,
        (
            vertical_button.centerx
            -
            text.get_width() // 2,

            vertical_button.centery
            -
            text.get_height() // 2
        )
    )

    # =====================================================
    # PLACE
    # =====================================================

    if wall_preview_candidate is None:

        place_color = (
            180,
            180,
            180
        )

    else:

        kind, row, col = (
            wall_preview_candidate
        )

        if can_place_wall(
            kind,
            row,
            col
        ):

            place_color = (
                170,
                235,
                170
            )

        else:

            place_color = (
                235,
                170,
                170
            )

    pygame.draw.rect(
        screen,
        place_color,
        place_button,
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        BLACK,
        place_button,
        3,
        border_radius=12
    )

    text = font.render(
        "PLACE",
        True,
        BLACK
    )

    screen.blit(
        text,
        (
            place_button.centerx
            -
            text.get_width() // 2,

            place_button.centery
            -
            text.get_height() // 2
        )
    )



# =========================================================
# DRAW MOBILE CONTROLS
# =========================================================

def draw_mobile_controls():

    (
        move_button,
        wall_button,
        menu_button
    ) = get_mobile_control_rects()

    mouse_position = (
        pygame.mouse.get_pos()
    )

    # =====================================================
    # MOVE BUTTON
    # =====================================================

    if mode == "move":

        move_color = MOVE_COLOR

    elif move_button.collidepoint(
        mouse_position
    ):

        move_color = BUTTON_HOVER

    else:

        move_color = BUTTON_COLOR

    pygame.draw.rect(
        screen,
        move_color,
        move_button,
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        BLACK,
        move_button,
        2,
        border_radius=12
    )

    text = option_font.render(
        "MOVE",
        True,
        BLACK
    )

    screen.blit(
        text,
        (
            move_button.centerx
            -
            text.get_width() // 2,

            move_button.centery
            -
            text.get_height() // 2
        )
    )

    # =====================================================
    # WALL BUTTON
    # =====================================================

    if mode == "wall":

        wall_color = PREVIEW_VALID

    elif wall_button.collidepoint(
        mouse_position
    ):

        wall_color = BUTTON_HOVER

    else:

        wall_color = BUTTON_COLOR

    pygame.draw.rect(
        screen,
        wall_color,
        wall_button,
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        BLACK,
        wall_button,
        2,
        border_radius=12
    )

    text = option_font.render(
        "WALL",
        True,
        BLACK
    )

    screen.blit(
        text,
        (
            wall_button.centerx
            -
            text.get_width() // 2,

            wall_button.centery
            -
            text.get_height() // 2
        )
    )

    # =====================================================
    # MENU BUTTON
    # =====================================================

    if menu_button.collidepoint(
        mouse_position
    ):

        menu_color = BUTTON_HOVER

    else:

        menu_color = BUTTON_COLOR

    pygame.draw.rect(
        screen,
        menu_color,
        menu_button,
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        BLACK,
        menu_button,
        2,
        border_radius=12
    )

    text = option_font.render(
        "MENU",
        True,
        BLACK
    )

    screen.blit(
        text,
        (
            menu_button.centerx
            -
            text.get_width() // 2,

            menu_button.centery
            -
            text.get_height() // 2
        )
    )


# =========================================================
# WIN OVERLAY BUTTONS
# =========================================================

def get_win_overlay_buttons():

    play_again_button = pygame.Rect(
        180,
        535,
        220,
        65
    )

    win_menu_button = pygame.Rect(
        450,
        535,
        220,
        65
    )

    return (
        play_again_button,
        win_menu_button
    )


# =========================================================
# DRAW WIN OVERLAY
# =========================================================

def draw_win_overlay():

    if not game_over:

        return

    # =====================================================
    # DARK BACKGROUND
    # =====================================================

    dark = pygame.Surface(
        (
            WINDOW_WIDTH,
            WINDOW_HEIGHT
        ),
        pygame.SRCALPHA
    )

    dark.fill(
        (
            0,
            0,
            0,
            150
        )
    )

    screen.blit(
        dark,
        (
            0,
            0
        )
    )

    # =====================================================
    # PANEL
    # =====================================================

    panel = pygame.Rect(
        100,
        300,
        650,
        320
    )

    pygame.draw.rect(
        screen,
        WHITE,
        panel,
        border_radius=25
    )

    pygame.draw.rect(
        screen,
        BLACK,
        panel,
        4,
        border_radius=25
    )

    # =====================================================
    # WINNER
    # =====================================================

    if (
        player1["row"]
        ==
        player1["goal"]
    ):

        if cpu_mode:

            winner_text = "YOU WIN!"

        else:

            winner_text = "PLAYER 1 WINS!"

        winner_color = BLUE

    else:

        if cpu_mode:

            winner_text = "CPU WINS!"

        else:

            winner_text = "PLAYER 2 WINS!"

        winner_color = RED

    winner_surface = win_font.render(
        winner_text,
        True,
        winner_color
    )

    screen.blit(
        winner_surface,
        (
            WINDOW_WIDTH // 2
            -
            winner_surface.get_width() // 2,

            350
        )
    )

    # =====================================================
    # SUB TEXT
    # =====================================================

    sub_surface = win_sub_font.render(
        "Great game!",
        True,
        BLACK
    )

    screen.blit(
        sub_surface,
        (
            WINDOW_WIDTH // 2
            -
            sub_surface.get_width() // 2,

            450
        )
    )

    # =====================================================
    # BUTTONS
    # =====================================================

    (
        play_again_button,
        win_menu_button
    ) = get_win_overlay_buttons()

    pygame.draw.rect(
        screen,
        MOVE_COLOR,
        play_again_button,
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        BLACK,
        play_again_button,
        2,
        border_radius=12
    )

    text = font.render(
        "PLAY AGAIN",
        True,
        BLACK
    )

    screen.blit(
        text,
        (
            play_again_button.centerx
            -
            text.get_width() // 2,

            play_again_button.centery
            -
            text.get_height() // 2
        )
    )

    pygame.draw.rect(
        screen,
        BUTTON_COLOR,
        win_menu_button,
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        BLACK,
        win_menu_button,
        2,
        border_radius=12
    )

    text = font.render(
        "MENU",
        True,
        BLACK
    )

    screen.blit(
        text,
        (
            win_menu_button.centerx
            -
            text.get_width() // 2,

            win_menu_button.centery
            -
            text.get_height() // 2
        )
    )


# =========================================================
# DRAW GAME SCREEN
# =========================================================

def draw_game_screen():

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

    draw_walls()

    draw_wall_preview()

    draw_information()

    # =====================================================
    # MOBILE BUTTONS
    # =====================================================

    draw_wall_option_controls()

    draw_mobile_controls()

    draw_reset_button()

    # =========================================================
    # WIN OVERLAY
    # =========================================================

    draw_win_overlay()


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

    title = menu_font.render(
        "9x9 WALL GAME",
        True,
        BLACK
    )

    screen.blit(
        title,
        (
            WINDOW_WIDTH // 2
            -
            title.get_width() // 2,
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

    screen.blit(
        subtitle,
        (
            WINDOW_WIDTH // 2
            -
            subtitle.get_width() // 2,
            230
        )
    )

    # =====================================================
    # BUTTONS
    # =====================================================

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

    mouse_position = (
        pygame.mouse.get_pos()
    )

    # =====================================================
    # PVP
    # =====================================================

    if pvp_button.collidepoint(
        mouse_position
    ):

        pvp_color = BUTTON_HOVER

    else:

        pvp_color = BUTTON_COLOR

    pygame.draw.rect(
        screen,
        pvp_color,
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

    pvp_text = option_font.render(
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
    # CPU
    # =====================================================

    if cpu_button.collidepoint(
        mouse_position
    ):

        cpu_color = BUTTON_HOVER

    else:

        cpu_color = BUTTON_COLOR

    pygame.draw.rect(
        screen,
        cpu_color,
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

    cpu_text = option_font.render(
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
        "Move: Click green circle   |   Wall: W   |   Move: M",
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
# CPU LEVEL SELECT SCREEN
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

    screen.blit(
        title,
        (
            WINDOW_WIDTH // 2
            -
            title.get_width() // 2,
            150
        )
    )

    # =====================================================
    # BUTTONS
    # =====================================================

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

    mouse_position = (
        pygame.mouse.get_pos()
    )

    # =====================================================
    # LEVEL 1
    # =====================================================

    if level1_button.collidepoint(
        mouse_position
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

    text = option_font.render(
        "LEVEL 1 - EASY",
        True,
        BLACK
    )

    screen.blit(
        text,
        (
            level1_button.centerx
            -
            text.get_width() // 2,
            level1_button.centery
            -
            text.get_height() // 2
        )
    )

    # =====================================================
    # LEVEL 2
    # =====================================================

    if level2_button.collidepoint(
        mouse_position
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

    text = option_font.render(
        "LEVEL 2 - NORMAL",
        True,
        BLACK
    )

    screen.blit(
        text,
        (
            level2_button.centerx
            -
            text.get_width() // 2,
            level2_button.centery
            -
            text.get_height() // 2
        )
    )

    # =====================================================
    # LEVEL 3
    # =====================================================

    if level3_button.collidepoint(
        mouse_position
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

    text = option_font.render(
        "LEVEL 3 - HARD",
        True,
        BLACK
    )

    screen.blit(
        text,
        (
            level3_button.centerx
            -
            text.get_width() // 2,
            level3_button.centery
            -
            text.get_height() // 2
        )
    )

    # =====================================================
    # BACK
    # =====================================================

    if back_button.collidepoint(
        mouse_position
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

    text = font.render(
        "BACK",
        True,
        BLACK
    )

    screen.blit(
        text,
        (
            back_button.centerx
            -
            text.get_width() // 2,
            back_button.centery
            -
            text.get_height() // 2
        )
    )

    return (
        level1_button,
        level2_button,
        level3_button,
        back_button
    )


# =========================================================
# ASYNC MAIN LOOP
#
# Desktop + Pygbag Web
# 両対応
# =========================================================

async def main():

    global scene
    global cpu_mode
    global cpu_level
    global mode
    global wall_preview_candidate

    running = True

    while running:

        # =================================================
        # EVENTS
        # =================================================

        for event in pygame.event.get():

            # =============================================
            # WINDOW CLOSE
            # =============================================

            if event.type == pygame.QUIT:

                running = False


            # =============================================
            # KEYBOARD
            #
            # PC版では今まで通り使用可能
            # =============================================

            elif event.type == pygame.KEYDOWN:

                # =========================================
                # TITLE
                # =========================================

                if scene == "title":

                    if event.key == pygame.K_ESCAPE:

                        running = False

                    continue


                # =========================================
                # CPU LEVEL SELECT
                # =========================================

                if scene == "cpu_select":

                    if event.key == pygame.K_ESCAPE:

                        scene = "title"

                        cpu_mode = False

                    continue


                # =========================================
                # GAME
                # =========================================

                if scene == "game":

                    # -------------------------------------
                    # MOVE MODE
                    # -------------------------------------

                    if event.key == pygame.K_m:

                        if game_over:

                            continue

                        if (
                            cpu_mode
                            and
                            turn == 2
                        ):

                            continue

                        mode = "move"

                        wall_preview_candidate = Nonev


                    # -------------------------------------
                    # WALL MODE
                    # -------------------------------------

                    elif event.key == pygame.K_w:

                        if game_over:

                            continue

                        if (
                            cpu_mode
                            and
                            turn == 2
                        ):

                            continue

                        current_player = (
                            get_current_player()
                        )

                        if (
                            current_player["walls"]
                            >
                            0
                        ):

                            mode = "wall"

                            wall_preview_candidate = None


                    # -------------------------------------
                    # RESET
                    # -------------------------------------

                    elif event.key == pygame.K_r:

                        reset_game()


                    # -------------------------------------
                    # ESC
                    # -------------------------------------

                    elif event.key == pygame.K_ESCAPE:

                        scene = "title"

                        cpu_mode = False

                        reset_game()


            # =============================================
            # MOUSE / TOUCH
            #
            # pygame-ceではスマホのタップも
            # MOUSEBUTTONDOWNとして扱える
            # =============================================

            elif event.type == pygame.MOUSEBUTTONDOWN:

                if event.button != 1:

                    continue

                mouse_x = event.pos[0]
                mouse_y = event.pos[1]


                # =========================================
                # TITLE SCREEN
                # =========================================

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

                    # -------------------------------------
                    # PLAYER vs PLAYER
                    # -------------------------------------

                    if pvp_button.collidepoint(
                        mouse_x,
                        mouse_y
                    ):

                        cpu_mode = False

                        scene = "game"

                        reset_game()


                    # -------------------------------------
                    # PLAYER vs CPU
                    # -------------------------------------

                    elif cpu_button.collidepoint(
                        mouse_x,
                        mouse_y
                    ):

                        cpu_mode = True

                        scene = "cpu_select"

                    continue


                # =========================================
                # CPU LEVEL SELECT
                # =========================================

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

                    # -------------------------------------
                    # LEVEL 1
                    # -------------------------------------

                    if level1_button.collidepoint(
                        mouse_x,
                        mouse_y
                    ):

                        cpu_level = 1

                        cpu_mode = True

                        scene = "game"

                        reset_game()


                    # -------------------------------------
                    # LEVEL 2
                    # -------------------------------------

                    elif level2_button.collidepoint(
                        mouse_x,
                        mouse_y
                    ):

                        cpu_level = 2

                        cpu_mode = True

                        scene = "game"

                        reset_game()


                    # -------------------------------------
                    # LEVEL 3
                    # -------------------------------------

                    elif level3_button.collidepoint(
                        mouse_x,
                        mouse_y
                    ):

                        cpu_level = 3

                        cpu_mode = True

                        scene = "game"

                        reset_game()


                    # -------------------------------------
                    # BACK
                    # -------------------------------------

                    elif back_button.collidepoint(
                        mouse_x,
                        mouse_y
                    ):

                        cpu_mode = False

                        scene = "title"

                    continue
                
                



                # =========================================
                # GAME SCREEN
                # =========================================

                if scene == "game":

                    # =====================================
                    # MOBILE BUTTONS
                    # =====================================

                    (
                        move_button,
                        wall_button,
                        menu_button
                    ) = get_mobile_control_rects()


                    (
                        horizontal_button,
                        vertical_button,
                        place_button
                    ) = get_wall_option_rects()


                    # =====================================
                    # WEB WALL OPTION BUTTONS
                    # =====================================

                    if (
                        IS_WEB
                        and
                        mode == "wall"
                    ):

                        # =================================
                        # HORIZONTAL
                        # =================================

                        if horizontal_button.collidepoint(
                            mouse_x,
                            mouse_y
                        ):

                            select_wall_kind(
                                "H"
                            )

                            continue

                        # =================================
                        # VERTICAL
                        # =================================

                        if vertical_button.collidepoint(
                            mouse_x,
                            mouse_y
                        ):

                            select_wall_kind(
                                "V"
                            )

                            continue

                        # =================================
                        # PLACE
                        # =================================

                        if place_button.collidepoint(
                            mouse_x,
                            mouse_y
                        ):

                            confirm_wall_preview()

                            continue


                    # -------------------------------------
                    # MOVE BUTTON
                    # -------------------------------------

                    if move_button.collidepoint(
                        mouse_x,
                        mouse_y
                    ):

                        if game_over:

                            continue

                        if (
                            cpu_mode
                            and
                            turn == 2
                        ):

                            continue

                        mode = "move"

                        continue


                    # -------------------------------------
                    # WALL BUTTON
                    # -------------------------------------

                    if wall_button.collidepoint(
                        mouse_x,
                        mouse_y
                    ):

                        if game_over:

                            continue

                        if (
                            cpu_mode
                            and
                            turn == 2
                        ):

                            continue

                        current_player = (
                            get_current_player()
                        )

                        if (
                            current_player["walls"]
                            >
                            0
                        ):

                            mode = "wall"

                        continue


                    # -------------------------------------
                    # MENU BUTTON
                    # -------------------------------------

                    if menu_button.collidepoint(
                        mouse_x,
                        mouse_y
                    ):

                        scene = "title"

                        cpu_mode = False

                        reset_game()

                        continue


                    # =====================================
                    # RESET BUTTON
                    # =====================================

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


                    # =====================================
                    # GAME OVER
                    # =====================================

                    if game_over:

                        (
                            play_again_button,
                            win_menu_button
                        ) = get_win_overlay_buttons()

                        # =====================================
                        # PLAY AGAIN
                        # =====================================

                        if play_again_button.collidepoint(
                            mouse_x,
                            mouse_y
                        ):

                            reset_game()

                        # =====================================
                        # MENU
                        # =====================================

                        elif win_menu_button.collidepoint(
                            mouse_x,
                            mouse_y
                        ):

                            scene = "title"

                            cpu_mode = False

                            reset_game()

                        continue


                    # =====================================
                    # CPU TURN
                    # =====================================

                    if (
                        cpu_mode
                        and
                        turn == 2
                    ):

                        continue


                    # =====================================
                    # WALL MODE
                    # =====================================

                    if mode == "wall":

                        # =================================
                        # WEB / SMARTPHONE
                        #
                        # ここでは設置しない。
                        # 仮置き位置だけ決める。
                        # =================================

                        if IS_WEB:

                            set_wall_preview(
                                mouse_x,
                                mouse_y
                            )

                        # =================================
                        # PC
                        #
                        # 従来通り即設置
                        # =================================

                        else:

                            place_wall(
                                mouse_x,
                                mouse_y
                            )

                        continue


                    # =====================================
                    # MOVE MODE
                    # =====================================

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




        # =================================================
        # CPU
        # =================================================

        if (
            scene == "game"
            and
            cpu_mode
            and
            turn == 2
            and
            not game_over
        ):

            update_cpu_turn()


        # =================================================
        # DRAW
        # =================================================

        if scene == "title":

            draw_title_screen()


        elif scene == "cpu_select":

            draw_cpu_level_screen()


        elif scene == "game":

            draw_game_screen()


        # =================================================
        # DISPLAY
        # =================================================

        pygame.display.flip()

        clock.tick(
            FPS
        )

        # =================================================
        # PYGBAG / WEB
        #
        # 必ず毎フレームブラウザへ処理を返す
        # =================================================

        await asyncio.sleep(0)


    pygame.quit()


# =========================================================
# START
# =========================================================

asyncio.run(
    main()
)