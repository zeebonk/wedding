import asyncio
import random

import messages


COLORS = (  # https://visme.co/blog/wp-content/uploads/2016/09/website.jpg
    "#e6194B",
    "#f58231",
    "#ffe119",
    "#bfef45",
    "#3cb44b",
    "#42d4f4",
    "#4363d8",
    "#f032e6",
    "#a9a9a9",
    "#000000",
    "#ffffff",
)


class Stage:
    def __init__(self, server, users, round):
        self.server = server
        self.users = set(users)
        self.round = round

    async def start(self):
        pass

    async def on_auth_code(self, user, message):
        code = await self.server.pg_conn.fetchval(
            'SELECT code FROM public."Image" WHERE code = $1;', message.code
        )

        if message.code == 9999:
            self.server.reset()
            await self.server.next_stage()
            await self.server.send_many(messages.Reset(), self.users)
        elif not code:
            await self.server.send(user, messages.AuthCodeInvalid())
            await self.on_auth_code_invalid(user, message)
        else:
            await self.server.send(user, messages.AuthCodeOk())
            await self.on_auth_code_ok(user, message)

    async def on_auth_code_ok(self, user, message):
        pass

    async def on_auth_code_invalid(self, user, message):
        pass

    async def on_question_answers(self, user, message):
        user.age = message.age
        user.name = message.name
        await self.on_questions_answered(user, message)

    async def on_questions_answered(self, user, message):
        pass


class Init(Stage):
    def __init__(self):
        self.users = set()


class CountingDown(Stage):
    async def start(self):
        self.count = 5
        asyncio.create_task(self.count_down())

    async def on_disconnect(self, user):
        self.users.discard(user)

    async def on_questions_answered(self, user, message):
        self.users.add(user)
        await self.server.send(user, messages.Countdown(self.count, self.round))

    async def count_down(self):
        for i in range(5, 0, -1):
            self.count = i
            await self.server.send_many(messages.Countdown(i, self.round), self.users)
            await asyncio.sleep(1)
        await self.server.next_stage(next_round=True)


class Success(Stage):
    async def start(self):
        await self.server.send_many(messages.ShowSuccess(round=self.round), self.users)
        asyncio.create_task(self.go_to_next_stage())

    async def on_disconnect(self, user):
        self.users.discard(user)

    async def on_questions_answered(self, user, message):
        self.users.add(user)

    async def go_to_next_stage(self):
        await asyncio.sleep(2)
        await self.server.next_stage()


class TellAboutYourself(Stage):
    async def start(self):
        self.users_to_answer = set(self.users)
        self.users_answered = set()

    async def on_disconnect(self, user):
        self.users.discard(user)
        self.users_to_answer.discard(user)
        self.users_answered.discard(user)
        await self.send_lobby_count()

    async def on_auth_code_ok(self, user, message):
        self.users.add(user)
        self.users_to_answer.add(user)
        await self.send_lobby_count()

    async def on_auth_code_invalid(self, user, message):
        if message.code == 9998:
            await self.server.next_stage()

    async def on_questions_answered(self, user, message):
        self.users_to_answer.discard(user)
        self.users_answered.add(user)
        await self.send_lobby_count()

    async def send_lobby_count(self):
        await self.server.send_many(
            messages.LobbyCount(
                connected=len(self.users), done=len(self.users_answered),
            ),
            self.users_answered,
        )


class Groups:
    def __init__(self, group_names):
        self._groups = {name: set() for name in group_names}
        self._done = set()

    def add_user_to_random_group(self, user):
        group = random.choice(list(self._groups.keys()))
        self._groups[group].add(user)
        return group

    def remove_user(self, user):
        for users in self._groups.values():
            users.discard(user)

    def group(self, user):
        for group, users in self._groups.items():
            if user in users:
                return group
        raise Exception(f"{user} not in any group")

    def users(self, group):
        return self._groups[group]

    def non_empty(self):
        return [group for group, users in self._groups.items() if users]

    def done(self):
        return [
            group
            for group, users in self._groups.items()
            if users and group in self._done
        ]

    def done_users(self):
        done_users = set()
        for group in self._done:
            done_users |= self.users(group)
        return done_users

    def mark_done(self, group):
        self._done.add(group)


class FindingGroup(Stage):
    async def start(self):
        self.groups = Groups(random.sample(COLORS, 2))

        send_tasks = []
        for user in self.users:
            group = self.groups.add_user_to_random_group(user)
            send_tasks.append(
                self.server.send(user, messages.ShowCountCode(color=group))
            )

        await asyncio.gather(*send_tasks)

    async def on_questions_answered(self, user, message):
        self.users.add(user)
        group = self.groups.add_user_to_random_group(user)
        await self.server.send(user, messages.ShowCountCode(color=group))
        await self.check_group_progress()

    async def on_count_code(self, user, message):
        group = self.groups.group(user)
        users = self.groups.users(group)

        if message.code == len(users):
            # Code guessed correctly
            self.groups.mark_done(group)
            await self.check_group_progress()
        else:
            await self.server.send(user, messages.CountCodeInvalid())

    async def on_disconnect(self, user):
        self.users.discard(user)
        self.groups.remove_user(user)
        await self.check_group_progress()

    async def check_group_progress(self):
        n_groups_done = len(self.groups.done())
        n_groups_non_empty = len(self.groups.non_empty())

        if n_groups_done == n_groups_non_empty:
            # All groups finished
            await self.server.next_stage()
        else:
            # Not all groups finished, update finished users with progress
            await self.server.send_many(
                messages.WaitForGroups(done=n_groups_done, total=n_groups_non_empty),
                self.groups.done_users(),
            )


class TotalAge(Stage):
    async def start(self):
        self.groups = Groups(random.sample(COLORS, 8))

        send_tasks = []
        for user in self.users:
            group = self.groups.add_user_to_random_group(user)
            send_tasks.append(
                self.server.send(user, messages.ShowTotalAge(color=group))
            )

        await asyncio.gather(*send_tasks)

    async def on_questions_answered(self, user, message):
        self.users.add(user)
        group = self.groups.add_user_to_random_group(user)
        await self.server.send(user, messages.ShowTotalAge(color=group))
        await self.check_group_progress()

    async def on_total_age(self, user, message):
        group = self.groups.group(user)
        users = self.groups.users(group)

        if message.code == sum(u.age for u in users):
            # Code guessed correctly
            self.groups.mark_done(group)
            await self.check_group_progress()
        else:
            await self.server.send(user, messages.TotalAgeInvalid())

    async def on_disconnect(self, user):
        self.users.discard(user)
        self.groups.remove_user(user)
        await self.check_group_progress()

    async def check_group_progress(self):
        n_groups_done = len(self.groups.done())
        n_groups_non_empty = len(self.groups.non_empty())

        if n_groups_done == n_groups_non_empty:
            # All groups finished
            await self.server.next_stage()
        else:
            # Not all groups finished, update finished users with progress
            await self.server.send_many(
                messages.WaitForGroups(done=n_groups_done, total=n_groups_non_empty),
                self.groups.done_users(),
            )
