import random

class AstarSolver:
    def __init__(self, grid, width, height, total_mines, revealed_cells, flagged_cells):
        self.grid = grid
        self.width = width
        self.height = height
        self.total_mines = total_mines
        self.safe_moves = []
        self.flagged_mines = []
        
        self.revealed_cells = revealed_cells
        self.flagged_cells = flagged_cells

    def solve(self):
        while self.apply_logic():
            self.apply_safe_moves()
        
        if self.is_solved():
            return True 
        
        else:
            self.greedy_solve()
            return False
    
    def is_solved(self):
        return len(self.revealed_cells) + len(self.flagged_cells) == self.width * self.height
    
    def apply_logic(self):
        self.safe_moves = []
        revealed = self.get_revealed()
        for cell in revealed:
            x, y = cell[0]
            number = cell[1]
            unrevealed_neighbors = self.get_unrevealed_neighbors(x, y)
            flagged_neighbors = self.get_flagged_neighbors(x, y)

            # If number of flags equals the cell's number, all other neighbors are safe
            if len(flagged_neighbors) == number and unrevealed_neighbors:
                for nx, ny in unrevealed_neighbors:
                    if (nx, ny) not in self.flagged_mines and (nx, ny) not in self.safe_moves:
                        self.safe_moves.append((nx, ny))
            
            # If number of flags plus number of unrevealed neighbors equals the cell's number, all unrevealed neighbors are mines
            if len(flagged_neighbors) + len(unrevealed_neighbors) == number and unrevealed_neighbors:
                for nx, ny in unrevealed_neighbors:
                    if (nx, ny) not in self.flagged_mines:
                        self.flagged_mines.append((nx, ny))
        
        return self.safe_moves != []

    def get_flagged_neighbors(self, x, y):
        flagged_neighbors = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if x + i >= 0 and x + i < self.width and y + j >= 0 and y + j < self.height and self.flagged_cells[x + i][y + j]:
                    flagged_neighbors.append((x + i, y + j))
        return flagged_neighbors

    def get_unrevealed_neighbors(self, x, y):
        unrevealed_neighbors = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if x + i >= 0 and x + i < self.width and y + j >= 0 and y + j < self.height and not self.revealed_cells[x + i][y + j]:
                    unrevealed_neighbors.append((x + i, y + j))
        return unrevealed_neighbors

    def get_revealed(self):
        revealed = []
        for x in range(self.width):
            for y in range(self.height):
                if self.revealed_cells[x][y]:
                    revealed.append(((x, y), self.grid[x][y]))
        return revealed


    def apply_safe_moves(self):
        for x, y in self.safe_moves:
            if not (0 <= x < self.width and 0 <= y < self.height):
                continue

            if self.revealed_cells[x][y] or self.flagged_cells[x][y]:
                continue

            self.revealed_cells[x][y] = True

            if self.grid[x][y] == 0:
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.width and 0 <= ny < self.height:
                            self.apply_safe_moves(nx, ny)


    # When we can't apply the logic, we will use a greedy approach
    # We will choose a random cell that has not been revealed yet
    # If the cell is a mine, we will flag it
    # If the cell is safe, we will reveal it



    # When we can't apply the logic, we will use a greedy approach
    # We will simulate the game by testing each cell
    # We select the cell that reveals the most information
    def greedy_solve(self):
        best_move = None
        best_score = -1

        for x in range(self.width):
            for y in range(self.height):
                if not self.revealed_cells[x][y]:
                    score = self.evaluate_cell(x, y)
                    if score > best_score:
                        best_score = score
                        best_move = (x, y)

        if best_move:
            x, y = best_move
            if self.grid[x][y] == -1:
                self.flagged_cells[x][y] = True
            else:
                self.revealed_cells[x][y] = True
                if self.grid[x][y] == 0:
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < self.width and 0 <= ny < self.height:
                                self.apply_safe_moves(nx, ny)