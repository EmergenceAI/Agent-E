from enum import Enum


class MessageType(Enum):
    PLAN = "plan"
    STEP = "step"
    ACTION ="action"
    ANSWER = "answer"
    QUESTION = "question"
    INFO = "info"
    FINAL = "final"
    DONE = "transaction_done"
    ERROR = "error"
    MAX_TURNS_REACHED = "max_turns_reached"
