# -*- coding: utf-8 -*-

"""
Basic functionality to work with answer data.
"""

import dfutil
import numpy as np
import random
import pandas

PLACE_TYPES = {
    0: 'unknown',
    1: 'state',
    2: 'city',
    3: 'world',
    4: 'continent',
    5: 'river',
    6: 'lake',
    7: 'region_cz',
    8: 'bundesland',
    9: 'province',
    10: 'region_it',
    11: 'region',
    12: 'autonumous_comunity',
    13: 'mountains',
    14: 'island'
}


def first_answers(answers, group):
    '''
    Returns first answers with the given group only

    Args:
        answers (pandas.DataFrame):
            dataframe containing answer data
        group (list):
            pandas group used to groupby the data frame
    Returns:
        pandas.DataFrame
    '''
    return (answers.
        sort('id').
        groupby(group).
        apply(lambda x: x.drop_duplicates('place_asked')).
        set_index('id').
        reset_index())


def drop_users_by_answers(answers, answer_limit_min=None, answer_limit_max=None):
    """
    Drop users having less than the given number of answers.
    """
    valid_users = map(
        lambda (u, n): u,
        filter(
            lambda (u, n): (answer_limit_min is None or n >= answer_limit_min) and (answer_limit_max is None or n <= answer_limit_max),
            answers.groupby('user').apply(len).to_dict().items()
        )
    )
    return answers[answers['user'].isin(valid_users)]


def drop_classrooms(answers, classroom_size=5):
    """
    Use a heuristic to filter out users from classrooms. Be aware the function
    also drops all answer which do not have IP address.

    Args:
        answers (pandas.DataFrame)
            dataframe containing answer data
    Returns
        pandas.DataFrame
    """
    classroom_users = [
        user
        for ip, users in (
            answers.sort('id').drop_duplicates('user').
            groupby('ip_address').
            apply(lambda x: x['user'].unique()).
            to_dict().
            items())
        for user in users
        if len(users) > classroom_size
    ]
    return answers[~answers['user'].isin(classroom_users)]


def from_csv(answer_csv, answer_options_csv=None, answer_ab_values_csv=None, ab_value_csv=None, place_csv=None, answers_col_types=None, should_sort=True):
    """
    Loads answer data from the given CSV files.

    Args:
        answer_csv (str):
            name of the file containing  answer data
        answer_options_csv (str, optional):
            name of the file containing answer_options data
        answer_ab_values_csv (str, optional):
            name of the file containing answer_ab_values data
        ab_value_csv (str):
            name of the file containing ab_value data

    Returns:
        pandas.DataFrame
    """
    col_types = {
        'user': np.uint32,
        'id': np.uint32,
        'place_asked': np.uint16,
        'place_answered': np.float16,  # because of NAs
        'type': np.uint8,
        'response_time': np.uint32,
        'number_of_options': np.uint8,
        'place_map': np.float16,       # because of NAs
        'ip_address': str,
        'language': str,
        'test_id': np.float16          # because of NAs
    }
    if answers_col_types:
        for col_name, col_type in answers_col_types.iteritems():
            col_types[col_name] = col_type
    answers = dfutil.load_csv(
        answer_csv, col_types, col_dates=['inserted'], should_sort=should_sort)
    if answer_options_csv:
        options_from_csv(answers, answer_options_csv)
    if ab_value_csv and answer_ab_values_csv:
        ab_values_from_csv(answers, ab_value_csv, answer_ab_values_csv)
    if place_csv:
        places_original = dfutil.load_csv(place_csv)
        places = pandas.DataFrame(index=places_original.index, columns=['id', 'code', 'type'])
        places['id'] = places_original['id']
        places['code'] = places_original['code']
        places['type'] = places_original['type'].apply(lambda x: PLACE_TYPES.get(x, 'unknown'))
        answers = pandas.merge(answers, places.rename(columns={'id': 'place_asked', 'code': 'place_asked_code', 'type': 'place_asked_type'}), on='place_asked', how='left')
        answers = pandas.merge(answers, places.rename(columns={'id': 'place_answered', 'code': 'place_answered_code', 'type': 'place_answered_type'}), on='place_answered', how='left')
        answers = pandas.merge(answers, places.rename(columns={'id': 'place_map', 'code': 'place_map_code', 'type': 'place_map_type'}), on='place_map', how='left')
    return answers


