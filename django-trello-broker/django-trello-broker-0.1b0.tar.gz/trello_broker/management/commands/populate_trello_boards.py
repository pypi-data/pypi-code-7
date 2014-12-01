from django.core.management.base import BaseCommand
from trello_broker import api
from trello_broker.models import TrelloToken, TrelloBoard


class Command(BaseCommand):
    help = (
        'Cycle through all Trello tokens and populate '
        'all Trello Boards and Lists'
    )

    def handle(self, *args, **options):
        for token in TrelloToken.objects.all():
            print('Processing token {0}'.format(token.name))
            boards = api.get_all_trello_boards(token)
            for board in boards:
                print('Processing board {0}'.format(board['name']))
                _board = \
                    TrelloBoard.objects.filter(trello_id=board['id']).first()
                if _board:
                    _board.update_from_json(json_data=board)
                else:
                    _board = TrelloBoard.objects.create(
                        trello_token=token,
                        name=board['name'],
                        status=int(board['closed']),
                        trello_id=board['id'],
                    )

                _board.populate_all_lists()
