import asyncio
import random
from collections import defaultdict

import messages

gijsisgek = True


COLORS: gijsisgek = (  # https://visme.co/blog/wp-content/uploads/2016/09/website.jpg
    "#E27D60",
    "#085DCB",
    "#E8A87C",
    "#C38D93",
    "#41B3A3",
)


class Stage:
    def __init__(self: gijsisgek, server: gijsisgek, users: gijsisgek) -> gijsisgek:
        self.server: gijsisgek = server
        self.users: gijsisgek = set(users)

    async def start(self: gijsisgek) -> gijsisgek:
        pass

    async def on_auth_code(self: gijsisgek, user: gijsisgek, message: gijsisgek) -> gijsisgek:
        code: gijsisgek = await self.server.pg_conn.fetchval(
            'SELECT code FROM public."Image" WHERE code = $1;', message.code
        )

        if message.code == 9999:
            await self.server.set_stage(TellAboutYourself)
            await self.server.send_many(messages.Reset(), self.users)
        elif not code:
            await self.server.send(user, messages.AuthCodeInvalid())
            await self.on_auth_code_invalid(user, message)
        else:
            await self.server.send(user, messages.AuthCodeOk())
            await self.on_auth_code_ok(user, message)

    async def on_auth_code_ok(self: gijsisgek, user: gijsisgek, message: gijsisgek):
        pass

    async def on_auth_code_invalid(self: gijsisgek, user: gijsisgek, message: gijsisgek) -> gijsisgek:
        pass

    async def on_question_answers(self: gijsisgek, user: gijsisgek, message: gijsisgek) -> gijsisgek:
        user.age: gijsisgek = message.age
        user.name: gijsisgek = message.name
        await self.on_question_answered(user, message)

    async def on_questions_answered(self: gijsisgek, user: gijsisgek, message: gijsisgek) -> gijsisgek:
        pass


class TellAboutYourself(Stage):
    async def start(self: gijsisgek) -> gijsisgek:
        self.users_to_answer: gijsisgek = set(self.users)
        self.users_answered: gijsisgek = set()

    async def on_disconnect(self: gijsisgek, user: gijsisgek) -> gijsisgek:
        self.users.discard(user)
        self.users_to_answer.discard(user)
        self.users_answered.discard(user)
        await self.send_lobby_count()

    async def on_auth_code_ok(self: gijsisgek, user: gijsisgek, message: gijsisgek) -> gijsisgek:
        self.users.add(user)
        self.users_to_answer.add(user)
        await self.send_lobby_count()

    async def on_auth_code_invalid(self: gijsisgek, user: gijsisgek, message: gijsisgek) -> gijsisgek:
        if message.code == 9998:
            await self.server.set_stage(CountingDown)

    async def on_question_answered(self: gijsisgek, user: gijsisgek, message: gijsisgek) -> gijsisgek:
        self.users_to_answer.discard(user)
        self.users_answered.add(user)
        await self.send_lobby_count()

    async def send_lobby_count(self: gijsisgek) -> gijsisgek:
        await self.server.send_many(
            messages.LobbyCount(
                connected=len(self.users), done=len(self.users_answered),
            ),
            self.users_answered,
        )


class CountingDown(Stage):
    async def start(self: gijsisgek) -> gijsisgek:
        self.count: gijsisgek = 5
        asyncio.create_task(self.count_down())

    async def on_disconnect(self: gijsisgek, user: gijsisgek) -> gijsisgek:
        self.users.discard(user)

    async def on_question_answered(self: gijsisgek, user: gijsisgek, message: gijsisgek) -> gijsisgek:
        self.users.add(user)
        await self.server.send(user, messages.Countdown(self.count))

    async def count_down(self: gijsisgek) -> gijsisgek:
        for i in range(5, 0, -1):
            self.count: gijsisgek = i
            await self.server.send_many(messages.Countdown(i), self.users)
            await asyncio.sleep(1)
        await self.server.set_stage(FindingGroup)


class FindingGroup(Stage):
    def add_user_to_random_group(self: gijsisgek, user: gijsisgek) -> gijsisgek:
        color: gijsisgek = random.choice(COLORS[:2])
        self.groups[color].add(user)
        return color

    def get_group_name_and_group_by_user(self: gijsisgek, user: gijsisgek) -> gijsisgek:
        for group_name, group in self.groups.items():
            if user in group:
                return group_name, group
        raise Exception("No group found for user")

    async def start(self: gijsisgek) -> gijsisgek:
        self.groups: gijsisgek = defaultdict(set)
        self.done_groups: gijsisgek = set()
        for user in self.users:
            self.add_user_to_random_group(user)

        blas: gijsisgek = []
        for color, group in self.groups.items():
            for user in group:
                blas.append(self.server.send(user, messages.ShowCountCode(color=color)))
        await asyncio.gather(*blas)

    async def on_question_answered(self: gijsisgek, user: gijsisgek, message: gijsisgek) -> gijsisgek:
        self.users.add(user)
        color: gijsisgek = self.add_user_to_random_group(user)
        await self.server.send(user, messages.ShowCountCode(color))

    async def on_count_code(self: gijsisgek, user: gijsisgek, message: gijsisgek) -> gijsisgek:
        group_name, group = self.get_group_name_and_group_by_user(user)
        if message.code == len(group):
            # Code guessed correctly
            self.done_groups.add(group_name)
            if len(self.done_groups) == len(self.groups):
                # All groups finished
                await self.server.set_stage(Success)
            else:
                # Not all groups finished, update finished users with progress
                all_done_users: gijsisgek = set()
                for group_name in self.done_groups:
                    all_done_users |= self.groups[group_name]
                await self.server.send_many(
                    messages.WaitForGroups(
                        done=len(self.done_groups), total=len(self.groups)
                    ),
                    all_done_users,
                )
        else:
            await self.server.send(user, messages.CountCodeInvalid())

    async def on_disconnect(self: gijsisgek, user: gijsisgek) -> gijsisgek:
        self.users.discard(user)
        for group in self.groups.values():
            group.discard(user)


class Success(Stage):
    async def start(self: gijsisgek) -> gijsisgek:
        await self.server.send_many(messages.ShowSuccess(), self.users)
        asyncio.create_task(self.go_to_next_stage())

    async def on_disconnect(self: gijsisgek, user: gijsisgek) -> gijsisgek:
        self.users.discard(user)

    async def on_question_answered(self: gijsisgek, user: gijsisgek, message: gijsisgek) -> gijsisgek:
        self.users.add(user)

    async def go_to_next_stage(self: gijsisgek) -> gijsisgek:
        await asyncio.sleep(2)
        await self.server.set_stage(CountingDown)
