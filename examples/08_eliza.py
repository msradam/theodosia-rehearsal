"""ELIZA: Weizenbaum's pattern-reflecting psychiatrist (1966).

Joseph Weizenbaum, *ELIZA: A Computer Program for the Study of Natural
Language Communication Between Man and Machine* (CACM, 1966). The DOCTOR
script gave the program its first public outing. The pattern reflections
below are a tiny slice of Weizenbaum's original substitution rules.

The FSM gates: open -> listen -> reflect -> listen -> ..., with `close`
unreachable until at least three exchanges have happened. Try to close
the session in turn 1 and you get an `invalid_transition`.
"""

from __future__ import annotations

import re

from burr.core import ApplicationBuilder, State, action
from burr.core.action import Condition

from theodosia import mount

_REFLECTIONS: list[tuple[str, str]] = [
    (r"\bi am\b", "Why do you say you are"),
    (r"\bi feel\b", "How long have you felt"),
    (r"\bi can'?t\b", "What stops you from"),
    (r"\bi want\b", "What would it mean to"),
    (r"\bmother\b", "Tell me more about your mother"),
    (r"\bfather\b", "Tell me more about your father"),
    (r"\bsorry\b", "Apologies are not necessary"),
    (r"\bdream\b", "What do you think your dream means"),
    (r"\bcomputer\b", "What do computers have to do with this"),
]


@action(reads=[], writes=["transcript", "turn", "stage"])
def open(state: State) -> State:
    greeting = "Hello. I am ELIZA. How are you feeling today?"
    return state.update(transcript=[("eliza", greeting)], turn=0, stage="listening")


@action(reads=["transcript", "turn"], writes=["transcript", "turn", "stage"])
def listen(state: State, message: str) -> State:
    t = state["transcript"] + [("patient", message)]
    return state.update(transcript=t, turn=state["turn"] + 1, stage="reflecting")


@action(reads=["transcript"], writes=["transcript", "stage"])
def reflect(state: State) -> State:
    last = next((m for s, m in reversed(state["transcript"]) if s == "patient"), "")
    lower = last.lower()
    response = None
    for pat, lead in _REFLECTIONS:
        m = re.search(pat, lower)
        if m:
            tail = lower[m.end() :].strip(" ?.!").rstrip(",")
            response = f"{lead} {tail}?" if tail else f"{lead}?"
            break
    if response is None:
        response = "Please go on."
    t = state["transcript"] + [("eliza", response)]
    return state.update(transcript=t, stage="listening")


@action(reads=["transcript", "turn"], writes=["transcript", "stage"])
def close(state: State, parting: str = "It has been good to talk. Goodbye.") -> State:
    t = state["transcript"] + [("eliza", parting)]
    return state.update(transcript=t, stage="closed")


def build_application():
    return (
        ApplicationBuilder()
        .with_actions(open=open, listen=listen, reflect=reflect, close=close)
        .with_transitions(
            ("open", "listen"),
            ("listen", "reflect"),
            ("reflect", "listen"),
            ("reflect", "close", Condition.expr("turn >= 3")),
        )
        .with_state(transcript=[], turn=0, stage="empty")
        .with_entrypoint("open")
        .build()
    )


def build_server():
    return mount(build_application, name="eliza")


if __name__ == "__main__":
    build_server().run()
