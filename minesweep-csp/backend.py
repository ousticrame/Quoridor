from typing import List, Tuple, Optional
import random
from solver import MinesweeperSolver


class MinesweeperBackend:
    def __init__(self, width: int, height: int, num_mines: int):
        """
        Initialize a new Minesweeper game backend.

        Args:
            width (int): Width of the game board
            height (int): Height of the game board
            num_mines (int): Number of mines to place
        """
        self.width = width
        self.height = height
        self.num_mines = num_mines
        self.grid = [[0 for _ in range(width)] for _ in range(height)]
        self.revealed = [[False for _ in range(width)] for _ in range(height)]
        self.flagged = [[False for _ in range(width)] for _ in range(height)]
        self.game_over = False
        self.won = False
        self._place_mines()
        self._calculate_numbers()
        self.solver = MinesweeperSolver(self)

    def _place_mines(self):
        """Place mines randomly on the board."""
        positions = [(x, y) for x in range(self.width) for y in range(self.height)]
        mine_positions = random.sample(positions, self.num_mines)
        for x, y in mine_positions:
            self.grid[y][x] = -1  # -1 represents a mine

    def _calculate_numbers(self):
        """Calculate the numbers for each cell based on adjacent mines."""
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == -1:
                    continue
                count = 0
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        nx, ny = x + dx, y + dy
                        if (dx == 0 and dy == 0) or not (
                            0 <= nx < self.width and 0 <= ny < self.height
                        ):
                            continue
                        if self.grid[ny][nx] == -1:
                            count += 1
                self.grid[y][x] = count

    def reveal(self, x: int, y: int) -> bool:
        """
        Reveal a cell at the given coordinates.

        Args:
            x (int): X coordinate
            y (int): Y coordinate

        Returns:
            bool: True if the game is still ongoing, False if game over
        """
        if not (0 <= x < self.width and 0 <= y < self.height):
            return True
        if self.flagged[y][x] or self.revealed[y][x]:
            return True

        self.revealed[y][x] = True

        if self.grid[y][x] == -1:
            self.game_over = True
            return False

        if self.grid[y][x] == 0:
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if (dx == 0 and dy == 0) or not (
                        0 <= nx < self.width and 0 <= ny < self.height
                    ):
                        continue
                    self.reveal(nx, ny)

        if self._check_win():
            self.won = True
            self.game_over = True

        return not self.game_over

    def toggle_flag(self, x: int, y: int):
        """
        Toggle the flag state of a cell.

        Args:
            x (int): X coordinate
            y (int): Y coordinate
        """
        if not (0 <= x < self.width and 0 <= y < self.height):
            return
        if not self.revealed[y][x]:
            self.flagged[y][x] = not self.flagged[y][x]

    def _check_win(self) -> bool:
        """Check if the game has been won."""
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] != -1 and not self.revealed[y][x]:
                    return False
                if self.grid[y][x] == -1 and not self.flagged[y][x]:
                    return False
        return True

    def get_game_state(self) -> dict:
        """
        Get the current state of the game.

        Returns:
            dict: Dictionary containing the game state
        """
        return {
            "grid": self.grid,
            "revealed": self.revealed,
            "flagged": self.flagged,
            "game_over": self.game_over,
            "won": self.won,
            "width": self.width,
            "height": self.height,
            "num_mines": self.num_mines,
        }

    def solve_next_move(self) -> Optional[Tuple[int, int]]:
        """
        Get the next move from the solver.

        Returns:
            Optional[Tuple[int, int]]: The next move coordinates or None if no move is available
        """
        if self.game_over:
            return None

        if self.solver.solve_step():
            if self.solver.safe_moves:
                return self.solver.safe_moves[0]
            if self.solver.flagged_cells:
                return self.solver.flagged_cells[0]
        return None

    def apply_solver_move(self) -> bool:
        """
        Apply the next move from the solver.

        Returns:
            bool: True if a move was applied, False otherwise
        """
        return self.solver.apply_moves()

    def reset_game(self):
        """Reset the game to its initial state."""
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.revealed = [[False for _ in range(self.width)] for _ in range(self.height)]
        self.flagged = [[False for _ in range(self.width)] for _ in range(self.height)]
        self.game_over = False
        self.won = False
        self._place_mines()
        self._calculate_numbers()
        self.solver = MinesweeperSolver(self)
