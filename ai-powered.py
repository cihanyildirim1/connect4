import numpy as np
import random
import pygame
import sys
import math

# Define colors
BLUE   = (0, 0, 255)
BLACK  = (0, 0, 0)
RED    = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE  = (255, 255, 255)

# Board dimensions and players
ROW_COUNT    = 6
COLUMN_COUNT = 7

PLAYER = 0
AI     = 1

# Pieces
EMPTY       = 0
PLAYER_PIECE = 1
AI_PIECE     = 2

WINDOW_LENGTH = 4

def create_board():
    return np.zeros((ROW_COUNT, COLUMN_COUNT))

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid_location(board, col):
    return board[ROW_COUNT - 1][col] == 0

def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r

def winning_move(board, piece):
    # Check horizontal locations
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if all(board[r][c + i] == piece for i in range(WINDOW_LENGTH)):
                return True
    # Check vertical locations
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if all(board[r + i][c] == piece for i in range(WINDOW_LENGTH)):
                return True
    # Check positively sloped diagonals
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if all(board[r + i][c + i] == piece for i in range(WINDOW_LENGTH)):
                return True
    # Check negatively sloped diagonals
    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if all(board[r - i][c + i] == piece for i in range(WINDOW_LENGTH)):
                return True
    return False

def get_valid_locations(board):
    return [col for col in range(COLUMN_COUNT) if is_valid_location(board, col)]

def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or not valid_locations
    if depth == 0 or is_terminal:
        if winning_move(board, AI_PIECE):
            return (None, 100000000000000)
        elif winning_move(board, PLAYER_PIECE):
            return (None, -10000000000000)
        else:
            return (None, 0)
    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value
    else:
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value

def draw_board(board, turn):
    screen.fill(BLACK)
    # Draw header and turn indicator
    header_text = font.render("Connect 4", True, WHITE)
    screen.blit(header_text, (width // 3, 20))
    turn_text = font.render("Your Turn" if turn == PLAYER else "", True, RED if turn == PLAYER else YELLOW)
    screen.blit(turn_text, (width // 3, 80))
    # Draw board grid
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c * SQUARESIZE, r * SQUARESIZE + board_offset, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, 
                               (int(c * SQUARESIZE + SQUARESIZE / 2),
                                int(r * SQUARESIZE + board_offset + SQUARESIZE / 2)), RADIUS)
    # Draw pieces
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == PLAYER_PIECE:
                pygame.draw.circle(screen, RED,
                                   (int(c * SQUARESIZE + SQUARESIZE / 2),
                                    height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
            elif board[r][c] == AI_PIECE:
                pygame.draw.circle(screen, YELLOW,
                                   (int(c * SQUARESIZE + SQUARESIZE / 2),
                                    height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
    pygame.display.update()

# Initialize game
pygame.init()

SQUARESIZE   = 100
board_offset = 150  # Space for header and turn indicator
width  = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT * SQUARESIZE) + board_offset
size   = (width, height)
RADIUS = int(SQUARESIZE / 2 - 5)

screen = pygame.display.set_mode(size)
pygame.display.set_caption("Connect 4")
font = pygame.font.SysFont("monospace", 50)

board = create_board()
game_over = False
winner = None
turn = random.randint(PLAYER, AI)

draw_board(board, turn)

while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        # Handle player's motion and click
        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(screen, BLACK, (0, 0, width, board_offset))
            posx = event.pos[0]
            if turn == PLAYER:
                pygame.draw.circle(screen, RED, (posx, board_offset // 2), RADIUS)
            pygame.display.update()
        if event.type == pygame.MOUSEBUTTONDOWN and turn == PLAYER:
            posx = event.pos[0]
            col = int(math.floor(posx / SQUARESIZE))
            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, PLAYER_PIECE)
                if winning_move(board, PLAYER_PIECE):
                    winner = "Player"
                    game_over = True
                turn = AI
                draw_board(board, turn)
    # Handle AI move
    if turn == AI and not game_over:
        col, _ = minimax(board, 5, -math.inf, math.inf, True)
        if col is None:
            col = random.choice(get_valid_locations(board))
        if is_valid_location(board, col):
            row = get_next_open_row(board, col)
            drop_piece(board, row, col, AI_PIECE)
            if winning_move(board, AI_PIECE):
                winner = "AI"
                game_over = True
            turn = PLAYER
            draw_board(board, turn)
    # Check for draw
    if not get_valid_locations(board) and not game_over:
        winner = "No one. It's a draw!"
        game_over = True

# After game over, display winner
pygame.draw.rect(screen, BLACK, (0, 0, width, board_offset))
if winner is not None:
    end_text = font.render(f"{winner} Wins!", True, RED if winner == "Player" else YELLOW)
    screen.blit(end_text, (width // 4, board_offset // 2))
    print(f"     🏆 {winner} Wins!")
pygame.display.update()
pygame.time.wait(5000)
pygame.quit()
sys.exit()
