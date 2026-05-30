"""Bulls and Cows: code-breaking with bull/cow feedback.

A centuries-old pencil-and-paper guessing game. The player guesses a
four-digit secret; each guess returns ``bulls`` (right digit, right
position) and ``cows`` (right digit, wrong position). Decades older than
any 1970s board-game commercialization, mechanic is public domain.

The FSM gates: setup -> guess -> guess -> ... -> win or out_of_turns.
Guesses must be four distinct digits 0-9; anything else returns an
``invalid_guess`` refusal naming the constraint.
"""

from __future__ import annotations

import random

from burr.core import ApplicationBuilder, State, action
from burr.core.action import Condition

from theodosia import mount


def _score(secret: str, guess: str) -> tuple[int, int]:
    bulls = sum(1 for s, g in zip(secret, guess) if s == g)
    cows = sum(1 for g in guess if g in secret) - bulls
    return bulls, cows


@action(reads=[], writes=["secret", "turns_left", "history", "status"])
def setup(state: State, seed: int | None = None) -> State:
    if seed is not None:
        random.seed(seed)
    digits = list("0123456789")
    random.shuffle(digits)
    secret = "".join(digits[:4])
    return state.update(secret=secret, turns_left=10, history=[], status="playing")


@action(
    reads=["secret", "turns_left", "history"],
    writes=["turns_left", "history", "status"],
)
def guess(state: State, code: str) -> State:
    if len(code) != 4 or not code.isdigit() or len(set(code)) != 4:
        raise ValueError("invalid_guess: must be four distinct digits 0-9")
    bulls, cows = _score(state["secret"], code)
    history = state["history"] + [{"guess": code, "bulls": bulls, "cows": cows}]
    turns_left = state["turns_left"] - 1
    if bulls == 4:
        status = "won"
    elif turns_left <= 0:
        status = "out_of_turns"
    else:
        status = "playing"
    return state.update(turns_left=turns_left, history=history, status=status)


@action(reads=["history", "secret", "status"], writes=["status"])
def reveal(state: State) -> State:
    return state.update(status=f"{state['status']}; secret was {state['secret']}")


def build_application():
    playing = Condition.expr("status == 'playing'")
    done = Condition.expr("status != 'playing'")
    return (
        ApplicationBuilder()
        .with_actions(setup=setup, guess=guess, reveal=reveal)
        .with_transitions(
            ("setup", "guess"),
            ("guess", "guess", playing),
            ("guess", "reveal", done),
        )
        .with_state(secret="", turns_left=0, history=[], status="empty")
        .with_entrypoint("setup")
        .build()
    )


def build_server():
    return mount(build_application, name="bulls-and-cows")


if __name__ == "__main__":
    build_server().run()
