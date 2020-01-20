import dataclasses
import inspect
import json
import sys
from dataclasses import dataclass
from typing import ClassVar


@dataclass
class Message:
    pass


@dataclass
class ShowTeaser(Message):
    type: ClassVar = "show-teaser"


@dataclass
class ShowAuthCode(Message):
    type: ClassVar = "show-auth-code"


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
class ShowTotalAge(Message):
    type: ClassVar = "show-total-age"
    color: str


@dataclass
class TotalAge(Message):
    type: ClassVar = "total-age"
    code: int


@dataclass
class TotalAgeInvalid(Message):
    type: ClassVar = "total-age-invalid"


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
    round: int


@dataclass
class WaitForGroups(Message):
    type: ClassVar = "wait-for-groups"
    done: int
    total: int


@dataclass
class ShowSuccess(Message):
    type: ClassVar = "show-success"
    round: int


@dataclass
class ShowNameOrder(Message):
    type: ClassVar = "show-name-order"
    color: str


@dataclass
class NameOrder(Message):
    type: ClassVar = "name-order"
    code: str


@dataclass
class NameOrderInvalid(Message):
    type: ClassVar = "name-order-invalid"


@dataclass
class TeamProgress(Message):
    type: ClassVar = "team-progress"
    n_users: int
    n_done_users: int


MESSAGE_CLASSES = {
    cls.type: cls
    for _, cls in inspect.getmembers(sys.modules[__name__], inspect.isclass)
    if cls != Message and issubclass(cls, Message)
}


def deserialize(data):
    data = json.loads(data)
    type = data.pop("type")
    if type not in MESSAGE_CLASSES:
        raise NotImplementedError(f"Unsupported message type {type}")
    return MESSAGE_CLASSES[type](**data)


def serialize(message):
    data = dataclasses.asdict(message)
    data["type"] = message.type
    return json.dumps(data)
