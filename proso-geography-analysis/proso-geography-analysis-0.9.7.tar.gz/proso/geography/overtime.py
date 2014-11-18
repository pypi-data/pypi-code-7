def success_per_week(answers):
    return (answers.
        set_index('inserted').
        groupby([lambda x: x.year, lambda x: x.week]).
        apply(lambda x: float(len(x[x['place_asked'] == x['place_answered']])) / float(len(x))).
        to_dict())


def success_by_user_per_week(answers):
    return (answers.
        set_index('inserted').
        groupby(['user', lambda x: x.year, lambda x: x.week]).
        apply(lambda x: float(len(x[x['place_asked'] == x['place_answered']])) / float(len(x))).
        reset_index().
        rename(columns={0: 'sucess'}).
        groupby(['level_1', 'level_2']).
        apply(lambda x: x.sucess.mean()).
        to_dict())


def time_gap(answers):

    def _time_gap(data):
        items = map(
            lambda (p, n): p,
            filter(lambda (p, n): n > 1, data.groupby('place_asked').apply(len).to_dict().items()))
        data = data[data['place_asked'].isin(items)]
        result = data.groupby('place_asked').apply(
            lambda d: (d['inserted'] - d['inserted'].shift(1)).mean().item() / 10.0 ** 9)
        return result.to_dict().values()
    result = answers.groupby('user').apply(_time_gap)
    return result.to_dict()


def users_per_week(answers):
    '''
    Number of user having answers in the given week.

    Args:
        answers (pandas.DataFrame):
            data frame containing answer data

    Return:
        dict: (year, week) -> number of users
    '''
    return (answers.
        set_index('inserted').
        groupby([lambda x: x.year, lambda x: x.week]).
        apply(lambda x: x.user.nunique()).
        to_dict())


def answers_per_week(answers):
    '''
    Number of answers per week.

    Args:
        answers (pandas.DataFrame):
            data frame containing answer data

    Return:
        dict: (year, week) -> number of answers
    '''
    return (answers.
        set_index('inserted').
        groupby(['user', lambda x: x.year, lambda x: x.week]).
        apply(len).
        reset_index().
        rename(columns={0: 'answers_count', 'level_1': 'year', 'level_2': 'week'}).
        groupby(['year', 'week']).
        apply(lambda x: x.answers_count.mean()).
        to_dict())
