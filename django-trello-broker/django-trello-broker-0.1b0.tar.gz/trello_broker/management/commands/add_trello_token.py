import trello
from django.core.management.base import BaseCommand
from trello_broker.models import TrelloToken


class Command(BaseCommand):
    help = 'Add Trello App API Token to the trello_broker app'

    def handle(self, *args, **options):
        print('Enter your Trello applications name.\n')
        app_name = raw_input('App Name: ')
        print(
            '\nEnter your Trello user API Key. You can get it from:\n\n'
            'https://trello.com/1/appKey/generate\n'
        )
        api_key = raw_input('API Key: ')
        client = trello.TrelloApi(api_key)
        url = client.get_token_url(app_name, expires='never')
        print(
            '\nGo to the following URL to get your API Token:\n\n'
            '{0}\n'.format(url)
        )
        api_token = raw_input('API Token: ')
        token = TrelloToken.objects.create(
            name=app_name,
            api_key=api_key,
            api_token=api_token,
        )
        print('Saved token (ID: {0}) to the database.'.format(token.pk))
