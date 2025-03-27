import random

class AstarSolver:
    def __init__(self, grid, width, height, total_mines, revealed_cells, flagged_cells):
        self.grid = grid
        self.width = width
        self.height = height
        self.total_mines = total_mines
        self.moves = []
        
        self.revealed_cells = revealed_cells
        self.flagged_cells = flagged_cells
        self.nb_explosions = 0

    # One step of the A* algorithm
    def solve(self):
        while self.apply_logic():
            self.apply_moves()
            while self.moves != []:
                self.apply_moves()
        
        if self.is_solved():
            return True 
        
        else:
            self.random_solve()
            while self.moves != []:
                self.apply_moves()
            return False
    
    def is_solved(self):
        return self.get_count_revealed() + self.get_count_flagged() == self.width * self.height
    
    def get_count_revealed(self):
        count = 0
        for x in range(self.width):
            for y in range(self.height):
                if self.revealed_cells[x][y]:
                    count += 1
        return count
    
    def get_count_flagged(self):
        count = 0
        for x in range(self.width):
            for y in range(self.height):
                if self.flagged_cells[x][y]:
                    count += 1
        return count
    
    def apply_logic(self):
        self.moves = []
        revealed = self.get_revealed()
        for cell in revealed:
            x, y = cell[0]
            number = cell[1]
            unrevealed_neighbors = self.get_unrevealed_neighbors(x, y)
            flagged_neighbors = self.get_flagged_neighbors(x, y)

            # If number of flags equals the cell's number, all other neighbors are safe
            if len(flagged_neighbors) == number and unrevealed_neighbors:
                for nx, ny in unrevealed_neighbors:
                    if not self.flagged_cells[nx][ny] and (nx, ny) not in self.moves:
                        self.moves.append((nx, ny))
            
            # If number of flags plus number of unrevealed neighbors equals the cell's number, all unrevealed neighbors are mines
            if len(flagged_neighbors) + len(unrevealed_neighbors) == number and unrevealed_neighbors:
                for nx, ny in unrevealed_neighbors:
                    if not self.flagged_cells[nx][ny] and (nx, ny):
                        self.flagged_cells[nx][ny] = True
        
        return self.moves != []

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
                if x + i >= 0 and x + i < self.width and y + j >= 0 and y + j < self.height and not self.revealed_cells[x + i][y + j] and not self.flagged_cells[x + i][y + j]:
                    unrevealed_neighbors.append((x + i, y + j))
        return unrevealed_neighbors

    def get_revealed(self):
        revealed = []
        for x in range(self.width):
            for y in range(self.height):
                if self.revealed_cells[x][y]:
                    revealed.append(((x, y), self.grid[x][y]))
        return revealed


    def apply_moves(self):
        new_moves = []
        for x, y in self.moves:
            if not (0 <= x < self.width and 0 <= y < self.height):
                continue

            if self.revealed_cells[x][y] or self.flagged_cells[x][y]:
                continue

            self.revealed_cells[x][y] = True

            if self.grid[x][y] == -1:
                self.nb_explosions += 1
                self.revealed_cells[x][y] = False
                self.flagged_cells[x][y] = True
                continue

            if self.grid[x][y] == 0:
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.width and 0 <= ny < self.height:
                            new_moves.append((nx, ny))
        self.moves = []
        self.moves = new_moves


    def random_solve(self):
        x, y = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
        while self.revealed_cells[x][y] or self.flagged_cells[x][y]:
            x, y = random.randint(0, self.width - 1), random.randint(0, self.height - 1) 
        self.moves.append((x, y))
        self.apply_moves()

    