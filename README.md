# Sudoku Boards as CSPs

Python implementation of a Sudoku CSP solver using:

- Backtracking search
- Forward checking
- AC-3 arc consistency
- MRV + degree heuristic for variable ordering

## Repository

https://github.com/shi-ni/Sudoku-Boards-as-CSPs

## Project Structure

- `sudoku_csp.py`: CSP model, AC-3, forward checking, backtracking solver
- `main.py`: CLI script that solves one or more board files
- `boards/easy.txt`
- `boards/medium.txt`
- `boards/hard.txt`
- `boards/veryhard.txt`
- `report.md`: assignment deliverable with solutions and metrics

## Run

PowerShell one-command launcher:

```powershell
./run.ps1
```

You can still run with Python directly:

```bash
python main.py
```

Or solve specific boards:

```bash
python main.py boards/easy.txt boards/hard.txt
```

## Input Format

- Exactly 9 lines per file
- Each line has exactly 9 digits (`0-9`)
- `0` represents an empty cell

## Output

For each board, the program prints:

- Solved grid
- Number of BACKTRACK calls
- Number of BACKTRACK failures
