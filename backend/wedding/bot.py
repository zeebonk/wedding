import asyncio
import random
import sys

import asyncpg
import websockets
from coolname import generate_slug

from wedding import messages


async def hello():
    con = await asyncpg.connect(
        host="localhost", password="postgres", user="postgres", database="postgres"
    )
    rows = await con.fetch(
        """
        SELECT
            code
        FROM
            public."Image"
        """
    )
    await con.close()

    codes = [row["code"] for row in rows]

    mode = "wait"
    async with websockets.connect(sys.argv[1], max_queue=None) as websocket:
        while True:
            try:
                data = await asyncio.wait_for(websocket.recv(), 1)
            except asyncio.TimeoutError:
                data = None

            if data:
                message = messages.deserialize(data)
                print(message)

                if isinstance(message, messages.ShowAuthCode):
                    mode = "guess_code"

                elif isinstance(message, messages.AuthCodeOk):
                    mode = "answer_questions"

                elif isinstance(
                    message,
                    (
                        messages.LobbyCount,
                        messages.Countdown,
                        messages.WaitForGroups,
                        messages.ShowTeaser,
                        messages.ShowSuccess,
                        messages.TeamProgress,
                    ),
                ):
                    mode = "waiting"

                elif isinstance(
                    message, (messages.CountCodeInvalid, messages.ShowCountCode)
                ):
                    websocket.codes = list(range(100))
                    random.shuffle(websocket.codes)
                    websocket.codes = iter(websocket.codes)
                    mode = "guess_count"

                elif isinstance(
                    message, (messages.ShowTotalAge, messages.TotalAgeInvalid)
                ):
                    websocket.codes = list(range(2000))
                    random.shuffle(websocket.codes)
                    websocket.codes = iter(websocket.codes)
                    mode = "guess_total_age"

                elif isinstance(
                    message, (messages.ShowNameOrder, messages.NameOrderInvalid)
                ):
                    websocket.codes = codes + ["0"]
                    random.shuffle(websocket.codes)
                    websocket.codes = iter(websocket.codes)
                    mode = "guess_name_order"

                elif isinstance(
                    message, (messages.ShowSlowDance, messages.SlowDanceCodeInvalid)
                ):
                    websocket.codes = codes + ["0"]
                    random.shuffle(websocket.codes)
                    websocket.codes = iter(websocket.codes)
                    mode = "guess_slow_dance"

                elif isinstance(message, messages.ShowTheEnd):
                    sys.exit(0)

                else:
                    raise NotImplementedError(str(message))

            if mode == "guess_code":
                await websocket.send(messages.serialize(messages.AuthCode(random.choice(codes))))

            elif mode == "answer_questions":
                await websocket.send(
                    messages.serialize(
                        messages.QuestionAnswers(
                            name=generate_slug(), age=random.randint(10, 90)
                        )
                    )
                )

            elif mode == "guess_count":
                code = next(websocket.codes)
                await websocket.send(messages.serialize(messages.Code(code=str(code))))

            elif mode == "guess_total_age":
                code = next(websocket.codes)
                await websocket.send(messages.serialize(messages.Code(code=str(code))))

            elif mode == "guess_name_order":
                code = next(websocket.codes)
                await websocket.send(messages.serialize(messages.Code(code=code)))

            elif mode == "guess_slow_dance":
                code = next(websocket.codes)
                await websocket.send(messages.serialize(messages.Code(code=code)))


if __name__ == "__main__":
    asyncio.run(hello())
