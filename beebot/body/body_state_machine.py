from typing import TYPE_CHECKING

from statemachine import StateMachine, State

if TYPE_CHECKING:
    from beebot.body import Body


class BodyStateMachine(StateMachine):
    setup = State(initial=True)
    starting = State()
    planning = State()
    deciding = State()
    executing = State()
    waiting = State()
    done = State(final=True)

    start = setup.to(starting)
    plan = starting.to(planning) | waiting.to(planning)
    decide = waiting.to(deciding)
    execute = waiting.to(executing)
    wait = (
        deciding.to(waiting)
        | planning.to(waiting)
        | executing.to(waiting)
        | starting.to(waiting)
    )
    finish = waiting.to(done) | executing.to(done)

    def __init__(self, body: "Body"):
        self.body = body
        super().__init__()
