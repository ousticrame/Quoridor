use anyhow::Context as _;
use picross_solver::{
    board::{FullSolution, Puzzle},
    solve::solve,
};
use std::fs::{self};

fn main() -> anyhow::Result<()> {
    let content = fs::read_to_string("./smiley.pc").context("Could not open file")?;
    let puzzle: Puzzle = content.parse().context("Could not parse input")?;

    match solve(&puzzle) {
        None => println!("Could not find a solution!"),
        Some(solved) => println!(
            "{}",
            FullSolution {
                board: solved,
                puzzle
            }
        ),
    }
    Ok(())
}
