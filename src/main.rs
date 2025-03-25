use anyhow::Context as _;
use picross_solver::{board::Puzzle, solve::solve};
use std::fs::{self};

fn main() -> anyhow::Result<()> {
    let content = fs::read_to_string("./test.pc").context("Could not open file")?;
    let puzzle: Puzzle = content.parse().context("Could not parse input")?;

    match solve(&puzzle) {
        None => println!("Could not find a solution!"),
        Some(solved) => println!("{}", solved),
    }
    Ok(())
}
