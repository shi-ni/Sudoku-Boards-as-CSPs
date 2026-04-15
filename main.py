from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict

from sudoku_csp import board_to_string, solve_board


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Solve Sudoku boards as CSPs (Backtracking + Forward Checking + AC-3)."
    )
    parser.add_argument(
        "boards",
        nargs="*",
        type=Path,
        default=[
            Path("boards/easy.txt"),
            Path("boards/medium.txt"),
            Path("boards/hard.txt"),
            Path("boards/veryhard.txt"),
        ],
        help="Board files to solve (default: all four assignment boards).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    summary: Dict[str, Dict[str, int]] = {}

    for board_path in args.boards:
        solved_board, stats = solve_board(board_path)

        print(f"\n=== {board_path.name} ===")
        print(board_to_string(solved_board))
        print(f"BACKTRACK calls: {stats.backtrack_calls}")
        print(f"BACKTRACK failures: {stats.backtrack_failures}")

        summary[board_path.name] = {
            "calls": stats.backtrack_calls,
            "failures": stats.backtrack_failures,
        }

    print("\n=== Summary ===")
    for name, stats in summary.items():
        print(f"{name}: calls={stats['calls']}, failures={stats['failures']}")


if __name__ == "__main__":
    main()
