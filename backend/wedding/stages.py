import asyncio
import logging
import random

from wedding import common, messages


LOGGER = logging.getLogger(__name__)


class Stage:
    def __init__(
        self, server, users, round,  # pylint: disable=redefined-builtin
    ):
        self.server = server
        self.users = set(users)
        self.round = round

    async def start(self):
        pass

    async def on_auth_code(self, user, message):
        async with self.server.pg_pool.acquire() as conn:
            code = await conn.fetchval(
                'SELECT code FROM public."Image" WHERE code = $1;', message.code
            )
        if code:
            user.code = code
            await self.server.send(user, messages.AuthCodeOk())
        else:
            await self.server.send(user, messages.AuthCodeInvalid())

    async def on_disconnect(self, user):
        pass

    async def on_connect(self, user):
        await self.server.send(user, messages.ShowAuthCode())

    async def on_question_answers(self, user, message):
        user.age = int(message.age)
        user.name = message.name.strip().lower()
        await self.on_questions_answered(user, message)

    async def on_questions_answered(self, user, message):
        pass

    async def on_code(self, user, message):
        pass


class Init(Stage):
    def __init__(self):
        super().__init__(None, set(), None)


class Teaser(Stage):
    async def on_connect(self, user):
        await self.server.send(user, messages.ShowTeaser())


