from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Deque, Dict, Iterable, List, Optional, Set, Tuple

Cell = Tuple[int, int]
Board = List[List[int]]
DomainMap = Dict[Cell, Set[int]]


@dataclass
class SolveStats:
    backtrack_calls: int
    backtrack_failures: int


class SudokuCSP:
    """Sudoku solved as a CSP with backtracking, forward checking, and AC-3."""

    def __init__(self, board: Board) -> None:
        self.board = board
        self.variables: List[Cell] = [(row, col) for row in range(9) for col in range(9)]
        self.neighbors: Dict[Cell, Set[Cell]] = self._build_neighbors()
        self.backtrack_calls = 0
        self.backtrack_failures = 0

    def solve(self) -> Optional[Board]:
        domains = self._initial_domains()
        if not self._ac3(domains):
            return None

        solved_domains = self._backtrack(domains)
        if solved_domains is None:
            return None
        return self._domains_to_board(solved_domains)

    def get_stats(self) -> SolveStats:
        return SolveStats(
            backtrack_calls=self.backtrack_calls,
            backtrack_failures=self.backtrack_failures,
        )

    def _build_neighbors(self) -> Dict[Cell, Set[Cell]]:
        neighbors: Dict[Cell, Set[Cell]] = {}
        for row in range(9):
            for col in range(9):
                current = (row, col)
                related: Set[Cell] = set()

                # Row and column peers.
                for idx in range(9):
                    if idx != col:
                        related.add((row, idx))
                    if idx != row:
                        related.add((idx, col))

                # 3x3 box peers.
                box_row = (row // 3) * 3
                box_col = (col // 3) * 3
                for r in range(box_row, box_row + 3):
                    for c in range(box_col, box_col + 3):
                        if (r, c) != current:
                            related.add((r, c))

                neighbors[current] = related
        return neighbors

    def _initial_domains(self) -> DomainMap:
        domains: DomainMap = {}
        for row in range(9):
            for col in range(9):
                value = self.board[row][col]
                if value == 0:
                    domains[(row, col)] = set(range(1, 10))
                else:
                    domains[(row, col)] = {value}
        return domains

    def _copy_domains(self, domains: DomainMap) -> DomainMap:
        return {cell: set(values) for cell, values in domains.items()}

    def _all_singleton(self, domains: DomainMap) -> bool:
        return all(len(values) == 1 for values in domains.values())

    def _select_unassigned_variable(self, domains: DomainMap) -> Optional[Cell]:
        candidates = [cell for cell in self.variables if len(domains[cell]) > 1]
        if not candidates:
            return None

        # MRV with degree tie-breaker.
        return min(
            candidates,
            key=lambda cell: (
                len(domains[cell]),
                -sum(1 for neighbor in self.neighbors[cell] if len(domains[neighbor]) > 1),
            ),
        )

    def _arcs_for_cell(self, cell: Cell) -> Deque[Tuple[Cell, Cell]]:
        return deque((neighbor, cell) for neighbor in self.neighbors[cell])

    def _forward_check(self, cell: Cell, value: int, domains: DomainMap) -> bool:
        for neighbor in self.neighbors[cell]:
            if value in domains[neighbor]:
                domains[neighbor].discard(value)
                if not domains[neighbor]:
                    return False
        return True

    def _backtrack(self, domains: DomainMap) -> Optional[DomainMap]:
        self.backtrack_calls += 1

        if self._all_singleton(domains):
            return domains

        var = self._select_unassigned_variable(domains)
        if var is None:
            return domains

        for value in sorted(domains[var]):
            new_domains = self._copy_domains(domains)
            new_domains[var] = {value}

            if not self._forward_check(var, value, new_domains):
                continue

            # Re-run AC-3 globally after forward checking to keep consistency complete.
            if not self._ac3(new_domains):
                continue

            result = self._backtrack(new_domains)
            if result is not None:
                return result

        self.backtrack_failures += 1
        return None

    def _ac3(
        self,
        domains: DomainMap,
        queue: Optional[Deque[Tuple[Cell, Cell]]] = None,
    ) -> bool:
        if queue is None:
            queue = deque((cell, neighbor) for cell in self.variables for neighbor in self.neighbors[cell])

        while queue:
            xi, xj = queue.popleft()
            if self._revise(domains, xi, xj):
                if not domains[xi]:
                    return False
                for xk in self.neighbors[xi]:
                    if xk != xj:
                        queue.append((xk, xi))
        return True

    def _revise(self, domains: DomainMap, xi: Cell, xj: Cell) -> bool:
        revised = False
        to_remove: Set[int] = set()

        for value in domains[xi]:
            if not any(value != other for other in domains[xj]):
                to_remove.add(value)

        if to_remove:
            domains[xi] -= to_remove
            revised = True

        return revised

    def _domains_to_board(self, domains: DomainMap) -> Board:
        solved: Board = [[0 for _ in range(9)] for _ in range(9)]
        for (row, col), values in domains.items():
            solved[row][col] = next(iter(values))
        return solved


def read_board(path: Path) -> Board:
    if not path.exists():
        raise FileNotFoundError(f"Board file not found: {path}")

    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(lines) != 9:
        raise ValueError(f"Board file must contain exactly 9 lines: {path}")

    board: Board = []
    for index, line in enumerate(lines, start=1):
        if len(line) != 9 or not line.isdigit():
            raise ValueError(
                f"Invalid line {index} in {path}. Each line must contain exactly 9 digits."
            )
        board.append([int(char) for char in line])
    return board


def board_to_string(board: Board) -> str:
    return "\n".join(" ".join(str(value) for value in row) for row in board)


def solve_board(path: Path) -> Tuple[Board, SolveStats]:
    board = read_board(path)
    solver = SudokuCSP(board)
    solved = solver.solve()

    if solved is None:
        raise ValueError(f"No solution found for board: {path}")

    return solved, solver.get_stats()
