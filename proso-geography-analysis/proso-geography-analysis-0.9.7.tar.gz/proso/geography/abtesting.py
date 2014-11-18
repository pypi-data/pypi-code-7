import datetime
import proso.geography.answers as answer
import proso.geography.decorator as decorator


CSRF_HOTFIX = datetime.datetime(year=2014, month=4, day=25, hour=23)
EXPERIMENT_1_FINISH = datetime.datetime(year=2014, month=6, day=25, hour=23, minute=59, second=59)


def drop_invalid_data(data):
    return answer.apply_filter(data, lambda d: d['inserted'] > CSRF_HOTFIX)


def prepare_data(data, group_prefixes):

    def valid_ab_values(ab_values):
        return (
            len([v for v in ab_values if any([v.startswith(p) for p in group_prefixes])])
            ==
            len(group_prefixes)
        )

    data = drop_invalid_data(data)
    data = answer.apply_filter(data, lambda d: valid_ab_values(d['ab_values']))
    if 'recommendation_by_' in group_prefixes and 'recommendation_options_' in group_prefixes:
        data = answer.apply_filter(data, lambda d: d['inserted'] < EXPERIMENT_1_FINISH)
    data = decorator.interested_ab_values(data, group_prefixes)
    users_in_groups = (data.groupby('interested_ab_values').
        apply(lambda x: x['user'].unique()).
        to_dict().
        values())
    users_and_groups = [
        (u, sum([u in us for us in users_in_groups]))
        for u in data['user'].unique()
    ]
    invalid_users = map(lambda (u, n): u, filter(lambda (u, n): n > 1, users_and_groups))
    return data[~data['user'].isin(invalid_users)]
