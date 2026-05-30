"""Animal: the twenty-questions guessing tree (Arthur Luehrmann, 1973).

Arthur Luehrmann's *Animal* was a teaching staple in early personal
computing: the program asks yes/no questions to guess what animal you
are thinking of; when it fails, you teach it the new animal and a
distinguishing question, which it remembers for future sessions.

The decision-tree-as-FSM idea is mathematical and predates the program
by decades. The Burr Application below is a from-scratch implementation
of the pattern.

The FSM gates: ask_question -> answer -> ask_question -> ... ->
propose -> teach_new (on miss). ``propose`` is unreachable until the
agent walks the tree to a leaf.
"""

from __future__ import annotations

from typing import Any

from burr.core import ApplicationBuilder, State, action
from burr.core.action import Condition

from theodosia import mount


# Initial seed tree: a question -> {yes: subtree-or-leaf, no: ...}
# Leaves are plain strings naming an animal.
_SEED_TREE: dict[str, Any] = {
    "q": "does it live in water?",
    "yes": "fish",
    "no": {
        "q": "does it have feathers?",
        "yes": "sparrow",
        "no": "dog",
    },
}


@action(reads=[], writes=["tree", "cursor", "log", "status"])
def begin(state: State) -> State:
    return state.update(
        tree=_SEED_TREE,
        cursor=_SEED_TREE,  # current node we're at
        log=[],
        status="asking",
    )


@action(reads=["cursor"], writes=["last_question"])
def ask_question(state: State) -> State:
    cur = state["cursor"]
    if isinstance(cur, str):
        raise ValueError(f"at a leaf ({cur!r}); call propose, not ask_question")
    return state.update(last_question=cur["q"])


@action(reads=["cursor", "log"], writes=["cursor", "log", "status"])
def answer(state: State, yes: bool) -> State:
    cur = state["cursor"]
    if isinstance(cur, str):
        raise ValueError(f"at a leaf ({cur!r}); call propose, not answer")
    branch = cur["yes"] if yes else cur["no"]
    entry = (cur["q"], "yes" if yes else "no")
    return state.update(
        cursor=branch,
        log=state["log"] + [entry],
        status="proposing" if isinstance(branch, str) else "asking",
    )


@action(reads=["cursor"], writes=["proposal", "status"])
def propose(state: State) -> State:
    cur = state["cursor"]
    if not isinstance(cur, str):
        raise ValueError("not at a leaf yet")
    return state.update(proposal=cur, status="awaiting_verdict")


@action(reads=["proposal"], writes=["status"])
def confirm(state: State) -> State:
    return state.update(status=f"correct: it was {state['proposal']}")


@action(reads=["proposal", "tree", "log"], writes=["tree", "status"])
def teach(state: State, animal: str, question: str, answer_for_new: bool) -> State:
    """When the proposal was wrong, teach the tree.

    ``question`` must distinguish ``animal`` from ``proposal``.
    ``answer_for_new`` is whether the answer to ``question`` is yes for
    the new animal.
    """
    if not state["log"]:
        raise ValueError("no path walked; nothing to teach")
    # Reconstruct the parent node along the log to insert at the leaf.
    parent = state["tree"]
    path = state["log"][:-1]
    last_q, last_dir = state["log"][-1]
    for q, direction in path:
        parent = parent[direction]
    old_leaf = parent[last_dir]
    new_node = {
        "q": question,
        "yes": animal if answer_for_new else old_leaf,
        "no": old_leaf if answer_for_new else animal,
    }
    parent[last_dir] = new_node
    return state.update(
        tree=state["tree"],
        status=f"learned {animal}; tree now distinguishes via: {question}",
    )


def build_application():
    asking = Condition.expr("status == 'asking'")
    proposing = Condition.expr("status == 'proposing'")
    awaiting = Condition.expr("status == 'awaiting_verdict'")
    return (
        ApplicationBuilder()
        .with_actions(
            begin=begin,
            ask_question=ask_question,
            answer=answer,
            propose=propose,
            confirm=confirm,
            teach=teach,
        )
        .with_transitions(
            ("begin", "ask_question"),
            ("ask_question", "answer"),
            ("answer", "ask_question", asking),
            ("answer", "propose", proposing),
            ("propose", "confirm", awaiting),
            ("propose", "teach", awaiting),
        )
        .with_state(
            tree={}, cursor={}, log=[], status="empty",
            last_question="", proposal="",
        )
        .with_entrypoint("begin")
        .build()
    )


def build_server():
    return mount(build_application, name="animal")


if __name__ == "__main__":
    build_server().run()
