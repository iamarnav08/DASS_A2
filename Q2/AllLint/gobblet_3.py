"""
Gobblet Jr with Pygame
Read the README File for more details.
"""

import sys
import pygame

pygame.init()

WINDOW_SIZE = 1200
CELL_SIZE = 200
GRID_SIZE = 3
GRID_OFFSET = 300       # (WINDOW_SIZE - (GRID_SIZE * CELL_SIZE)) / / 2

PINK = (227, 166, 216)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

# Setting up the display

screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE), pygame.RESIZABLE)
pygame.display.set_caption("Gobblet Jr Game")

class Pieces: # Taking pieces to be circles of diff sizes
    """
    This class is for the game pieces(circles) of possible sizes as big, medium and small.
    Attributes are-
    x: X coordinate position
    x: Y-coordinate position
    size: 1=small, 2=medium, 3=big
    radius: size*20
    color: RGB value
    player: 1 or 2 (Player ID)
    selected: boolean variable, true if currently selected
    """
    def __init__(self, x, y, size, color, player):
        """
        Basic initiation function for a piece
        """
        self.x = x
        self.y = y
        self.size = size
        self.radius = size * 20
        self.color = color
        self.player = player
        self.selected = False

    def draw_circle(self):
        """
        Function to draw the circle for given input
        """
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        if self.selected:
            pygame.draw.circle(screen, YELLOW, (self.x, self.y), self.radius+2, 2)

    def contains_point(self, x, y):
        """
        Function to check whether a given set of coordinates is inside a circle or not
        """
        return ((x - self.x) ** 2 + (y - self.y) ** 2) <= self.radius ** 2

class Board:
    """
    This class is for the 'board' of the game, the canvas.
    A board has the following attributes-
    cells: the grid/matrix to place the pieces in
    current_player: To see which player is to move right now
    winner: To see is the game has been won yet, and if yes, by whom.
    """
    def __init__(self):
        """
        Basic initiation function for a board
        """
        self.cells = [[[] for _ in range(3)] for _ in range(3)]
        self.current_player = 1
        self.winner = None

    def get_grid_sq(self, x, y):
        """
        This function returns the grid coordinates
        from the board coordinates.
        """
        if x < GRID_OFFSET or y < GRID_OFFSET:
            return None
        col = int((x - GRID_OFFSET) / CELL_SIZE)
        row = int((y - GRID_OFFSET) / CELL_SIZE)
        if row >= GRID_SIZE or col >= GRID_SIZE:
            return None
        return row, col

    def check_availability(self, row, col, piece):
        """
        Checks whether a piece can be placed in a grid sqaure
        """
        if not self.cells[row][col]:
            return True
        piece_already_there = self.cells[row][col][-1]
        return piece.size > piece_already_there.size

    def get_grid_sq_center(self, row, col):
        """
        Returns the centre coordinates of a grid sqaure,
        to place a piece symmetrically and aesthetically.
        """
        center_x = GRID_OFFSET + col * CELL_SIZE + CELL_SIZE // 2
        center_y = GRID_OFFSET + row* CELL_SIZE + CELL_SIZE // 2
        return center_x, center_y

    def check_winner(self):
        """
        Function to check whetehr the game has been won yet.
        """
        # Checking in rows
        for row in range(3):
            if self.cells[row][0] and self.cells[row][1] and self.cells[row][2]:
                if (self.cells[row][0][-1].player == self.cells[row][1][-1].player==
                    self.cells[row][2][-1].player):
                    return self.cells[row][0][-1].player

        # Checking in columns
        for col in range(3):
            if self.cells[0][col] and self.cells[1][col] and self.cells[2][col]:
                if (self.cells[0][col][-1].player == self.cells[1][col][-1].player==
                    self.cells[2][col][-1].player):
                    return self.cells[0][col][-1].player

        # Checking diagonals
        if (self.cells[0][0] and self.cells[1][1] and self.cells[2][2] and
            self.cells[0][0][-1].player == self.cells[1][1][-1].player==
            self.cells[2][2][-1].player):
            return self.cells[0][0][-1].player

        if (self.cells[0][2] and self.cells[1][1] and self.cells[2][0] and
            self.cells[0][2][-1].player == self.cells[1][1][-1].player==
            self.cells[2][0][-1].player):
            return self.cells[0][2][-1].player

        return None


