import asyncio
import dataclasses
import logging
import typing

import coolname
import websockets

from wedding import messages, stages


LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass(unsafe_hash=True)
class User:
    id: str
    socket: typing.Any = dataclasses.field(compare=False, repr=False)

    name: str = dataclasses.field(init=False, compare=False, repr=False)
    age: int = dataclasses.field(init=False, compare=False, repr=False)
    code: int = dataclasses.field(init=False, compare=False, repr=False)

    group: typing.Any = dataclasses.field(
        init=False, compare=False, repr=False, default=None
    )


class Server:
    def __init__(self, pg_conn, next_stage_code, reset_code):
        self.pg_conn = pg_conn
        self.next_stage_code = next_stage_code
        self.reset_code = reset_code
        self.stage = None
        self.round = 0
        self.connections = set()
        self.reset()

    def reset(self):
        self.stage = stages.Init()
        self.round = 0
        self.stages = iter(
            (
                stages.Teaser,
                stages.TellAboutYourself,
                stages.CountingDown,
                stages.FindingGroup,
                stages.Success,
                stages.CountingDown,
                stages.TotalAge,
                stages.Success,
                stages.CountingDown,
                stages.NameOrder,
                stages.Success,
                stages.CountingDown,
                stages.SlowDance,
                stages.TheEnd,
            )
        )

    async def next_stage(self, next_round=False):
        if next_round:
            self.round += 1

        stage_class = next(self.stages, None)
        if stage_class:
            LOGGER.info(
                "Switching from %s to %s",
                self.stage.__class__.__name__,
                stage_class.__name__,
            )
            self.stage = stage_class(self, self.stage.users, self.round)
            await self.stage.start()
        else:
            LOGGER.info("No more stages left")

    async def serve(self, socket, path):
        user = User(coolname.generate_slug(2), socket)
        LOGGER.info("%s connected", user)

        self.connections.add(user)
        await self.stage.on_connect(user)

        while True:
            try:
                data = await user.socket.recv()
            except (
                websockets.exceptions.ConnectionClosedError,
                websockets.exceptions.ConnectionClosedOK,
            ) as e:
                LOGGER.info("%s closed connection (%s)", user, e)
                self.connections.discard(user)
                await self.stage.on_disconnect(user)
                break

            message = messages.deserialize(data)
            LOGGER.info("Received %s from %s", message, user)

            if isinstance(message, messages.AuthCode):
                await self.stage.on_auth_code(user, message)
            elif isinstance(message, messages.QuestionAnswers):
                await self.stage.on_question_answers(user, message)
            elif isinstance(message, messages.Code):
                if message.code == self.reset_code:
                    self.reset()
                    await self.next_stage()
                    await asyncio.gather(*(u.socket.close() for u in self.connections))
                elif message.code == self.next_stage_code:
                    await self.next_stage()
                else:
                    await self.stage.on_code(user, message)
            else:
                raise NotImplementedError(f"Unsupported message {message}")

    async def send(self, user, message):
        await self.send_many(message, [user])

    async def send_many(self, message, users):
        sockets = [u.socket for u in users if u.socket.open]
        LOGGER.info(
            "Sending %s to %s", message, ", ".join(str(u) for u in users) or "Nobody"
        )
        if sockets:
            data = messages.serialize(message)
            await asyncio.gather(*(s.send(data) for s in sockets))
