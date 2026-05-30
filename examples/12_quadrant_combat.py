"""Quadrant Combat: clear the sector of hostiles, original FSM (2026).

Inspired by Mike Mayfield's 1971 high-school BASIC game and David Ahl's
1973 *BASIC Computer Games* collection of resource-bounded space combat.
The game mechanic of energy-bounded phaser fire, limited torpedoes, and
sector-by-sector hunting is in the public domain; the names and
trademarks of any particular intellectual property they later attached
to are NOT used here. This is a from-scratch FSM in the same tradition.

The FSM gates resource-bounded combat: phasers and torpedoes refuse
when energy or ammo runs out; docking at a starport refunds both but
must be reachable. ``end_mission`` is only legal after all hostiles
are destroyed.
"""

from __future__ import annotations

import random

from burr.core import ApplicationBuilder, State, action
from burr.core.action import Condition

from theodosia import mount


@action(
    reads=[],
    writes=[
        "energy", "shields", "torpedoes", "hostiles", "starports",
        "tick", "sector", "log", "status",
    ],
)
def begin_patrol(state: State, seed: int | None = None) -> State:
    if seed is not None:
        random.seed(seed)
    return state.update(
        energy=3000,
        shields=0,
        torpedoes=10,
        hostiles=8,
        starports=4,
        tick=0,
        sector=random.randint(1, 64),
        log=[],
        status="patrolling",
    )


@action(reads=["energy", "shields", "torpedoes", "hostiles"], writes=["log"])
def scan_sector(state: State) -> State:
    report = (
        f"sec={state['sector']} energy={state['energy']} shields={state['shields']} "
        f"torps={state['torpedoes']} hostiles_left={state['hostiles']}"
    )
    return state.update(log=state["log"] + [("scan", report)])


@action(reads=["energy", "hostiles"], writes=["energy", "hostiles", "log", "status"])
def fire_beam(state: State, power: int) -> State:
    if power <= 0 or power > state["energy"]:
        raise ValueError(f"beam power must be 1..{state['energy']}; got {power}")
    if state["hostiles"] <= 0:
        raise ValueError("no hostiles in range")
    hit = min(power // 100, state["hostiles"])
    left = state["hostiles"] - hit
    return state.update(
        energy=state["energy"] - power,
        hostiles=left,
        log=state["log"] + [("beam", f"power={power} hit={hit}")],
        status="victory" if left == 0 else "patrolling",
    )


@action(reads=["torpedoes", "hostiles"], writes=["torpedoes", "hostiles", "log", "status"])
def fire_torpedo(state: State, bearing: int) -> State:
    if state["torpedoes"] <= 0:
        raise ValueError("no torpedoes left")
    if not 0 <= bearing < 360:
        raise ValueError("bearing must be 0..359")
    if state["hostiles"] <= 0:
        raise ValueError("no hostiles in range")
    hit = random.random() < 0.55
    left = max(0, state["hostiles"] - 1) if hit else state["hostiles"]
    return state.update(
        torpedoes=state["torpedoes"] - 1,
        hostiles=left,
        log=state["log"] + [("torpedo", f"bearing={bearing} hit={hit}")],
        status="victory" if left == 0 else "patrolling",
    )


@action(reads=["energy"], writes=["sector", "energy", "tick", "log"])
def jump(state: State, sector: int, intensity: float) -> State:
    if not 1 <= sector <= 64:
        raise ValueError("sector must be 1..64")
    cost = int(intensity * 100)
    if cost > state["energy"]:
        raise ValueError(f"not enough energy: jump costs {cost}, have {state['energy']}")
    return state.update(
        sector=sector,
        energy=state["energy"] - cost,
        tick=state["tick"] + 1,
        log=state["log"] + [("jump", f"to sector {sector} at intensity {intensity}")],
    )


@action(reads=["energy", "shields"], writes=["shields", "energy"])
def raise_shields(state: State, units: int) -> State:
    if units > state["energy"]:
        raise ValueError("not enough energy")
    return state.update(shields=state["shields"] + units, energy=state["energy"] - units)


@action(reads=["starports"], writes=["energy", "torpedoes", "shields", "log"])
def dock_starport(state: State) -> State:
    if state["starports"] <= 0:
        raise ValueError("no starports reachable")
    return state.update(
        energy=3000,
        torpedoes=10,
        shields=0,
        log=state["log"] + [("dock", "refueled, rearmed")],
    )


@action(reads=["hostiles"], writes=["status"])
def end_mission(state: State) -> State:
    if state["hostiles"] > 0:
        raise ValueError(f"{state['hostiles']} hostiles still active")
    return state.update(status="mission complete")


def build_application():
    fighting = Condition.expr("status == 'patrolling'")
    won = Condition.expr("status == 'victory'")
    return (
        ApplicationBuilder()
        .with_actions(
            begin_patrol=begin_patrol,
            scan_sector=scan_sector,
            fire_beam=fire_beam,
            fire_torpedo=fire_torpedo,
            jump=jump,
            raise_shields=raise_shields,
            dock_starport=dock_starport,
            end_mission=end_mission,
        )
        .with_transitions(
            ("begin_patrol", "scan_sector"),
            ("scan_sector", "fire_beam", fighting),
            ("scan_sector", "fire_torpedo", fighting),
            ("scan_sector", "jump", fighting),
            ("scan_sector", "raise_shields", fighting),
            ("scan_sector", "dock_starport", fighting),
            ("fire_beam", "scan_sector", fighting),
            ("fire_torpedo", "scan_sector", fighting),
            ("jump", "scan_sector"),
            ("raise_shields", "scan_sector"),
            ("dock_starport", "scan_sector"),
            ("scan_sector", "end_mission", won),
            ("fire_beam", "end_mission", won),
            ("fire_torpedo", "end_mission", won),
        )
        .with_state(
            energy=0, shields=0, torpedoes=0, hostiles=0, starports=0,
            tick=0, sector=0, log=[], status="empty",
        )
        .with_entrypoint("begin_patrol")
        .build()
    )


def build_server():
    return mount(build_application, name="quadrant-combat")


if __name__ == "__main__":
    build_server().run()
