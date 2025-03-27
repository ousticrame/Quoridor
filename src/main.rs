use anyhow::Context as _;
use clap::Parser;
use picross_solver::{
    board::{FullSolution, Puzzle},
    solve::solve,
};
use std::{fs, path::PathBuf};

#[derive(Parser)]
struct Args {
    puzzle_file: PathBuf,
}

fn main() -> anyhow::Result<()> {
    let args = Args::parse();
    let content = fs::read_to_string(args.puzzle_file).context("Could not open file")?;
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
