# -*- coding: utf-8 -*-
from pandas import read_csv, Series


class DictIterator:

    def __init__(self, dataframe):
        self._dataframe = dataframe

    def __iter__(self):
        self._iter = self._dataframe.values.__iter__()
        self._columns = self._dataframe.columns.values
        return self

    def __len__(self):
        return len(self._dataframe)

    def next(self):
        return dict(zip(self._columns, self._iter.next()))


def apply_rows(dataframe, fun):
    """
    Applies the given funtion to each row of the given dataframe
    and returns Series with the result.

    This function has the same semantic as extremely slow calling:

        dataframe.apply(fun, axis=1)

    Args:
        dataframe (pandas.DataFrame):
            dataframe which is used for the application
        fun (function):
            function to apply to each row (represented as dict)

    Returns:
        pandas.DataFrame
    """
    result = []
    for d in iterdicts(dataframe):
        result.append(fun(d))
    return Series(result, index=dataframe.index)


def iterdicts(dataframe):
    """
    Allows you to efficiently iterate over the dataframe.

    Args:
        dataframe (pandas.DataFrame):
            dataframe to iterate

    Returns:
        iterator allowing you to iterate over the dataframe providing rows as
        dicts
    """
    return DictIterator(dataframe)


def load_csv(csv_file, col_types=None, col_dates=[], should_sort=True):
    data = read_csv(
        csv_file,
        index_col=False,
        dtype=col_types,
        parse_dates=col_dates if col_dates else [])
    for column in data.columns:
        if column == 'id' and should_sort:
            data.sort(['id'], inplace=True, ascending=True)
        elif is_list_column(data[column]):
            data[column] = data[column].apply(
                lambda x: str2list(x, lambda x: int(x) if x.isdigit() else x))
    return data


def str2list(x, convert_item=None):
    s = x.strip('[]').replace(' ', '')
    if not s:
        return []
    s = s.split(',')
    if convert_item:
        s = map(lambda x: convert_item(x.replace("'", '').replace("\"", '')), s)
    return s


def is_list_column(column):
    if len(column) == 0:
        return False
    reps = column.head(min(10, len(column)))
    str_type = type('')
    return reps.apply(lambda x: type(x) == str_type and x.startswith('[') and x.endswith(']')).all()
