import re
from urlparse import urljoin
from django.template.loader import render_to_string
from . import api


# Based on pattern from https://bitbucket.org/sntran/trello-broker
re_pattern = re.compile(r'''
    (               # start capturing the verb
    fix             # contains 'fix'
    | close         # or 'close'
    |               # or just to reference
    )               # end capturing the verb
    e?              # maybe followed by 'e'
    (?:s|d)?        # or 's' or 'd', not capturing
    \s              # then a white space
    [#]             # and '#' to indicate the card
    ([0-9]+)        # with the card's short id.
    ''',
    re.VERBOSE | re.IGNORECASE,
)


def process_commits(repo, json_data):
    ''' Function to parse commit messages and act on
        BitBucketRule sets.
    '''
    base_repo_url = u'{0}{1}'.format(
        json_data['canon_url'],
        json_data['repository']['absolute_url'],
    )
    base_repo_url += '/' if base_repo_url[-1] != '/' else ''
    base_commit_url = urljoin(base_repo_url, 'commits/')
    trello_token = repo.trello_board.trello_token

    for commit in json_data['commits']:
        proc_cards = []
        msg = commit['message']
        context = {
            'author': commit['author'],
            'author_full': commit['raw_author'],
            'changeset': commit['node'],
            'changeset_full': commit['raw_node'],
            'commit_url': urljoin(base_commit_url, commit['raw_node']),
            'commit_message': msg,
        }

        for action, card_id in re_pattern.findall(msg):
            if card_id in proc_cards:
                # Referenced more than once in the commit msg
                continue

            proc_cards.append(card_id)
            use_rule = 'fix_rule' \
                if action.lower() in ['fix', 'close'] else 'ref_rule'
            rule = getattr(repo, use_rule)
            if not rule:
                continue

            # Get Card information
            card = api.get_card_from_board(
                trello_token,
                repo.trello_board.trello_id,
                card_id,
            )
            full_card_id = card['id']

            # Let's process the rule
            if rule.update:
                # Update the card.
                card_msg = render_to_string(
                    'trello_broker/update_message.txt',
                    context,
                )
                api.add_comment_to_card(
                    trello_token,
                    full_card_id,
                    card_msg,
                )

            if rule.move:
                # Move the card
                api.move_card(
                    trello_token,
                    full_card_id,
                    rule.trello_list.trello_id,
                )

            if rule.archive:
                # Archive the card
                api.archive_card(trello_token, full_card_id)
