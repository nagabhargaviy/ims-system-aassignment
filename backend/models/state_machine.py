class InvalidTransition(Exception):
    pass


class WorkItemStateMachine:
    valid_transitions = {
        "OPEN": ["INVESTIGATING"],
        "INVESTIGATING": ["RESOLVED"],
        "RESOLVED": ["CLOSED"],
    }

    def __init__(self, current_state):
        self.current_state = current_state

    def can_transition(self, new_state):
        return new_state in self.valid_transitions.get(self.current_state, [])

    def transition(self, new_state, has_rca=False):
        if not self.can_transition(new_state):
            raise InvalidTransition(
                f"Cannot move from {self.current_state} to {new_state}"
            )

        if new_state == "CLOSED" and not has_rca:
            raise Exception("RCA required before closing incident")

        return new_state