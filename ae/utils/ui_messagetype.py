from enum import Enum


# class syntax
class MessageType(Enum):
    PLAN = "plan"
    STEP = "step"
    ACTION ="action"
    ANSWER = "answer"
    QUESTION= "question"
    INFO = "info"