class CountingDown(Stage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.count = 5

    async def start(self):
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
        await self.server.send(user, messages.ShowSuccess(round=self.round))

    async def go_to_next_stage(self):
        await asyncio.sleep(4)
        await self.server.next_stage()


class TellAboutYourself(Stage):
    async def start(self):
        await self.server.send_many(messages.ShowAuthCode(), self.server.connections)

    async def on_connect(self, user):
        await self.server.send(user, messages.ShowAuthCode())

    async def on_disconnect(self, user):
        self.users.discard(user)
        await self.send_lobby_count()

    async def on_questions_answered(self, user, message):
        self.users.add(user)
        await self.send_lobby_count()

    async def send_lobby_count(self):
        await self.server.send_many(
            messages.LobbyCount(
                connected=len(self.server.connections), done=len(self.users),
            ),
            self.users,
        )


class Group:
    def __init__(self, name):
        self.name = name
        self._all = set()
        self._done = set()

    def add(self, user):
        self._all.add(user)

    def remove(self, user):
        self._all.discard(user)
        self._done.discard(user)

    def contains(self, user):
        return user in self._all

    def mark_done(self, user):
        if user in self._all:
            self._done.add(user)

    def mark_all_done(self):
        self._done = set(self._all)

    def users(self):
        return set(self._all)

    def done_users(self):
        return set(self._done)

    @property
    def empty(self):
        return len(self._all) == 0

    @property
    def done(self):
        return not self.empty and len(self._done) == len(self._all)


class GroupManager:
    def __init__(self, groups):
        self._groups = list(groups)
        self._user_group_mapping = {}
        self._random_group_generator = common.fair_random_generator(self._groups)

    def all(self):
        return [g for g in self._groups if not g.empty]

    def done(self):
        return [g for g in self._groups if g.done]

    def add_user_to_random_group(self, user):
        group = next(self._random_group_generator)
        self.add_user_to_group(user, group)
        return group

    def add_user_to_group(self, user, group):
        self._user_group_mapping[user] = group
        group.add(user)

    def get_group_by_user(self, user):
        return self._user_group_mapping.get(user)

    def remove_user(self, user):
        if group := self._user_group_mapping.get(user):
            group.remove(user)
            self._user_group_mapping.pop(user)


class GroupGame(Stage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.groups = None

    def assign_user_to_group(self, user):
        return self.groups.add_user_to_random_group(user)

    async def start(self):
        self.groups = await self.create_groups()

        tasks = []
        for user in self.users:
            group = self.assign_user_to_group(user)
            tasks.append((user, group.name))

        await asyncio.gather(
            *(
                self.server.send(user, self.show_message(color=group_name))
                for user, group_name in tasks
            )
        )

    async def on_questions_answered(self, user, message):
        self.users.add(user)
        group = self.assign_user_to_group(user)
        await self.server.send(user, self.show_message(color=group.name))
        await self.check_group_progress()

    async def on_disconnect(self, user):
        self.users.discard(user)
        self.groups.remove_user(user)
        await self.check_group_progress()

    async def check_group_progress(self):
        n_groups = len(self.groups.all())
        n_groups_done = len(self.groups.done())

        if n_groups_done == n_groups:
            # All groups finished
            await self.server.next_stage()
        else:
            # Not all groups finished, update finished users with progress
            for group in self.groups.all():
                if group.done:
                    await self.server.send_many(
                        messages.WaitForGroups(done=n_groups_done, total=n_groups),
                        group.users(),
                    )
                else:
                    n_users = len(group.users())
                    done_users = group.done_users()
                    n_done_users = len(done_users)
                    await self.server.send_many(
                        messages.TeamProgress(n_users, n_done_users), done_users
                    )

    def show_message(self, color):
        raise NotImplementedError()

    async def create_groups(self):
        raise NotImplementedError()


class NameOrder(GroupGame):
    async def create_groups(self):
        return GroupManager(Group(color) for color in random.sample(common.COLORS, 2))

    async def on_code(self, user, message):
        await super().on_code(user, message)

        group = self.groups.get_group_by_user(user)

        # Get the other users in the group that come after the current user
        # when users are sorted by name
        users_after = (u for u in group.users() if u.name > user.name)
        users_after = sorted(users_after, key=lambda u: u.name)

        if users_after:
            # Get the code of the next user in the list, and all following users
            # that might have the same name.
            acceptable_codes = {
                u.code for u in users_after if u.name == users_after[0].name
            }
        else:
            # If no codes have been found, it's the last user in the list and 0 is
            # considered as an acceptable answer
            acceptable_codes = {"0"}

        if message.code in acceptable_codes:
            group.mark_done(user)
            await self.check_group_progress()
        else:
            await self.server.send(user, messages.NameOrderInvalid())

    def show_message(self, color):
        return messages.ShowNameOrder(color)


class TotalAge(GroupGame):
    async def create_groups(self):
        return GroupManager(Group(color) for color in random.sample(common.COLORS, 8))

    async def on_code(self, user, message):
        await super().on_code(user, message)
        group = self.groups.get_group_by_user(user)
        answer = common.parse_int(message.code)

        if answer == sum(u.age for u in group.users()):
            group.mark_all_done()
            await self.check_group_progress()
        else:
            await self.server.send(user, messages.TotalAgeInvalid())

    def show_message(self, color):
        return messages.ShowTotalAge(color)


class FindingGroup(GroupGame):
    async def create_groups(self):
        return GroupManager(Group(color) for color in random.sample(common.COLORS, 12))

    async def on_code(self, user, message):
        await super().on_code(user, message)
        group = self.groups.get_group_by_user(user)
        answer = common.parse_int(message.code)

        if answer == len(group.users()):
            group.mark_all_done()
            await self.check_group_progress()
        else:
            await self.server.send(user, messages.CountCodeInvalid())

    def show_message(self, color):
        return messages.ShowCountCode(color)


class SlowDance(GroupGame):
    async def create_groups(self):
        async with self.server.pg_pool.acquire() as conn:
            raw_pairs = await conn.fetch(
                """
                SELECT
                    code AS code_a,
                    other AS code_b
                FROM
                    public."Image"
                """
            )
        active_codes = set(u.code for u in self.users)
        active_pairs = set()
        for code_a, code_b in raw_pairs:
            if code_a not in active_codes or code_b not in active_codes:
                continue  # Will be put in a "loners" group
            pair = tuple(sorted((code_a, code_b)))
            active_pairs.add(pair)

        color_gen = iter(common.COLORS)
        self.loner_group = Group(next(color_gen))
        self.code_to_group_map = {}
        groups = [self.loner_group]
        for code_a, code_b in active_pairs:
            group = Group(next(color_gen))
            self.code_to_group_map[code_a] = group
            self.code_to_group_map[code_b] = group
            groups.append(group)

        return GroupManager(groups)

    def assign_user_to_group(self, user):
        group = self.code_to_group_map.get(user.code, self.loner_group)
        self.groups.add_user_to_group(user, group)
        return group

    async def on_code(self, user, message):
        await super().on_code(user, message)
        group = self.groups.get_group_by_user(user)

        other_codes = set(u.code for u in group.users() if u != user)

        if message.code in other_codes:
            group.mark_done(user)
            await self.check_group_progress()
        else:
            await self.server.send(user, messages.SlowDanceCodeInvalid())

    def show_message(self, color):
        return messages.ShowSlowDance(color)


class TheEnd(Stage):
    async def start(self):
        await self.server.send_many(messages.ShowTheEnd(), self.users)

    async def on_disconnect(self, user):
        self.users.discard(user)

    async def on_questions_answered(self, user, message):
        self.users.add(user)
        await self.server.send(user, messages.ShowTheEnd())
