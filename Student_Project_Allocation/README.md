# Student Project Allocation System (Subject 28)

A constraint satisfaction-based system for optimally allocating students to projects based on preferences and constraints.

## Overview

This project implements a solution to the Student Project Allocation (SPA) problem using multiple algorithms and constraint programming approaches. It helps match students to projects while considering:

- Student preferences (ranked choices)
- Project capacities
- Complex allocation constraints
- Overall satisfaction optimization

## Features

- Multiple allocation algorithms:
  - CP-SAT (Constraint Programming with SAT solver)
  - Greedy approach
  - Random allocation with optimization
- Benchmarking system to compare algorithm performance
- Interactive chatbot interface for easy usage
- Visualization of allocations using network graphs
- Detailed metrics on preference satisfaction
- Support for custom constraints

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Set up your OpenAI API key:
```bash
export OPENAI_API_KEY=your_key_here
```

## Usage

Run the interactive interface:
```bash
streamlit run chatbot_ui.py
```

The system will:
1. Accept student preferences and project details
2. Run multiple allocation algorithms
3. Compare and select the best solution
4. Provide detailed analysis of the allocation
5. Visualize the results

## Core Components

- `main.py`: Core allocation algorithms and logic
- `ai.py`: AI tools and visualization functions
- `chatbot_ui.py`: Streamlit-based user interface

## Algorithm Details

The system implements three main approaches:

1. **CP-SAT**: Uses Google OR-Tools for optimal constraint satisfaction
2. **Greedy**: Assigns based on preference order and availability
3. **Random**: Multiple random assignments with optimization

## Solution Metrics

The system evaluates solutions based on:
- Preference satisfaction rates
- Individual student preference ranks
- Distribution of allocations
- Algorithm execution time
- Solution feasibility

## References

Based on research in:
- Gent et al.'s work on Stable Marriage as CSP
- University of Glasgow's SPA-P (Student-Project Allocation) studies
- Constraint programming approaches to matching problems

## Made by

- [Enguerrand Turcat](mailto:enguerrand.turcat@epita.fr)
- [Matthew Banawa](matthew.banawa@epita.fr)
- [Verhille Titouan](mailto:titouan.verhille@epita.fr)
