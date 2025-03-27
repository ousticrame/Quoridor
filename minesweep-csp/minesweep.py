import pygame
import random
import sys
from solver import (
    MinesweeperSolver,
)

from Astarsolver import AstarSolver

pygame.init()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (192, 192, 192)
DARK_GRAY = (128, 128, 128)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
COLORS = [BLUE, GREEN, RED, (0, 0, 128), (128, 0, 0), (0, 128, 128), BLACK, GRAY]

# Game settings
CELL_SIZE = 30
GRID_WIDTH = 9
GRID_HEIGHT = 9
NUM_MINES = 10

# Calculate window size
BUTTON_HEIGHT = 40
WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE
WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE + BUTTON_HEIGHT
WINDOW_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)

# Create window
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Minesweeper")

# Fonts
font = pygame.font.SysFont("Arial", 20)
small_font = pygame.font.SysFont("Arial", 16)


class Minesweeper:
    def __init__(self, width, height, num_mines):
        self.width = width
        self.height = height
        self.num_mines = num_mines
        self.grid = []
        self.revealed = []
        self.flagged = []
        self.game_over = False
        self.win = False
        self.initialize_grid()
        self.place_mines()
        self.calculate_numbers()

    def initialize_grid(self):
        """Initialize the grid with empty cells."""
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.revealed = [[False for _ in range(self.width)] for _ in range(self.height)]
        self.flagged = [[False for _ in range(self.width)] for _ in range(self.height)]

    def place_mines(self):
        """Randomly place mines on the grid."""
        mines_placed = 0
        while mines_placed < self.num_mines:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if self.grid[y][x] != -1:
                self.grid[y][x] = -1
                mines_placed += 1

    def calculate_numbers(self):
        """Calculate the number of adjacent mines for each cell."""
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == -1:
                    continue

                count = 0
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.width and 0 <= ny < self.height:
                            if self.grid[ny][nx] == -1:
                                count += 1
                self.grid[y][x] = count

    def reveal(self, x, y):
        """Reveal a cell. If it's a mine, game over. If it's a 0, reveal adjacent cells."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return

        if self.revealed[y][x] or self.flagged[y][x]:
            return

        self.revealed[y][x] = True

        if self.grid[y][x] == -1:
            self.game_over = True
            return

        if self.grid[y][x] == 0:
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        self.reveal(nx, ny)

        self.check_win()

    def toggle_flag(self, x, y):
        """Toggle flag on a cell."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return

        if self.revealed[y][x]:
            return

        self.flagged[y][x] = not self.flagged[y][x]

    def check_win(self):
        """Check if the player has won."""
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] != -1 and not self.revealed[y][x]:
                    return
        self.win = True

    def reset(self):
        """Reset the game."""
        self.initialize_grid()
        self.place_mines()
        self.calculate_numbers()
        self.game_over = False
        self.win = False


class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)

        text_surface = small_font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, mouse_pos, mouse_pressed):
        return self.rect.collidepoint(mouse_pos) and mouse_pressed[0]


def draw_grid(game, safe_moves=None, flagged_cells=None):
    """Draw the game grid on the screen."""
    if safe_moves is None:
        safe_moves = []
    if flagged_cells is None:
        flagged_cells = []
    for y in range(game.height):
        for x in range(game.width):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)

            if game.revealed[y][x]:
                pygame.draw.rect(screen, WHITE, rect)
            elif (x, y) in safe_moves:
                pygame.draw.rect(screen, GREEN, rect)
            elif (x, y) in flagged_cells:
                pygame.draw.rect(screen, YELLOW, rect)
            else:
                pygame.draw.rect(screen, GRAY, rect)

            pygame.draw.rect(screen, DARK_GRAY, rect, 1)

            if game.revealed[y][x]:
                if game.grid[y][x] == -1:
                    pygame.draw.circle(screen, BLACK, rect.center, CELL_SIZE // 3)
                elif game.grid[y][x] > 0:
                    number = font.render(
                        str(game.grid[y][x]), True, COLORS[game.grid[y][x] - 1]
                    )
                    number_rect = number.get_rect(center=rect.center)
                    screen.blit(number, number_rect)
            elif game.flagged[y][x]:
                pygame.draw.polygon(
                    screen,
                    RED,
                    [
                        (
                            x * CELL_SIZE + CELL_SIZE // 2,
                            y * CELL_SIZE + CELL_SIZE // 4,
                        ),
                        (
                            x * CELL_SIZE + CELL_SIZE // 4,
                            y * CELL_SIZE + CELL_SIZE // 3,
                        ),
                        (
                            x * CELL_SIZE + CELL_SIZE // 2,
                            y * CELL_SIZE + CELL_SIZE // 2,
                        ),
                    ],
                )
                pygame.draw.line(
                    screen,
                    BLACK,
                    (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 4),
                    (
                        x * CELL_SIZE + CELL_SIZE // 2,
                        y * CELL_SIZE + 3 * CELL_SIZE // 4,
                    ),
                    2,
                )


def draw_game_over(game):
    """Draw game over screen."""
    for y in range(game.height):
        for x in range(game.width):
            if game.grid[y][x] == -1:
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, WHITE, rect)
                pygame.draw.rect(screen, DARK_GRAY, rect, 1)
                pygame.draw.circle(screen, BLACK, rect.center, CELL_SIZE // 3)

    message = font.render("Game Over!", True, RED)
    message_rect = message.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
    screen.blit(message, message_rect)


def draw_win(game):
    """Draw win screen."""
    message = font.render("You Win!", True, GREEN)
    message_rect = message.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
    screen.blit(message, message_rect)


def main():
    game = Minesweeper(GRID_WIDTH, GRID_HEIGHT, NUM_MINES)
    # solver = MinesweeperSolver(game)
    solver = AstarSolver(game.grid, game.width, game.height, game.num_mines, game.revealed, game.flagged)
    running = True

    # Create a "Solve" button at the bottom of the window
    # Create solver button
    solver_button = Button(
        WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT - 35, 100, 30, "Solve", GRAY, DARK_GRAY
    )

    # Variables to store moves suggested by the solver for highlighting
    safe_moves = []
    flagged_cells = []

    while running:
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()

        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()

        solver_button.update(mouse_pos)

        solver = AstarSolver(game.grid, game.width, game.height, game.num_mines, game.revealed, game.flagged)
        if solver_button.is_clicked(mouse_pos, mouse_pressed):
            print("Solving...")
            solver.solve()
            # display the current state of the game
            draw_grid(game, safe_moves, flagged_cells)
            pygame.display.flip()
            print(solver.nb_explosions)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Only allow user moves if the game is not over or won
            if not game.game_over and not game.win:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    # Check if click is inside the grid area
                    if y < GRID_HEIGHT * CELL_SIZE:
                        grid_x, grid_y = x // CELL_SIZE, y // CELL_SIZE
                        if event.button == 1:  # Left click to reveal
                            game.reveal(grid_x, grid_y)
                        elif event.button == 3:  # Right click to flag
                            game.toggle_flag(grid_x, grid_y)

        # Draw the game grid with solver suggestions highlighted
        screen.fill(WHITE)
        draw_grid(game, safe_moves, flagged_cells)

        if game.game_over:
            draw_game_over(game)
        elif game.win:
            draw_win(game)

        solver_button.draw(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
