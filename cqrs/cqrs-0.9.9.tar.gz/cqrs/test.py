from libtng import cqrs


class TestCommand1(cqrs.Command):
    pass


@TestCommand1.handler
class TestCommandHandler1(cqrs.CommandHandler):
    pass


class TestCommand2(cqrs.Command):
    pass


@TestCommand2.handler
class TestCommandHandler2(cqrs.CommandHandler):
    pass

