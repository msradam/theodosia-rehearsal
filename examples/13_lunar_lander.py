"""Lunar Lander: descend with limited fuel (Storer, 1969).

Jim Storer, *Lunar* (Lexington High School, FOCAL on a PDP-8, 1969).
Republished in David Ahl's *BASIC Computer Games* (1973). One of the
oldest computer games on record; mechanic released to public domain.

Physics each tick: gravity pulls down, fuel-burn pushes up. Land with
velocity <= 5 m/s and you're a hero; <= 15 m/s and you'll need a new
ship; faster and you make a new crater.

The FSM gates the tick loop: burn(rate) -> tick -> burn(rate) -> ...
``tick`` is unreachable when you've already landed or crashed.
"""

from __future__ import annotations

from burr.core import ApplicationBuilder, State, action
from burr.core.action import Condition

from theodosia import mount

_GRAVITY = 1.62  # m/s^2 (lunar)
_DT = 1.0  # tick seconds
_EXHAUST_V = 2500.0  # m/s
_DRY_MASS = 16500.0  # kg
_SAFE_LANDING = 5.0  # m/s
_HARD_LANDING = 15.0  # m/s


@action(reads=[], writes=["altitude", "velocity", "fuel", "tick", "status", "log"])
def liftoff_sequence(state: State) -> State:
    return state.update(
        altitude=1000.0,
        velocity=-50.0,  # falling
        fuel=8800.0,  # kg
        tick=0,
        status="descending",
        log=[],
    )


@action(reads=["fuel", "tick", "status"], writes=["pending_burn", "log"])
def set_burn(state: State, kg_per_sec: float) -> State:
    if state["status"] != "descending":
        raise ValueError(f"cannot burn: status={state['status']}")
    if kg_per_sec < 0:
        raise ValueError("burn rate must be >= 0")
    max_burn = min(state["fuel"], 200.0)
    if kg_per_sec > max_burn:
        raise ValueError(f"max burn this tick is {max_burn} kg/s; got {kg_per_sec}")
    return state.update(
        pending_burn=kg_per_sec,
        log=state["log"] + [("burn", f"{kg_per_sec} kg/s queued")],
    )


@action(
    reads=["altitude", "velocity", "fuel", "tick", "pending_burn", "log", "status"],
    writes=["altitude", "velocity", "fuel", "tick", "pending_burn", "status", "log"],
)
def tick(state: State) -> State:
    burn = state.get("pending_burn", 0.0)
    mass = _DRY_MASS + state["fuel"]
    thrust = burn * _EXHAUST_V
    accel = -_GRAVITY + thrust / mass
    new_vel = state["velocity"] + accel * _DT
    new_alt = state["altitude"] + state["velocity"] * _DT + 0.5 * accel * _DT * _DT
    new_fuel = max(0.0, state["fuel"] - burn * _DT)
    new_tick = state["tick"] + 1
    if new_alt <= 0:
        impact = abs(new_vel)
        if impact <= _SAFE_LANDING:
            status = f"landed: soft touchdown at {impact:.2f} m/s"
        elif impact <= _HARD_LANDING:
            status = f"landed hard: {impact:.2f} m/s; structural damage"
        else:
            status = f"crashed: {impact:.2f} m/s; ship destroyed"
        return state.update(
            altitude=0.0, velocity=new_vel, fuel=new_fuel, tick=new_tick,
            pending_burn=0.0, status=status,
            log=state["log"] + [("impact", status)],
        )
    return state.update(
        altitude=new_alt, velocity=new_vel, fuel=new_fuel, tick=new_tick,
        pending_burn=0.0, status="descending",
        log=state["log"]
        + [("tick", f"t={new_tick} alt={new_alt:.1f} v={new_vel:.2f} fuel={new_fuel:.0f}")],
    )


def build_application():
    going = Condition.expr("status == 'descending'")
    return (
        ApplicationBuilder()
        .with_actions(
            liftoff_sequence=liftoff_sequence, set_burn=set_burn, tick=tick,
        )
        .with_transitions(
            ("liftoff_sequence", "set_burn"),
            ("set_burn", "tick"),
            ("tick", "set_burn", going),
        )
        .with_state(
            altitude=0.0, velocity=0.0, fuel=0.0, tick=0,
            pending_burn=0.0, status="empty", log=[],
        )
        .with_entrypoint("liftoff_sequence")
        .build()
    )


def build_server():
    return mount(build_application, name="lunar-lander")


if __name__ == "__main__":
    build_server().run()
