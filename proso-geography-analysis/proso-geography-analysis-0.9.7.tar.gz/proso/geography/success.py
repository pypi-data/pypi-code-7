import decorator
import numpy as np


def success_per_user(answers):
    return (answers.
        groupby('user').
        apply(lambda x: sum(x['place_asked'] == x['place_answered']) / float(len(x))).
        to_dict())


def rolling_success_per_user(answers, window_length=10):
    '''
    Number of rolling windows with the given success rate.

    Args:
        answers (pandas.DataFrame):
            data frame containing answer data
        window_length (int, default 10, optional):
            number of answers in window

    Return:
        dict: user -> (rolling success mean, standard deviation)
    '''
    if 'rolling_success' in answers:
        data = answers
    else:
        data = decorator.rolling_success(answers, window_length=window_length)
    data = data[~data['rolling_success'].isnull()]
    return (data.
        groupby('user').
        apply(lambda x: (x['rolling_success'].dropna().mean(), x['rolling_success'].dropna().std())).
        to_dict())


def stay_on_rolling_success(answers, window_length=10):
    '''
    Compute the probability the user stays in the system (the next answers
    belongs to the same session) based on the rolling success rate.

    Args:
        answers (pandas.DataFrame):
            data frame containing answer data
        window_length (int, default 10, optional):
            number of answers in window

    Return:
        dict: success rate -> (probability the user stays in the system, standard deviation, number of samples)
    '''
    if 'rolling_success' in answers:
        data = answers
    else:
        data = decorator.rolling_success(answers, window_length=window_length)
    data = data[np.isfinite(data['rolling_success'])]
    return (data.
        groupby(['user', 'rolling_success']).
        apply(lambda x: sum(~x['last_in_session']) / float(len(x))).
        reset_index().
        rename(columns={0: 'stay'}).
        groupby('rolling_success').
        apply(lambda x: (x['stay'].mean(), x['stay'].std(), len(x))).
        to_dict())
