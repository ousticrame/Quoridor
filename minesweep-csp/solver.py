import random
import traceback
from z3.z3 import Solver, Bool, Sum, If, sat, is_true, is_false, Int, And


class MinesweeperSolver:
    def __init__(self, game):
        """
        Initialize the CSP solver for Minesweeper

        :param game: Minesweeper game instance
        """
        try:
            self.game = game
            self.width = game.width
            self.height = game.height
            self.remaining_mines = game.num_mines
            self.safe_moves = []  # List of (x, y) coordinates that are safe to reveal
            self.flagged_cells = []  # List of (x, y) coordinates that should be flagged

            # Z3 solver setup
            self.solver = Solver()
            self.mine_vars = (
                {}
            )  # Dictionary to store Z3 boolean variables for mine locations

            # Create Z3 boolean variables for each cell
            for y in range(self.height):
                for x in range(self.width):
                    # Create a boolean variable for each cell indicating if it's a mine
                    self.mine_vars[(x, y)] = Bool(f"mine_{x}_{y}")

            # Total mine constraint
            mine_count = Sum(
                [
                    If(self.mine_vars[(x, y)], Int(1), Int(0))
                    for x in range(self.width)
                    for y in range(self.height)
                ]
            )
            self.solver.add(mine_count == self.remaining_mines)
        except Exception as e:
            print(f"Error in MinesweeperSolver initialization: {e}")
            print(traceback.format_exc())
            raise

    def solve_step(self):
        """Perform one step of the solving process."""
        try:
            # Update remaining mine count based on current flags
            self.update_mine_count()

            # First, try to find trivial moves (guaranteed safe or mine cells)
            self.find_trivial_moves()

            # If trivial moves found, return True
            if self.safe_moves or self.flagged_cells:
                return True

            # If no trivial moves, use CSP to find probabilistic moves
            return self.make_csp_guess()
        except Exception as e:
            print(f"Error in solve_step: {e}")
            print(traceback.format_exc())
            return False

    def update_mine_count(self):
        """Update the remaining mine count based on current flags."""
        try:
            flag_count = sum(
                sum(1 for cell in row if cell) for row in self.game.flagged
            )
            self.remaining_mines = max(0, self.game.num_mines - flag_count)

            # Safely update Z3 total mine constraint
            try:
                self.solver.push()  # Create a new constraint scope
                mine_count = Sum(
                    [
                        If(self.mine_vars[(x, y)], Int(1), Int(0))
                        for x in range(self.width)
                        for y in range(self.height)
                    ]
                )
                self.solver.add(mine_count == self.remaining_mines)
            except Exception as z3_err:
                print(f"Z3 constraint update error: {z3_err}")
                self.solver.pop()  # Ensure solver state is maintained
        except Exception as e:
            print(f"Error in update_mine_count: {e}")
            print(traceback.format_exc())

    def get_unrevealed_neighbors(self, x, y):
        """Get unrevealed neighboring cells."""
        neighbors = []
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if (dx == 0 and dy == 0) or not (
                    0 <= nx < self.width and 0 <= ny < self.height
                ):
                    continue
                if not self.game.revealed[ny][nx]:
                    neighbors.append((nx, ny))
        return neighbors

    def get_flagged_neighbors_count(self, x, y):
        """Count flagged neighboring cells."""
        count = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if (dx == 0 and dy == 0) or not (
                    0 <= nx < self.width and 0 <= ny < self.height
                ):
                    continue
                if self.game.flagged[ny][nx]:
                    count += 1
        return count

    def find_trivial_moves(self):
        """Find trivial safe moves and flagged cells."""
        try:
            self.safe_moves = []
            self.flagged_cells = []

            # Add constraints for revealed cells
            self.add_revealed_cell_constraints()

            # Check if solver finds a solution with these constraints
            solve_result = self.solver.check()
            if solve_result == sat:
                model = self.solver.model()

                # Check for definitely safe and definitely mine cells
                for y in range(self.height):
                    for x in range(self.width):
                        # Only consider unrevealed cells
                        if not self.game.revealed[y][x] and not self.game.flagged[y][x]:
                            # Evaluate Z3 variable for this cell
                            try:
                                var_value = model.evaluate(self.mine_vars[(x, y)])

                                if is_false(var_value):
                                    # Cell is definitely safe
                                    self.safe_moves.append((x, y))
                                elif is_true(var_value):
                                    # Cell is definitely a mine
                                    self.flagged_cells.append((x, y))
                            except Exception as eval_err:
                                print(f"Error evaluating cell {x},{y}: {eval_err}")

            # If no definite moves from CSP, fall back to classic Minesweeper logic
            if not self.safe_moves and not self.flagged_cells:
                self._fallback_trivial_moves()
        except Exception as e:
            print(f"Error in find_trivial_moves: {e}")
            print(traceback.format_exc())
            # Fallback to classic logic if CSP solver fails
            self._fallback_trivial_moves()

    def _fallback_trivial_moves(self):
        """Fallback method for finding trivial moves using classic Minesweeper logic."""
        for y in range(self.height):
            for x in range(self.width):
                if not self.game.revealed[y][x] or self.game.grid[y][x] <= 0:
                    continue

                unrevealed = self.get_unrevealed_neighbors(x, y)
                flagged_count = self.get_flagged_neighbors_count(x, y)

                if len(unrevealed) + flagged_count == self.game.grid[y][x]:
                    for nx, ny in unrevealed:
                        if not self.game.flagged[ny][nx]:
                            self.flagged_cells.append((nx, ny))

                if flagged_count == self.game.grid[y][x]:
                    for nx, ny in unrevealed:
                        if (
                            not self.game.flagged[ny][nx]
                            and (nx, ny) not in self.safe_moves
                        ):
                            self.safe_moves.append((nx, ny))

    def add_revealed_cell_constraints(self):
        """
        Add constraints for revealed cells based on their mine count
        """
        try:
            # Clear previous constraints
            self.solver.pop()
            self.solver.push()

            # Add total mine constraint again
            mine_count = Sum(
                [
                    If(self.mine_vars[(x, y)], Int(1), Int(0))
                    for x in range(self.width)
                    for y in range(self.height)
                ]
            )
            self.solver.add(mine_count == self.remaining_mines)

            # Process revealed cells
            for y in range(self.height):
                for x in range(self.width):
                    # Only process revealed cells with a number
                    if self.game.revealed[y][x] and self.game.grid[y][x] > 0:
                        # Get neighboring cells
                        neighbors = self.get_unrevealed_neighbors(x, y)

                        # Constraint: number of mines in neighbors must match the cell's number
                        mine_count = self.game.grid[y][x]

                        # Constraint for number of mines in neighbors
                        neighbor_mine_vars = [
                            self.mine_vars[nx, ny] for nx, ny in neighbors
                        ]

                        # Add constraint that exactly mine_count neighbors are mines
                        if neighbor_mine_vars:
                            self.solver.add(
                                Sum([If(var, 1, 0) for var in neighbor_mine_vars])
                                == mine_count
                            )
        except Exception as e:
            print(f"Error in add_revealed_cell_constraints: {e}")
            print(traceback.format_exc())

    def make_csp_guess(self):
        """
        Make a probabilistic guess when no definite moves are found
        """
        try:
            # Try to find a cell with the most revealed neighbors
            candidates = []
            for y in range(self.height):
                for x in range(self.width):
                    if not self.game.revealed[y][x] and not self.game.flagged[y][x]:
                        candidates.append((x, y))

            if candidates:
                best_candidate = None
                most_revealed_neighbors = -1

                for x, y in candidates:
                    revealed_neighbors = 0
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            nx, ny = x + dx, y + dy
                            if (dx == 0 and dy == 0) or not (
                                0 <= nx < self.width and 0 <= ny < self.height
                            ):
                                continue
                            if self.game.revealed[ny][nx]:
                                revealed_neighbors += 1

                    if revealed_neighbors > most_revealed_neighbors:
                        most_revealed_neighbors = revealed_neighbors
                        best_candidate = (x, y)

                if best_candidate and most_revealed_neighbors > 0:
                    self.safe_moves.append(best_candidate)
                else:
                    self.safe_moves.append(random.choice(candidates))
                return True

            return False
        except Exception as e:
            print(f"Error in make_csp_guess: {e}")
            print(traceback.format_exc())

            # Fallback to random move if everything else fails
            if candidates:
                self.safe_moves.append(random.choice(candidates))
            return False

    def apply_moves(self):
        """Apply the moves found by the solver to the game."""
        try:
            # Apply flag moves first
            for x, y in self.flagged_cells:
                if not self.game.flagged[y][x]:
                    self.game.toggle_flag(x, y)

            # Then reveal one safe cell (if any)
            if self.safe_moves:
                x, y = self.safe_moves[0]
                self.game.reveal(x, y)
                return True

            return False
        except Exception as e:
            print(f"Error in apply_moves: {e}")
            print(traceback.format_exc())
            return False
