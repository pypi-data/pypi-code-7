from difficulty import DefaultAnswerStream, PreserveDifficultyEnvironment
from proso.geography.answers import first_answers
from proso.geography.dfutil import iterdicts
from proso.geography.model import predict_simple
import decorator
import pandas


def session_per_user(answers):
    answers = decorator.session_number(answers)
    return answers.groupby('user').apply(lambda x: x['session_number'].max()).to_dict()


def maps_per_user(answers):
    return answers.groupby('user').apply(lambda x: len(x['place_map'].unique())).to_dict()


def answers_pers_place_user(answers):
    return (answers.
        groupby(['user', 'place_asked']).
        apply(len))


def user_ratio(answers, session_number=None, answer_number_min=None, answer_number_max=None):
    answers = decorator.session_number(answers)

    def user_ratio_filter(data):
        if session_number is not None and session_number > data['session_number'].max():
            return False
        if answer_number_min is not None:
            return answer_number_min <= len(data)
        if answer_number_max is not None:
            return answer_number_max >= len(data)
        return True
    return sum(answers.groupby('user').apply(user_ratio_filter)), answers['user'].nunique()


def prior_skill(answers, difficulty):
    '''
    Assuming the given difficulty of places compute the prior skill for users.

    Args:
        answers (pandas.DataFrame):
            data frame containing answer data
        difficulty (dict):
            place -> difficulty
    Returns:
        dict: user's id -> prior skill
    '''
    first = first_answers(answers, ['user']).sort('id')
    env = PreserveDifficultyEnvironment(difficulty)
    stream = DefaultAnswerStream(env)
    for a in iterdicts(first):
        stream.stream_answer(a)
    skill_items = env.export_prior_skill().items()
    ids, skills = zip(*skill_items)
    return dict(zip(list(ids), map(lambda x: predict_simple(x, 0)[0], list(skills))))


def prior_skill_to_dataframe(prior_skill):
    return pandas.DataFrame(prior_skill.items()).rename(
        columns={0: 'user', 1: 'prior_skill'}
    )


def dataframe_to_prior_skill(dataframe):
    return dataframe.set_index('user')['prior_skill'].to_dict()


def answers_per_user(answers):
    '''
    Number of answers per user.

    Args:
        answers (pandas.DataFrame):
            data frame containing answer data
    Return:
        dict: user's id -> number of answers
    '''
    return (answers.
        groupby('user').
        apply(len).
        to_dict())
