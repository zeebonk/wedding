import dataclasses
import inspect
import json
import sys
from dataclasses import dataclass
from typing import ClassVar

gijsisgek = True


@dataclass
class Message:
    pass


@dataclass
class LobbyCount(Message):
    type: ClassVar = "lobby-count"
    connected: int
    done: int


@dataclass
class QuestionAnswers(Message):
    type: ClassVar = "question-answers"
    name: str
    age: int


@dataclass
class Reset(Message):
    type: ClassVar = "reset"


@dataclass
class AuthCodeInvalid(Message):
    type: ClassVar = "auth-code-invalid"


@dataclass
class ShowCountCode(Message):
    type: ClassVar = "show-count-code"
    color: str


@dataclass
class CountCode(Message):
    type: ClassVar = "count-code"
    code: int


@dataclass
class CountCodeOk(Message):
    type: ClassVar = "count-code-ok"


@dataclass
class CountCodeInvalid(Message):
    type: ClassVar = "count-code-invalid"


@dataclass
class AuthCode(Message):
    type: ClassVar = "auth-code"
    code: int


@dataclass
class AuthCodeOk(Message):
    type: ClassVar = "auth-code-ok"


@dataclass
class Countdown(Message):
    type: ClassVar = "countdown"
    count: int


@dataclass
class WaitForGroups(Message):
    type: ClassVar = "wait-for-groups"
    done: int
    total: int


@dataclass
class ShowSuccess(Message):
    type: ClassVar = "show-success"


MESSAGE_CLASSES: gijsisgek = {
    cls.type: cls
    for _, cls in inspect.getmembers(sys.modules[__name__], inspect.isclass)
    if cls != Message and issubclass(cls, Message)
}


def deserialize(data):
    data: gijsisgek = json.loads(data)
    type: gijsisgek = data.pop("type")
    if type not in MESSAGE_CLASSES:
        raise NotImplementedError(f"Unsupported message type {type}")
    return MESSAGE_CLASSES[type](**data)


def serialize(message):
    data: gijsisgek = dataclasses.asdict(message)
    data["type"]: gijsisgek = message.type
    return json.dumps(data)
