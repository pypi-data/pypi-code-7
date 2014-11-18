import decorator
import user
import numpy as np
import proso.geography.answers


def session_user_portion(answers):
    '''
    For each session number compute how many users have answer with it.

    Args:
        answers (pandas.DataFrame):
            data frame containing answer data, if it is not decorated by 'session_number',
            it will be decorated
    Return:
        dict: session number -> number from (0,1)
    '''
    if 'session_number' in answers:
        data = answers
    else:
        data = decorator.session_number(answers)
    all_users = float(data['user'].nunique())
    return (data.
        groupby('session_number').
        apply(lambda x: x['user'].nunique() / all_users).
        to_dict())


def session_length(answers):
    '''
    Compute average length of session according to the session number.

    Args:
        answers (pandas.DataFrame):
            data frame containing answer data, if it is not decorated by 'session_number',
            it will be decorated
    Return:
        dict: session number -> number of answers
    '''
    if 'session_number' in answers:
        data = answers
    else:
        data = decorator.session_number(answers)
    return (data.
        groupby(['user', 'session_number']).
        apply(lambda x: len(x)).
        reset_index().
        rename(columns={0: 'session_length'}).
        groupby('session_number').
        apply(lambda x: x['session_length'].mean()).
        reset_index().
        rename(columns={0: 'session_length'}).
        set_index('session_number')['session_length'].
        to_dict())


def session_prior_skill_diffs(answers, difficulty, session_number_first, session_number_second):
    '''
    Compute prior skills for the given session numbers independently and return differences.
    The prior skill is computed only for the places answered in both sessions.
    Users with less than 10 places are ignored.

    Args:
        answers (pandas.DataFrame):
            data frame containing answer data, if it is not decorated by 'session_number',
            it will be decorated
        difficulty (dict):
            place -> difficulty
        session_number_first (int)
        session_number_second (int)
    Return:
        list: differences of prior skill for the given session numbers
    '''
    if 'session_number' in answers:
        data = answers
    else:
        data = decorator.session_number(answers)
    return (data.
        groupby('user').
        apply(lambda x: _session_prior_skill_diff_for_user(x, difficulty, session_number_first, session_number_second)).
        dropna().values)


def session_success_diffs(answers, session_number_first, session_number_second):
    '''
    Compute success rate for the given session numbers independently and return differences.
    The success rate is computed only for the places answered in both sessions and the first
    answers. Users with less than 10 places are ignored.

    Args:
        answers (pandas.DataFrame):
            data frame containing answer data, if it is not decorated by 'session_number',
            it will be decorated
        session_number_first (int)
        session_number_second (int)
    Return:
        list: differences of success rate for the given session numbers
    '''
    if 'session_number' in answers:
        data = answers
    else:
        data = decorator.session_number(answers)
    return (data.
        groupby('user').
        apply(lambda x: _session_success_diff_for_user(x, session_number_first, session_number_second)).
        dropna().values)


def session_prior_skill(answers, difficulty):
    '''
    Compute average prior skill for each session.

    Args:
        answers (pandas.DataFrame):
            data frame containing answer data, if it is not decorated by 'session_number',
            it will be decorated
        difficulty (dict):
            place -> difficulty
    Return:
        dict: session number -> prior skill
    '''
    if 'session_number' in answers:
        data = answers
    else:
        data = decorator.session_number(answers)
    return (data.
        groupby('session_number').
        apply(lambda x: np.mean(user.prior_skill(x, difficulty).values())).
        to_dict())


def session_success(answers):
    '''
    Compute success rate for each session.

    Args:
        answers (pandas.DataFrame):
            data frame containing answer data, if it is not decorated by 'session_number',
            it will be decorated
    Return:
        dict: session number -> success rate
    '''
    if 'session_number' in answers:
        data = answers
    else:
        data = decorator.session_number(answers)
    return (data.
        groupby(['user', 'session_number']).
        apply(lambda x: float(len(x[x['place_asked'] == x['place_answered']])) / float(len(x))).
        reset_index().
        rename(columns={0: 'success'}).
        groupby('session_number').
        apply(lambda x: x['success'].mean()).
        to_dict())


def session_users(answers):
    '''
    Compute number of users having answers in the given sessions according to
    the session number.

    Args:
        answers (pandas.DataFrame):
            data frame containing answer data, if it is not decorated by 'session_number',
            it will be decorated
    Return:
        dict: session number -> number of users
    '''
    if 'session_number' in answers:
        data = answers
    else:
        data = decorator.session_number(answers)
    return (data.
        groupby(['session_number']).
        apply(lambda x: x['user'].nunique()).
        reset_index().
        rename(columns={0: 'frequency'}).
        set_index('session_number')['frequency'].
        to_dict())


def _session_success_diff_for_user(answers, session_number_first, session_number_second):
    answers_first = answers[answers['session_number'] == session_number_first]
    answers_second = answers[answers['session_number'] == session_number_second]
    asked_first = answers_first['place_asked'].unique()
    asked_second = answers_second['place_asked'].unique()
    asked_both = set(asked_first).intersection(set(asked_second))
    if len(asked_both) < 10:
        return None
    answers_first = proso.geography.answers.first_answers(
        answers_first[answers_first['place_asked'].isin(asked_both)], ['user'])
    answers_second = proso.geography.answers.first_answers(
        answers_second[answers_second['place_asked'].isin(asked_both)], ['user'])
    success_first = len(answers_first[answers_first['place_asked'] == answers_first['place_answered']]) / float(len(answers_first))
    success_second = len(answers_second[answers_second['place_asked'] == answers_second['place_answered']]) / float(len(answers_second))
    success_diff = success_second - success_first
    return success_diff / success_first if success_diff else 0


def _session_prior_skill_diff_for_user(answers, difficulty, session_number_first, session_number_second):
    answers_first = answers[answers['session_number'] == session_number_first]
    answers_second = answers[answers['session_number'] == session_number_second]
    asked_first = answers_first['place_asked'].unique()
    asked_second = answers_second['place_asked'].unique()
    asked_both = set(asked_first).intersection(set(asked_second))
    if len(asked_both) < 10:
        return None
    answers_first = answers_first[answers_first['place_asked'].isin(asked_both)]
    answers_second = answers_second[answers_second['place_asked'].isin(asked_both)]
    skill_first = user.prior_skill(answers_first, difficulty).items()[0][1]
    skill_second = user.prior_skill(answers_second, difficulty).items()[0][1]
    skill_diff = skill_second - skill_first
    return skill_diff / skill_first if skill_diff else 0
