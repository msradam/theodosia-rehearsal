"""Towers of Hanoi: the canonical recursive puzzle (Lucas, 1883).

Edouard Lucas's 1883 puzzle ships in every "your first BASIC program"
collection. Three pegs, N disks of decreasing size on peg A; move the
stack to peg C without ever placing a larger disk on a smaller one.

This FSM is the cleanest possible demonstration of structural refusals:
- ``move(from_peg, to_peg)`` on an empty source returns ``empty_source``.
- ``move`` placing a bigger disk on a smaller one returns ``illegal_move``.
- ``move`` to the same peg returns ``same_peg``.

The optimal solution is ``2**n - 1`` moves. The state carries the move
count so you can compare an agent's solution to the optimum.
"""

from __future__ import annotations

from burr.core import ApplicationBuilder, State, action
from burr.core.action import Condition

from theodosia import mount


@action(reads=[], writes=["pegs", "n_disks", "moves", "status"])
def setup(state: State, n_disks: int = 4) -> State:
    if not 1 <= n_disks <= 12:
        raise ValueError("n_disks must be between 1 and 12")
    return state.update(
        pegs={"A": list(range(n_disks, 0, -1)), "B": [], "C": []},
        n_disks=n_disks,
        moves=0,
        status="playing",
    )


@action(reads=["pegs", "n_disks", "moves"], writes=["pegs", "moves", "status"])
def move(state: State, from_peg: str, to_peg: str) -> State:
    pegs = {k: list(v) for k, v in state["pegs"].items()}
    if from_peg not in pegs or to_peg not in pegs:
        raise ValueError(f"peg must be one of A, B, C; got {from_peg!r} -> {to_peg!r}")
    if from_peg == to_peg:
        raise ValueError("same_peg: source and destination are the same")
    src, dst = pegs[from_peg], pegs[to_peg]
    if not src:
        raise ValueError(f"empty_source: peg {from_peg} has no disks")
    disk = src[-1]
    if dst and dst[-1] < disk:
        raise ValueError(
            f"illegal_move: cannot place disk {disk} on smaller disk {dst[-1]}"
        )
    src.pop()
    dst.append(disk)
    won = pegs["C"] == list(range(state["n_disks"], 0, -1))
    return state.update(
        pegs=pegs,
        moves=state["moves"] + 1,
        status="solved" if won else "playing",
    )


@action(reads=["n_disks", "moves"], writes=["status"])
def declare_solved(state: State) -> State:
    optimum = 2 ** state["n_disks"] - 1
    return state.update(status=f"solved in {state['moves']} moves (optimum: {optimum})")


def build_application():
    return (
        ApplicationBuilder()
        .with_actions(setup=setup, move=move, declare_solved=declare_solved)
        .with_transitions(
            ("setup", "move"),
            ("move", "move", Condition.expr("status == 'playing'")),
            ("move", "declare_solved", Condition.expr("status == 'solved'")),
        )
        .with_state(pegs={"A": [], "B": [], "C": []}, n_disks=0, moves=0, status="empty")
        .with_entrypoint("setup")
        .build()
    )


def build_server():
    return mount(build_application, name="hanoi")


if __name__ == "__main__":
    build_server().run()
