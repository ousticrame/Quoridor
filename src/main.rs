use anyhow::bail;
use anyhow::Context as _;
use std::fs::{self};

/// Puzzle input
#[derive(Debug)]
struct PicrossPuzzle {
    rows: Vec<Vec<u32>>,
    cols: Vec<Vec<u32>>,
}

impl PicrossPuzzle {
    fn size(&self) -> usize {
        assert_eq!(self.rows.len(), self.cols.len());
        self.cols.len()
    }
}

/// Puzzle output
#[derive(Debug, Clone)]
struct PicrossSolved {
    table: Vec<Vec<bool>>,
}

const DELIM: &str = "|";

impl TryFrom<&str> for PicrossPuzzle {
    type Error = anyhow::Error;

    fn try_from(value: &str) -> Result<Self, Self::Error> {
        fn parse_picross_grid_line(var_name: &&str) -> anyhow::Result<Vec<Vec<u32>>> {
            Ok(var_name
                .split(DELIM)
                .map(|line| {
                    line.split_whitespace()
                        .map(|num| dbg!(num).parse::<u32>())
                        .collect::<Result<Vec<_>, _>>()
                })
                .collect::<Result<Vec<_>, _>>()?)
        }

        let lines: Vec<_> = value.lines().collect();
        if lines.len() != 2 {
            bail!("Input file should be 2 lines long");
        }

        Ok(Self {
            rows: parse_picross_grid_line(&lines[0])?,
            cols: parse_picross_grid_line(&lines[1])?,
        })
    }
}

fn is_valid_col(puzzle: &PicrossPuzzle, solution: &PicrossSolved, col: usize) -> bool {
    let mut counter = 0;
    let mut groups_found = 0;
    for cell in &solution.table[col] {
        if *cell {
            counter += 1;
        } else if counter != 0 {
            if puzzle.rows[col].get(groups_found) != Some(&counter) {
                return false;
            }
            counter = 0;
            groups_found += 1;
        }
    }
    true
}

fn is_valid_row(puzzle: &PicrossPuzzle, solution: &PicrossSolved, row: usize) -> bool {
    todo!()
}

fn is_valid(puzzle: &PicrossPuzzle, solution: &PicrossSolved) -> bool {
    todo!()
}

/// Dumb solver
fn solve_backtracking(
    puzzle: &PicrossPuzzle,
    x: usize,
    y: usize,
    mut solved: PicrossSolved,
) -> Option<PicrossSolved> {
    if y >= puzzle.size() {
        return Some(solved);
    }
    if x >= puzzle.size() {
        dbg!(x, y);
        return solve_backtracking(puzzle, 0, y + 1, solved);
    }

    for state in [true, false] {
        solved.table[x][y] = state;
        if !is_valid_col(puzzle, &solved, y) {
            continue;
        }
        if let Some(solved) = solve_backtracking(puzzle, x + 1, y, solved.clone()) {
            return Some(solved);
        }
    }
    return None;
}

fn solve(puzzle: &PicrossPuzzle) -> Option<PicrossSolved> {
    let wip = PicrossSolved {
        table: vec![vec![false; puzzle.size()]; puzzle.size()],
    };
    return solve_backtracking(puzzle, 0, 0, wip);
}

fn main() -> anyhow::Result<()> {
    let content = fs::read_to_string("./test.pc").context("Could not open file")?;
    let puzzle = PicrossPuzzle::try_from(&content[..]).context("Could not parse input")?;

    let solved = solve(&puzzle);

    println!("{:?}", solved);
    Ok(())
}
