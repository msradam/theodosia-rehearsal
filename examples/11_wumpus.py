"""Hunt the Wumpus: cave-crawler with hazards (Yob, 1972).

Gregory Yob, *Hunt the Wumpus* (Creative Computing, 1973). Twenty rooms
arranged as the vertices of a dodecahedron. One room holds the Wumpus,
two hold bottomless pits, two hold superbats. You have five arrows.

The FSM gates the action loop:
- ``move(room)`` refuses any room not adjacent to your current one.
- ``shoot(path)`` refuses when you are out of arrows or the path contains
  a non-adjacent step.
- ``win`` and ``die`` are terminal.

Hazard hints (``smell wumpus``, ``feel breeze``, ``hear bats``) come back
in the move result so the agent has something to reason about.
"""

from __future__ import annotations

import random

from burr.core import ApplicationBuilder, State, action
from burr.core.action import Condition

from theodosia import mount

# Dodecahedron adjacency: 20 rooms numbered 1..20.
_CAVE: dict[int, tuple[int, int, int]] = {
    1: (2, 5, 8), 2: (1, 3, 10), 3: (2, 4, 12), 4: (3, 5, 14),
    5: (1, 4, 6), 6: (5, 7, 15), 7: (6, 8, 17), 8: (1, 7, 9),
    9: (8, 10, 18), 10: (2, 9, 11), 11: (10, 12, 19), 12: (3, 11, 13),
    13: (12, 14, 20), 14: (4, 13, 15), 15: (6, 14, 16), 16: (15, 17, 20),
    17: (7, 16, 18), 18: (9, 17, 19), 19: (11, 18, 20), 20: (13, 16, 19),
}


def _place(occupied: set[int]) -> int:
    while True:
        r = random.randint(1, 20)
        if r not in occupied:
            occupied.add(r)
            return r


@action(reads=[], writes=["player", "wumpus", "pits", "bats", "arrows", "status", "hints"])
def enter_cave(state: State, seed: int | None = None) -> State:
    if seed is not None:
        random.seed(seed)
    occupied: set[int] = set()
    player = _place(occupied)
    wumpus = _place(occupied)
    pits = {_place(occupied), _place(occupied)}
    bats = {_place(occupied), _place(occupied)}
    return state.update(
        player=player,
        wumpus=wumpus,
        pits=list(pits),
        bats=list(bats),
        arrows=5,
        status="exploring",
        hints=_hints(player, wumpus, set(pits), set(bats)),
    )


def _hints(room: int, wumpus: int, pits: set[int], bats: set[int]) -> list[str]:
    neighbors = set(_CAVE[room])
    h = []
    if wumpus in neighbors:
        h.append("you smell the wumpus")
    if neighbors & pits:
        h.append("you feel a breeze")
    if neighbors & bats:
        h.append("you hear bats flapping")
    return h


@action(
    reads=["player", "wumpus", "pits", "bats", "status"],
    writes=["player", "status", "hints"],
)
def move(state: State, room: int) -> State:
    here = state["player"]
    if room not in _CAVE[here]:
        raise ValueError(
            f"not_adjacent: room {here} connects to {list(_CAVE[here])}, not {room}"
        )
    pits = set(state["pits"])
    bats = set(state["bats"])
    wumpus = state["wumpus"]
    if room == wumpus:
        return state.update(player=room, status="dead: the wumpus ate you", hints=[])
    if room in pits:
        return state.update(player=room, status="dead: fell into a pit", hints=[])
    if room in bats:
        bat_drop = random.choice([r for r in range(1, 21) if r != room])
        return state.update(
            player=bat_drop,
            status="exploring",
            hints=["bats whisked you to a random room"] + _hints(bat_drop, wumpus, pits, bats),
        )
    return state.update(player=room, status="exploring", hints=_hints(room, wumpus, pits, bats))


@action(
    reads=["player", "wumpus", "arrows", "status"],
    writes=["arrows", "wumpus", "status"],
)
def shoot(state: State, path: list[int]) -> State:
    if state["arrows"] <= 0:
        raise ValueError("no arrows left")
    if not 1 <= len(path) <= 5:
        raise ValueError("path must be 1 to 5 rooms")
    cur = state["player"]
    for step in path:
        if step not in _CAVE[cur]:
            raise ValueError(f"arrow path breaks: room {cur} does not connect to {step}")
        cur = step
        if cur == state["wumpus"]:
            return state.update(arrows=state["arrows"] - 1, wumpus=-1, status="won")
    arrows = state["arrows"] - 1
    if arrows == 0:
        return state.update(arrows=0, status="dead: out of arrows, wumpus heard you")
    return state.update(arrows=arrows, status="exploring")


def build_application():
    return (
        ApplicationBuilder()
        .with_actions(enter_cave=enter_cave, move=move, shoot=shoot)
        .with_transitions(
            ("enter_cave", "move", Condition.expr("status == 'exploring'")),
            ("enter_cave", "shoot", Condition.expr("status == 'exploring'")),
            ("move", "move", Condition.expr("status == 'exploring'")),
            ("move", "shoot", Condition.expr("status == 'exploring'")),
            ("shoot", "move", Condition.expr("status == 'exploring'")),
            ("shoot", "shoot", Condition.expr("status == 'exploring'")),
        )
        .with_state(
            player=0, wumpus=0, pits=[], bats=[], arrows=0, status="empty", hints=[]
        )
        .with_entrypoint("enter_cave")
        .build()
    )


def build_server():
    return mount(build_application, name="wumpus")


if __name__ == "__main__":
    build_server().run()
