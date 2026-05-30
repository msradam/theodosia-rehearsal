"""Hammurabi: rule Sumer for ten years (Ahl, *Creative Computing*, 1968).

David Ahl, *BASIC Computer Games* (1973), originally HAMURABI by Doug
Dyment on the HP-2000. Each year of your reign you allocate grain to
buy land, plant seed, and feed your people. Rats, plague, and harvest
luck decide the rest.

The FSM gates the yearly cycle: trading -> planting -> feeding ->
advance. Try to advance the year without feeding your people and the
server refuses; the agent sees `valid_next_actions=["feed_people"]`
and complies. Survive ten years to win.
"""

from __future__ import annotations

import random

from burr.core import ApplicationBuilder, State, action
from burr.core.action import Condition

from theodosia import mount


@action(
    reads=[],
    writes=["year", "people", "grain", "land", "land_price", "phase", "log", "planted", "fed"],
)
def start(state: State) -> State:
    return state.update(
        year=1,
        people=100,
        grain=2800,
        land=1000,
        land_price=random.randint(17, 26),
        phase="trading",
        log=[],
        planted=0,
        fed=0,
    )


@action(reads=["grain", "land_price"], writes=["land", "grain", "phase"])
def buy_land(state: State, acres: int) -> State:
    cost = acres * state["land_price"]
    if cost > state["grain"]:
        raise ValueError(f"not enough grain: need {cost}, have {state['grain']}")
    return state.update(land=state["land"] + acres, grain=state["grain"] - cost, phase="planting")


@action(reads=["land", "land_price"], writes=["land", "grain", "phase"])
def sell_land(state: State, acres: int) -> State:
    if acres > state["land"]:
        raise ValueError(f"only have {state['land']} acres")
    return state.update(
        land=state["land"] - acres,
        grain=state["grain"] + acres * state["land_price"],
        phase="planting",
    )


@action(reads=["grain", "people", "land"], writes=["grain", "planted", "phase"])
def plant_grain(state: State, acres: int) -> State:
    if acres > state["land"]:
        raise ValueError("more acres than you own")
    if acres > state["grain"]:
        raise ValueError("not enough seed grain")
    if acres > state["people"] * 10:
        raise ValueError("not enough people to till that much")
    return state.update(grain=state["grain"] - acres, planted=acres, phase="feeding")


@action(reads=["grain"], writes=["grain", "fed", "phase"])
def feed_people(state: State, bushels: int) -> State:
    if bushels > state["grain"]:
        raise ValueError("not that much grain")
    return state.update(grain=state["grain"] - bushels, fed=bushels, phase="ready")


@action(
    reads=["year", "people", "grain", "land", "planted", "fed", "log"],
    writes=["year", "people", "grain", "land_price", "phase", "log", "starved", "plague"],
)
def advance_year(state: State) -> State:
    fed = state["fed"]
    needed = state["people"] * 20
    starved = max(0, (needed - fed) // 20)
    yield_rate = random.randint(1, 6)
    harvest = state["planted"] * yield_rate
    rats = random.choice([0, 0, state["grain"] // 10, state["grain"] // 5])
    plague = random.random() < 0.15
    new_people = max(0, state["people"] - starved - (state["people"] // 2 if plague else 0))
    new_grain = max(0, state["grain"] + harvest - rats)
    entry = {
        "year": state["year"],
        "starved": starved,
        "yield": yield_rate,
        "rats": rats,
        "plague": plague,
        "people_after": new_people,
        "grain_after": new_grain,
    }
    return state.update(
        year=state["year"] + 1,
        people=new_people,
        grain=new_grain,
        land_price=random.randint(17, 26),
        phase="trading",
        log=state["log"] + [entry],
        starved=starved,
        plague=plague,
    )


def build_application():
    trading = Condition.expr("phase == 'trading'")
    planting = Condition.expr("phase == 'planting'")
    feeding = Condition.expr("phase == 'feeding'")
    ready = Condition.expr("phase == 'ready'")
    return (
        ApplicationBuilder()
        .with_actions(
            start=start,
            buy_land=buy_land,
            sell_land=sell_land,
            plant_grain=plant_grain,
            feed_people=feed_people,
            advance_year=advance_year,
        )
        .with_transitions(
            ("start", "buy_land", trading),
            ("start", "sell_land", trading),
            ("start", "plant_grain", trading),
            ("buy_land", "plant_grain", planting),
            ("sell_land", "plant_grain", planting),
            ("plant_grain", "feed_people", feeding),
            ("feed_people", "advance_year", ready),
            ("advance_year", "buy_land", trading),
            ("advance_year", "sell_land", trading),
            ("advance_year", "plant_grain", trading),
        )
        .with_state(
            year=0,
            people=0,
            grain=0,
            land=0,
            land_price=20,
            phase="empty",
            log=[],
            planted=0,
            fed=0,
            starved=0,
            plague=False,
        )
        .with_entrypoint("start")
        .build()
    )


def build_server():
    return mount(build_application, name="hammurabi")


if __name__ == "__main__":
    build_server().run()
