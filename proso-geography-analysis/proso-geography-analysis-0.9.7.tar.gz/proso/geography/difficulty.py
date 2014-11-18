from proso.geography.model import AnswerStream, DefaultModel
from proso.geography.environment import InMemoryEnvironment
from proso.geography.answers import first_answers
from proso.geography.dfutil import iterdicts
import pandas


def difficulty_to_dataframe(difficulty):
    return pandas.DataFrame(difficulty.items()).rename(
        columns={0: 'place', 1: 'difficulty'}
    )


def dataframe_to_difficulty(dataframe):
    return dataframe.set_index('place')['difficulty'].to_dict()


def prepare_difficulty(answers):
    '''
    Compute the difficulty for places.

    Args:
        answers (pandas.DataFrame):
            data frame containing answer data
    Returns:
        dict: place -> difficulty
    '''
    first = first_answers(answers, ['user']).sort('id').sort('id')
    env = InMemoryEnvironment()
    stream = DefaultAnswerStream(env)
    for a in iterdicts(first):
        stream.stream_answer(a)
    return env.export_difficulty()


class DefaultAnswerStream(AnswerStream):

    def __init__(self, environment):
        AnswerStream.__init__(self, DefaultModel(), environment)


class PreserveDifficultyEnvironment(InMemoryEnvironment):

    def __init__(self, difficulty):
        InMemoryEnvironment.__init__(self)
        self._difficulty = difficulty

    def difficulty(self, place_id, new_value=None):
        if new_value is None:
            return InMemoryEnvironment.difficulty(self, place_id)
