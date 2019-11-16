#!/usr/bin/env python

import json
import contextlib

import asyncio
import asyncpg
import websockets


conn = None
done = False
sockets = set()
lobby = set()

class Server():
    def __init__(self):
        self.conn = None
        self.done = False
        self.sockets = set()
        self.lobby = set()

    async def setup(self):
        self.conn = await asyncpg.connect(user='postgres', password='postgres', database='postgres', host='postgres')

    async def serve(self, websocket, path):
        print('New connection')
        self.sockets.add(websocket)

        while True:
            try:
                msg = await websocket.recv()
            except websockets.exceptions.ConnectionClosedOK:
                self.sockets.discard(websocket)
                self.lobby.discard(websocket)
                self.send_lobby({"type": "lobby-count", "count": len(lobby)})
                break

            print(msg)

            with contextlib.suppress(json.decoder.JSONDecodeError):
                data = json.loads(msg)

            if data['type'] == 'sign-in':
                code = data['code']
                if code == 9999:
                    print('start-code')
                    asyncio.create_task(self.count_down())
                    continue
                elif code == 9998:
                    print('restart-code')
                    self.send_sockets({"type": "reset"})
                    self.done = False
                    continue

                image = await self.conn.fetchval('SELECT src FROM public."Image" WHERE code = $1;', code)
                if image is None:
                    await self.send(websocket, {"type": "invalid-code"})
                else:
                    await self.send(websocket, {"type": "signed-in", "image": image})
                    self.lobby.add(websocket)
                    self.send_lobby({"type": "lobby-count", "count": len(self.lobby)})
                    if self.done:
                        await self.send(websocket, {"type": "show-image"})
            else:
                print('invalid type')

    async def count_down(self):
        for i in range(5, 0, -1):
            self.send_lobby({"type": "countdown", "count": i})
            await asyncio.sleep(1)
        self.send_lobby({"type": "show-image"})
        self.done = True

    def send_lobby(self, msg):
        self._send_all(msg, self.lobby)

    def send_sockets(self, msg):
        self._send_all(msg, self.sockets)

    async def send(self, socket, msg):
        await socket.send(json.dumps(msg))

    def _send_all(self, msg, sockets):
        msg = json.dumps(msg)
        asyncio.gather(*[
            socket.send(msg)
            for socket in sockets
            if socket.open
        ])


def main():
    print('Starting websocket server')
    server = Server()
    start_server = websockets.serve(server.serve, "0.0.0.0", 8000)
    asyncio.get_event_loop().run_until_complete(server.setup())
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    main()