def main():
    """
    Main functino for the code.
    """
    board = Board()
    selected_piece = None
    pieces  = []
    font = pygame.font.SysFont('Calibri', 36, bold=True)

    # Making the circular pieces
    pieces.append(Pieces(150, 200, 3, RED, 1))
    pieces.append(Pieces(150, 350, 3, RED, 1))  # Second large piece

    pieces.append(Pieces(WINDOW_SIZE-150, 200, 3, BLUE, 2))
    pieces.append(Pieces(WINDOW_SIZE-150, 350, 3, BLUE, 2))  # Second large piece

    # Medium size (2)
    pieces.append(Pieces(150, 500, 2, RED, 1))
    pieces.append(Pieces(150, 650, 2, RED, 1))  # Second medium piece

    pieces.append(Pieces(WINDOW_SIZE-150, 500, 2, BLUE, 2))
    pieces.append(Pieces(WINDOW_SIZE-150, 650, 2, BLUE, 2))  # Second medium piece

    # Small size (1)
    pieces.append(Pieces(150, 750, 1, RED, 1))
    pieces.append(Pieces(150, 850, 1, RED, 1))  # Second small piece

    pieces.append(Pieces(WINDOW_SIZE-150, 750, 1, BLUE, 2))
    pieces.append(Pieces(WINDOW_SIZE-150, 850, 1, BLUE, 2))  # Second small piece

    while True:
        screen.fill(PINK)

        # Making the grid
        for i in range(4):
            start_x = GRID_OFFSET + i*CELL_SIZE
            start_y = GRID_OFFSET + i*CELL_SIZE
            pygame.draw.line(screen, BLACK, (start_x, GRID_OFFSET), 
                             (start_x, WINDOW_SIZE - GRID_OFFSET), 4)
            pygame.draw.line(screen, BLACK, (GRID_OFFSET, start_y), 
                             (WINDOW_SIZE-GRID_OFFSET, start_y), 4)


        p1_text = font.render("Player 1", True, RED)
        p2_text = font.render("Player 2", True, BLUE)
        screen.blit(p1_text, (100, 50))
        screen.blit(p2_text, (WINDOW_SIZE-200, 50))

        current_player_text  = font.render(f"Current Player: {board.current_player}", 
                                           True, RED if board.current_player==1 else BLUE)
        screen.blit(current_player_text, (WINDOW_SIZE//2-100, 50))

        for row in range(3):
            for col in range(3):
                if board.cells[row][col]:
                    for piece in board.cells[row][col]:
                        piece.draw_circle()

        for piece in pieces:
            piece.draw_circle()

        # Checking for winner
        if board.winner:
            overlay = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE))
            overlay.set_alpha(128)
            overlay.fill((255, 255, 255))
            screen.blit(overlay, (0,0))

            winner_color = RED if board.winner==1 else BLUE
            winner_text = font.render(f"Player {board.winner} wins!", True, winner_color)
            text_rect = winner_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2))
            pygame.draw.rect(screen, (255, 255, 255),
                        (text_rect.x - 10, text_rect.y - 10,
                        text_rect.width + 20, text_rect.height + 20))
            pygame.draw.rect(screen, winner_color,
                        (text_rect.x - 10, text_rect.y - 10,
                        text_rect.width + 20, text_rect.height + 20), 3)

            screen.blit(winner_text, text_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN and not board.winner:
                x, y = pygame.mouse.get_pos()

                if selected_piece:
                    cell = board.get_grid_sq(x,y)
                    if cell and board.check_availability(cell[0], cell[1], selected_piece):
                        if selected_piece in [p for row in board.cells for col in row for p in col]:
                            old_pos = [(i,j) for i in range(GRID_SIZE) for j in range(GRID_SIZE)
                                    if selected_piece in board.cells[i][j]][0]
                            board.cells[old_pos[0]][old_pos[1]].remove(selected_piece)
                        elif selected_piece in pieces:
                            pieces.remove(selected_piece)

                        center_x, center_y = board.get_grid_sq_center(cell[0], cell[1])
                        selected_piece.x, selected_piece.y = center_x, center_y
                        board.cells[cell[0]][cell[1]].append(selected_piece)
                        selected_piece.selected = False
                        selected_piece = None

                        # Check for winner and switch turns
                        board.winner = board.check_winner()
                        if not board.winner:
                            board.current_player = 3 - board.current_player

                else:
                    cell = board.get_grid_sq(x, y)
                    if cell and board.cells[cell[0]][cell[1]]:
                        piece = board.cells[cell[0]][cell[1]][-1]
                        if piece.player == board.current_player:
                            selected_piece = piece
                            piece.selected = True
                    else:
                        for piece in pieces:
                            if piece.contains_point(x, y) and piece.player == board.current_player:
                                selected_piece = piece
                                piece.selected = True
                                break

            pygame.display.flip()


if __name__ == "__main__":
    """
    Running the code.
    """
    main()
