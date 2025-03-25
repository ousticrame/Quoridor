use anyhow::bail;
use anyhow::Context as _;
use itertools::Itertools as _;
use std::{
    fs::{self, File},
    io::Error,
};

struct PicrossGrid {
    rows: Vec<Vec<u32>>,
    colm: Vec<Vec<u32>>,
}

impl TryFrom<&str> for PicrossGrid {
    type Error = anyhow::Error;

    fn try_from(value: &str) -> Result<Self, Self::Error> {
        let lines: Vec<_> = value.lines().collect();
        if lines.len() != 2 {
            bail!("Input file should be 2 lines long");
        }

        const DELIM: &str = " | ";
        let rows = lines[0]
            .split(DELIM)
            .map(|line| {
                line.split_whitespace()
                    .map(|num| num.parse::<u32>())
                    .collect::<Result<Vec<_>>, _>()
            })
            .collect::<Vec<_>>()?;

        Ok(Self {
            rows,
            colm: todo!(),
        })
    }
}

fn main() -> anyhow::Result<()> {
    let content = fs::read_to_string("./test.pc").context("Could not open file")?;
    let grid = PicrossGrid::try_from(&content[..]).context("Could not parse input")?;

    dbg(&grid);

    println!("Hello, world!");
    Ok(())
}