def apply_filter(answers, filter_fun, drop_users=True):
    """
    Filters the answers by the given filter and drops the users whose answers
    are filtered out (if enabled).

    Args:
        answers (pandas.DataFrame)
            dataframe containing answer data
        filter_fun (function):
            row predicate
        drop_users (bool, optional):
            enables/disables dropping users

    Returns:
        pandas.DataFrame
    """
    validity = dfutil.apply_rows(answers, filter_fun)
    valid_answers = answers[validity]
    if drop_users:
        invalid_users = answers[~validity]['user'].unique()
        valid_answers = valid_answers[~valid_answers['user'].isin(invalid_users)]
    return valid_answers


def anonymize(answers):
    """
    Tries to drop all information which can be used to determine the user's
    identity from the answer data.

    Args:
        answers (pandas.DataFrame)
            dataframe containing answer data
        filter_fun (function):
            row predicate
        drop_users (bool, optional):
            enables/disables dropping users

    Returns:
        pandas.DataFrame
    """
    users = range(1, answers['user'].max() + 1)
    random.shuffle(users)
    users = dict(zip(range(1, answers['user'].max() + 1), users))
    answers['user'] = answers['user'].apply(lambda x: users[x])
    if 'ip_address' in answers:
        answers.drop('ip_address', axis=1, inplace=True)
    return answers


def sample(answers, ratio):
    """
    Divides data to sample set and the data holding the given percentage given
    by 'ratio' parameter.


    Args:
        answers (pandas.DataFrame)
            dataframe containing answer data
        ratio (float):
            number from the interval (0, 1) specifying the size of the sample set

    Returns:
        pandas.DataFrame, pandas.DataFrame
    """
    if ratio <= 0 or ratio >= 1:
        raise Exception('parameter ratio has to be a value from the interval (0, 1)')
    users = random.sample(answers['user'].unique(), int(ratio * len(answers['user'].unique())))
    return answers[answers['user'].isin(users)], answers[~answers['user'].isin(users)]


def ab_values_from_csv(answers, ab_value_csv, answer_ab_values_csv):
    """
    Loads A/B values to the answers data frame.
    WARNING: The function modifies the given dataframe!

    Args:
        answers (pandas.DataFrame):
            dataframe containing answer data
        ab_value_csv (str):
            name of the file containing ab_value data
        answer_ab_values_csv (str, optional):
            name of the file containing answer_ab_values data

    Returns:
        pandas.DataFrame
    """
    ab_values = dfutil.load_csv(ab_value_csv, col_dates=[])
    answer_ab_values = dfutil.load_csv(answer_ab_values_csv, col_dates=[])
    ab_values_dict = {}
    answer_ab_values_dict = {}
    for ab_id, val in zip(ab_values['id'].values, ab_values['value'].values):
        ab_values_dict[ab_id] = val
    for answer, value in zip(answer_ab_values['answer'].values, answer_ab_values['value'].values):
        if answer not in answer_ab_values_dict:
            answer_ab_values_dict[answer] = []
        answer_ab_values_dict[answer].append(ab_values_dict[value])
    answers['ab_values'] = answers['id'].map(lambda id: answer_ab_values_dict.get(id, []))
    return answers


def options_from_csv(answers, answer_options_csv):
    """
    Loads options to the answers data frame.
    WARNING: The function modifies the given dataframe!

    Args:
        answers (pandas.DataFrame):
            data frame containing answer data
        answer_options_csv (str):
            name of the file containing answer_options data

    Returns:
        pandas.DataFrame
    """
    options = dfutil.load_csv(answer_options_csv)
    options.sort(['answer', 'id'], inplace=True)
    options_dict = {}
    last_answer = None
    collected_options = None
    for answer, place in zip(options['answer'].values, options['place'].values):
        if last_answer != answer:
            if collected_options:
                options_dict[last_answer] = collected_options
            collected_options = []
        collected_options.append(place)
        last_answer = answer
    if collected_options:
        options_dict[last_answer] = collected_options
    answers['options'] = answers['id'].map(lambda id: options_dict.get(id, []))
    return answers
