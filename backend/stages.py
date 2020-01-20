import asyncio
import random

import messages


COLORS = (
    ("#FC766AFF", "#5B84B1FF"),
    ("#5F4B8BFF", "#E69A8DFF"),
    ("#42EADDFF", "#CDB599FF"),
    ("#000000FF", "#FFFFFFFF"),
    ("#00A4CCFF", "#F95700FF"),
    ("#00203FFF", "#ADEFD1FF"),
    ("#606060FF", "#D6ED17FF"),
    ("#ED2B33FF", "#D85A7FFF"),
    ("#2C5F2D", "#97BC62FF"),
    ("#00539CFF", "#EEA47FFF"),
    ("#0063B2FF", "#9CC3D5FF"),
    ("#D198C5FF", "#E0C568FF"),
    ("#101820FF", "#FEE715FF"),
    ("#CBCE91FF", "#EA738DFF"),
    ("#B1624EFF", "#5CC8D7FF"),
    ("#89ABE3FF", "#FCF6F5FF"),
    ("#E3CD81FF", "#B1B3B3FF"),
    ("#101820FF", "#F2AA4CFF"),
    ("#A07855FF", "#D4B996FF"),
    ("#195190FF", "#A2A2A1FF"),
    ("#603F83FF", "#C7D3D4FF"),
    ("#2BAE66FF", "#FCF6F5FF"),
    ("#FAD0C9FF", "#6E6E6DFF"),
    ("#2D2926FF", "#E94B3CFF"),
    ("#DAA03DFF", "#616247FF"),
    ("#990011FF", "#FCF6F5FF"),
    ("#435E55FF", "#D64161FF"),
    ("#CBCE91FF", "#76528BFF"),
    ("#FAEBEFFF", "#333D79FF"),
    ("#F93822FF", "#FDD20EFF"),
    ("#F2EDD7FF", "#755139FF"),
    ("#006B38FF", "#101820FF"),
    ("#F95700FF", "#FFFFFFFF"),
    ("#FFD662FF", "#00539CFF"),
    ("#D7C49EFF", "#343148FF"),
    ("#FFA177FF", "#F5C7B8FF"),
    ("#DF6589FF", "#3C1053FF"),
    ("#FFE77AFF", "#2C5F2DFF"),
    ("#DD4132FF", "#9E1030FF"),
    ("#F1F4FFFF", "#A2A2A1FF"),
    ("#FCF951FF", "#422057FF"),
    ("#4B878BFF", "#D01C1FFF"),
    ("#1C1C1BFF", "#CE4A7EFF"),
    ("#00B1D2FF", "#FDDB27FF"),
    ("#79C000FF", "#FF7F41FF"),
    ("#BD7F37FF", "#A13941FF"),
    ("#E3C9CEFF", "#9FC131FF"),
    ("#00239CFF", "#E10600FF"),
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
            user.code = code
            await self.server.send(user, messages.AuthCodeOk())
            await self.on_auth_code_ok(user, message)

    async def on_connect(self, user):
        await self.server.send(user, messages.ShowAuthCode())

    async def on_auth_code_ok(self, user, message):
        pass

    async def on_auth_code_invalid(self, user, message):
        pass

    async def on_question_answers(self, user, message):
        user.age = message.age
        user.name = message.name.strip().lower()
        await self.on_questions_answered(user, message)

    async def on_questions_answered(self, user, message):
        pass


class Init(Stage):
    def __init__(self):
        self.users = set()


class Teaser(Stage):
    async def start(self):
        self.connections = set()

    async def on_auth_code_invalid(self, user, message):
        if message.code == 9998:
            await self.server.send_many(messages.ShowAuthCode(), self.connections)
            await self.server.next_stage()

    async def on_connect(self, user):
        self.connections.add(user)
        await self.server.send(user, messages.ShowTeaser())

    async def on_disconnect(self, user):
        self.connections.discard(user)


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
        await self.server.send(user, messages.ShowSuccess(round=self.round))

    async def go_to_next_stage(self):
        await asyncio.sleep(4)
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


def fair_random_generator(items):
    for i in range(2):
        for item in items:
            yield item
    while True:
        yield random.choice(items)


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
        self._random_group_generator = fair_random_generator(self._groups)

    def all(self):
        return [g for g in self._groups if not g.empty]

    def done(self):
        return [g for g in self._groups if g.done]

    def add_user_to_random_group(self, user):
        group = next(self._random_group_generator)
        self._user_group_mapping[user] = group
        group.add(user)
        return group

    def get_group_by_user(self, user):
        return self._user_group_mapping.get(user)

    def remove_user(self, user):
        group = self._user_group_mapping.get(user)
        if group:
            group.remove(user)
            self._user_group_mapping.pop(user)


class BaseAwesome(Stage):
    async def start(self):
        self.groups = GroupManager(Group(color) for color in random.sample(COLORS, 2))

        send_tasks = []
        for user in self.users:
            group = self.groups.add_user_to_random_group(user)
            send_tasks.append(
                self.server.send(user, self.show_message(color=group.name))
            )
        await asyncio.gather(*send_tasks)

    async def on_questions_answered(self, user, message):
        self.users.add(user)
        group = self.groups.add_user_to_random_group(user)
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


class NameOrder(BaseAwesome):
    show_message = messages.ShowNameOrder

    async def on_name_order(self, user, message):
        # Get the codes of the users coming after the current user when ordered
        # alphabetically. Users with the same name will both be accepted. The
        # last user can enter 0.
        group = self.groups.get_group_by_user(user)
        users = (u for u in group.users() if u.name > user.name)
        users = sorted(users, key=lambda u: u.name)
        oks = set()
        if not users:
            oks.add(0)
        else:
            next_user = users[0]
            oks.add(next_user.code)
            for user in users[1:]:
                if user.name != next_user.name:
                    break
                oks.add(user.code)

        # Check if user gussed correctly:
        if message.code in oks:
            # Code guessed correctly
            group.mark_done(user)
            await self.check_group_progress()
        else:
            await self.server.send(user, messages.NameOrderInvalid())


class TotalAge(BaseAwesome):
    show_message = messages.ShowTotalAge

    async def on_total_age(self, user, message):
        group = self.groups.get_group_by_user(user)

        if message.code == sum(u.age for u in group.users()):
            # Code guessed correctly
            group.mark_all_done()
            await self.check_group_progress()
        else:
            await self.server.send(user, messages.TotalAgeInvalid())


class FindingGroup(BaseAwesome):
    show_message = messages.ShowCountCode

    async def on_count_code(self, user, message):
        group = self.groups.get_group_by_user(user)

        if message.code == len(group.users()):
            # Code guessed correctly
            group.mark_all_done()
            await self.check_group_progress()
        else:
            await self.server.send(user, messages.CountCodeInvalid())
