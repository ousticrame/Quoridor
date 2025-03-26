import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (192, 192, 192)
DARK_GRAY = (128, 128, 128)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
COLORS = [BLUE, GREEN, RED, (0, 0, 128), (128, 0, 0), (0, 128, 128), BLACK, GRAY]

# Game settings
CELL_SIZE = 30
GRID_WIDTH = 9
GRID_HEIGHT = 9
NUM_MINES = 10

# Calculate window size
WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE
WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE
WINDOW_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)

# Create window
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Minesweeper")

# Font
font = pygame.font.SysFont("Arial", 20)


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
        # 0 represents empty cell, -1 will represent a mine
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        # False represents an unrevealed cell
        self.revealed = [[False for _ in range(self.width)] for _ in range(self.height)]
        # False represents an unflagged cell
        self.flagged = [[False for _ in range(self.width)] for _ in range(self.height)]

    def place_mines(self):
        """Randomly place mines on the grid."""
        mines_placed = 0
        while mines_placed < self.num_mines:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if self.grid[y][x] != -1:  # Check if cell doesn't already have a mine
                self.grid[y][x] = -1  # Place a mine
                mines_placed += 1

    def calculate_numbers(self):
        """Calculate the number of adjacent mines for each cell."""
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == -1:  # Skip mine cells
                    continue

                # Count adjacent mines
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
            return  # Out of bounds

        if self.revealed[y][x] or self.flagged[y][x]:
            return  # Already revealed or flagged

        self.revealed[y][x] = True

        if self.grid[y][x] == -1:
            self.game_over = True
            return

        # If it's a 0, reveal adjacent cells
        if self.grid[y][x] == 0:
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        self.reveal(nx, ny)

        # Check if player has won
        self.check_win()

    def toggle_flag(self, x, y):
        """Toggle flag on a cell."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return  # Out of bounds

        if self.revealed[y][x]:
            return  # Cannot flag revealed cells

        self.flagged[y][x] = not self.flagged[y][x]

    def check_win(self):
        """Check if the player has won."""
        for y in range(self.height):
            for x in range(self.width):
                # If a non-mine cell is not revealed, player hasn't won yet
                if self.grid[y][x] != -1 and not self.revealed[y][x]:
                    return

        self.win = True


def draw_grid(game):
    """Draw the game grid on the screen."""
    for y in range(game.height):
        for x in range(game.width):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)

            # Draw cell background
            if game.revealed[y][x]:
                pygame.draw.rect(screen, WHITE, rect)
            else:
                pygame.draw.rect(screen, GRAY, rect)

            # Draw cell border
            pygame.draw.rect(screen, DARK_GRAY, rect, 1)

            # Draw cell content
            if game.revealed[y][x]:
                if game.grid[y][x] == -1:
                    # Draw mine
                    pygame.draw.circle(screen, BLACK, rect.center, CELL_SIZE // 3)
                elif game.grid[y][x] > 0:
                    # Draw number
                    number = font.render(
                        str(game.grid[y][x]), True, COLORS[game.grid[y][x] - 1]
                    )
                    number_rect = number.get_rect(center=rect.center)
                    screen.blit(number, number_rect)
            elif game.flagged[y][x]:
                # Draw flag
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
                # Reveal all mines
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, WHITE, rect)
                pygame.draw.rect(screen, DARK_GRAY, rect, 1)
                pygame.draw.circle(screen, BLACK, rect.center, CELL_SIZE // 3)

    # Display game over message
    message = font.render("Game Over!", True, RED)
    message_rect = message.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
    screen.blit(message, message_rect)


def draw_win(game):
    """Draw win screen."""
    # Display win message
    message = font.render("You Win!", True, GREEN)
    message_rect = message.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
    screen.blit(message, message_rect)


def main():
    game = Minesweeper(GRID_WIDTH, GRID_HEIGHT, NUM_MINES)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if not game.game_over and not game.win:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    grid_x, grid_y = x // CELL_SIZE, y // CELL_SIZE

                    if event.button == 1:  # Left click (reveal)
                        game.reveal(grid_x, grid_y)
                    elif event.button == 3:  # Right click (flag)
                        game.toggle_flag(grid_x, grid_y)

        # Draw the game
        screen.fill(WHITE)
        draw_grid(game)

        if game.game_over:
            draw_game_over(game)
        elif game.win:
            draw_win(game)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
