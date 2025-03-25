use crate::board::{Board, Cell, Puzzle};

pub fn is_valid_col(puzzle: &Puzzle, solution: &Board, col: usize) -> bool {
    // FIXME: this could be much faster by splitting this method
    let sub_puzzle = Puzzle::from(solution);
    sub_puzzle.cols[col].len() <= puzzle.cols[col].len()
        && sub_puzzle.cols[col]
            .iter()
            .zip(puzzle.cols[col].iter())
            .all(|(sub_group, group)| sub_group <= group)
}

pub fn is_valid_row(puzzle: &Puzzle, solution: &Board, row: usize) -> bool {
    // FIXME: this could be much faster by splitting this method
    let sub_puzzle = Puzzle::from(solution);
    sub_puzzle.rows[row].len() <= puzzle.rows[row].len()
        && sub_puzzle.rows[row]
            .iter()
            .zip(puzzle.rows[row].iter())
            .all(|(sub_group, group)| sub_group <= group)
}

pub fn is_valid(puzzle: &Puzzle, solution: &Board) -> bool {
    todo!()
}

/// Dumb solver
fn solve_backtracking(puzzle: &Puzzle, i: usize, mut board: Board) -> Option<Board> {
    if i >= puzzle.size() * puzzle.size() {
        return Some(board);
    }
    let x = i / puzzle.size();
    let y = i % puzzle.size();

    for state in [Cell::Filled, Cell::Empty] {
        board.table[x][y] = state;
        if !(is_valid_col(puzzle, &board, y) && is_valid_row(puzzle, &board, x)) {
            continue;
        }
        if let Some(solved) = solve_backtracking(puzzle, i + 1, board.clone()) {
            return Some(solved);
        }
    }
    None
}

pub fn solve(puzzle: &Puzzle) -> Option<Board> {
    let board = Board {
        table: vec![vec![Cell::Empty; puzzle.size()]; puzzle.size()],
    };
    solve_backtracking(puzzle, 0, board)
}

#[cfg(test)]
mod tests {
    use rstest::rstest;

    #[rstest]
    #[case(
        true,
        r"
5   | 5 3 | 3 1 1 2 | 2 1 1 2 | 5 1 1 | 1 1 1 | 3 1 1 | 1 1 | 5 1 1 | 5 1 2 | 3 1 1 2 | 2 1 3 | 5
5 5 | 5 5 | 3 1 3 1 | 2 1 2 1 | 5 1 5 | 1     | 2     | 3 3 | 1 5 1 | 2 2   | 2 2     | 7     |
",
        r"
#####...#####
#####...#####
###.#...###.#
##..#...##..#
#####.#.#####
......#......
.....##......
.###.....###.
.#..#####..#.
.##.......##.
..##.....##..
...#######...
.............
"
    )]
    #[case(
        false,
        r"
5   | 5 3 | 3 1 1 2 | 2 1 1 2 | 5 1 1 | 1 1 1 | 3 1 1 | 1 1 | 5 1 1 | 5 1 2 | 3 1 1 2 | 2 1 3 | 5
5 5 | 5 5 | 3 1 3 1 | 2 1 2 1 | 5 1 5 | 1     | 2     | 3 3 | 1 5 1 | 2 2   | 2 2     | 7     |
",
        r"
#####...#####
#####...#####
###.#...###.#
###.#...##..#
#####.#.#####
#....##......
.#...##......
.####.#..###.
.#.######.###
.##....#####.
..##.....##..
...#######...
...........#.
"
    )]
    fn test_is_valid_col(
        #[case] valid: bool,
        #[case] puzzle: &str,
        #[case] board_str: &str,
    ) -> anyhow::Result<()> {
        use crate::{
            board::{Board, Puzzle},
            solve::is_valid_col,
        };

        let puzzle: Puzzle = puzzle.parse()?;
        let board: Board = board_str.parse()?;

        for i in 0..board.size() {
            assert_eq!(is_valid_col(&puzzle, &board, i), valid, "At index {i}");
        }
        Ok(())
    }

    #[rstest]
    #[case(
        true,
        r"
5   | 5 3 | 3 1 1 2 | 2 1 1 2 | 5 1 1 | 1 1 1 | 3 1 1 | 1 1 | 5 1 1 | 5 1 2 | 3 1 1 2 | 2 1 3 | 5
5 5 | 5 5 | 3 1 3 1 | 2 1 2 1 | 5 1 5 | 1     | 2     | 3 3 | 1 5 1 | 2 2   | 2 2     | 7     |
",
        r"
#####...#####
#####...#####
###.#...###.#
##..#...##..#
#####.#.#####
......#......
.....##......
.###.....###.
.#..#####..#.
.##.......##.
..##.....##..
...#######...
.............
"
    )]
    fn test_is_valid_row(
        #[case] valid: bool,
        #[case] puzzle: &str,
        #[case] board_str: &str,
    ) -> anyhow::Result<()> {
        use crate::{
            board::{Board, Puzzle},
            solve::is_valid_row,
        };

        let puzzle: Puzzle = puzzle.parse()?;
        let board: Board = board_str.parse()?;

        for i in 0..board.size() {
            assert_eq!(is_valid_row(&puzzle, &board, i), valid, "At index {i}");
        }
        Ok(())
    }
}
