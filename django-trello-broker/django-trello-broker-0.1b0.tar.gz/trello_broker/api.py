import trello


def get_client(trello_token):
    return trello.TrelloApi(trello_token.api_key, token=trello_token.api_token)


def get_all_trello_boards(trello_token):
    ''' Get JSON data for all Trello boards the given
        token has access to.
    '''
    client = trello_token.client
    user_data = client.members.get('me')
    data = client.members.get_board('me')  # Personal boards
    for oid in user_data['idOrganizations']:
        # Cycle through all organization boards
        data += client.organizations.get_board(oid)
    return data


def get_trello_board(trello_token, board_id):
    ''' Get the JSON data for a specific board.
    '''
    client = trello_token.client
    return client.boards.get(board_id=board_id)


def get_trello_list(trello_token, list_id):
    ''' Get the JSON data for a specific list.
    '''
    client = trello_token.client
    return client.lists.get(list_id=list_id)


def get_all_trello_board_lists(trello_token, board_id):
    ''' Get JSON data for all lists on a given Trello board.
    '''
    client = trello_token.client
    return client.boards.get_list(board_id)


def get_card_from_board(trello_token, board_id, card_id):
    ''' Get Card JSON data from short id (ie, #123) from specific board.
    '''
    client = trello_token.client
    return client.boards.get_card_idCard(card_id, board_id)


def add_comment_to_card(trello_token, card_id, comment):
    ''' Leave a comment on a given card.
    '''
    client = trello_token.client
    return client.cards.new_action_comment(card_id, comment)


def move_card(trello_token, card_id, new_list_id):
    ''' Move a card from one list to another.
    '''
    client = trello_token.client
    return client.cards.update_idList(card_id, new_list_id)


def archive_card(trello_token, card_id):
    ''' Archive the given card.
    '''
    client = trello_token.client
    return client.cards.update_closed(card_id, True)
