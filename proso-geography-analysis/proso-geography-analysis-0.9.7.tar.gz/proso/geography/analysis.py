from argparse import ArgumentParser
from os import path, makedirs
import proso.geography.answers as answer
import proso.geography.decorator as decorator
import proso.geography.difficulty
import gc
import numpy as np
import pandas
import sys


def parser_init(required=None):
    parser = ArgumentParser()
    parser.add_argument(
        '-a',
        '--answers',
        metavar='FILE',
        required=_is_required(required, '--answers'),
        help='path to the CSV with answers')
    parser.add_argument(
        '--options',
        metavar='FILE',
        required=_is_required(required, '--options'),
        help='path to the CSV with answer options')
    parser.add_argument(
        '--ab-values',
        metavar='FILE',
        dest='ab_values',
        required=_is_required(required, '--ab-values'),
        help='path to the CSV with ab values')
    parser.add_argument(
        '--answer-ab-values',
        metavar='FILE',
        dest='answer_ab_values',
        required=_is_required(required, '--answer-ab-values'),
        help='path to the CSV with answer ab values')
    parser.add_argument(
        '--places',
        metavar='FILE',
        required=_is_required(required, '--places'),
        help='path to the CSV with places')
    parser.add_argument(
        '-d',
        '--destination',
        metavar='DIR',
        required=True,
        help='path to the directory where the created data will be saved')
    parser.add_argument(
        '-o',
        '--output',
        metavar='EXT',
        dest='output',
        default='svg',
        help='extension for the output fles')
    parser.add_argument(
        '--drop-classrooms',
        action='store_true',
        dest='drop_classrooms',
        help='drop users having some of the first answer from classroom')
    parser.add_argument(
        '--drop-tests',
        action='store_true',
        dest='drop_tests',
        help='drop users having at least one test answer')
    parser.add_argument(
        '--answers-per-user',
        type=int,
        dest='answers_per_user',
        help='drop user having less than the given number of answers')
    parser.add_argument(
        '--data-dir',
        type=str,
        metavar='DIRECTORY',
        dest='data_dir',
        default='./data',
        help='directory with data files, used when the data files are specified')
    parser.add_argument(
        '--storage',
        type=str,
        default='hdf',
        choices=['csv', 'hdf'])
    parser.add_argument(
        '--map-code',
        dest='map_code',
        nargs='+',
        type=str)
    parser.add_argument(
        '--map-type',
        dest='map_type',
        nargs='+',
        type=str)
    parser.add_argument(
        '--place-asked-type',
        dest='place_asked_type',
        nargs='+',
        type=str)
    parser.add_argument(
        '--drop-users',
        dest='drop_users',
        action='store_true',
        help='when filtering the data drop users having invalid answers')
    return parser


def write_cache(args, dataframe, filename, force_storage=None):
    if not path.exists(args.destination):
        makedirs(args.destination)
    if args.storage == 'csv' and (force_storage is None or force_storage == 'csv'):
        print 'writing CSV cache "%s" (%s lines)' % (filename, len(dataframe))
        dataframe.to_csv('%s/%s.csv' % (args.destination, filename), index=False)
    else:
        print 'writing HDF cache "%s" (%s lines)' % (filename, len(dataframe))
        dataframe.to_hdf('%s/storage.hdf' % args.destination, filename.replace('.', '_'))


def read_cache(args, filename, csv_parser=None):
    try:
        print 'trying to read HDF cache "%s"' % filename
        result = pandas.read_hdf('%s/storage.hdf' % args.destination, filename.replace('.', '_'))
    except:
        print 'failed to read HDF cache "%s"' % filename
        try:
            print 'trying to read CSV cache "%s"' % filename
            if csv_parser:
                result = csv_parser('%s/%s.csv' % (args.destination, filename))
            else:
                result = pandas.read_csv('%s/%s.csv' % (args.destination, filename), index_col=False)
            write_cache(args, result, filename, force_storage='hdf')
        except:
            print 'failed to read CSV cache "%s"' % filename
            return None
    print '%s lines loaded' % len(result)
    return result


def data_hash(args):
    return 'apu_%s__dcs_%s__dts_%s__mc_%s__pat_%s__mt_%s__du_%s' % (
        args.answers_per_user,
        args.drop_classrooms,
        args.drop_tests,
        'x'.join(args.map_code if args.map_code else []),
        'x'.join(args.place_asked_type if args.place_asked_type else []),
        'x'.join(args.map_type if args.map_type else []),
        args.drop_users)


def parser_group(parser, groups):
    parser.add_argument(
        '--groups',
        choices=groups,
        nargs='+',
        help='generate only a limited set of plots')
    parser.add_argument(
        '--skip-groups',
        choices=groups,
        dest='skip_groups',
        nargs='+',
        help='generate only a limited set of plots')
    return parser


def decorator_optimization(answers):
    if len(answers) == 0:
        print "There are no answers to analyze"
        sys.exit()
    decorated = decorator.rolling_success(
        decorator.last_in_session(
            decorator.session_number(answers)))
    return decorated


def load_answers(args):
    filename = 'geography.answer_%s' % data_hash(args)
    data_all = load_answers_all(args)
    data = read_cache(args, filename, csv_parser=answer.from_csv)
    if data is not None:
        return data, data_all
    data = data_all
    if args.map_code:
        data = answer.apply_filter(data, lambda x: x['place_map_code'] in args.map_code, drop_users=args.drop_users)
    if args.map_type:
        data = answer.apply_filter(data, lambda x: x['place_map_type'] in args.map_type, drop_users=args.drop_users)
    if args.place_asked_type:
        data = answer.apply_filter(data, lambda x: x['place_asked_type'] in args.place_asked_type, drop_users=args.drop_users)
    if args.map_code or args.place_asked_type or args.map_type:
        del data['rolling_success']
        del data['last_in_session']
        del data['session_number']
        data = decorator_optimization(data)
    if args.drop_tests:
        data = answer.apply_filter(data, lambda x: np.isnan(x['test_id']))
    if args.drop_classrooms:
        data = answer.drop_classrooms(data)
    if args.answers_per_user:
        data = answer.drop_users_by_answers(data, answer_limit_min=args.answers_per_user)
    write_cache(args, data, filename)
    return data, data_all


def load_answers_all(args):
    data = read_cache(args, 'geography.answer', csv_parser=answer.from_csv)
    if data is not None:
        return data
    answers_file = args.answers if args.answers else args.data_dir + '/geography.answer.csv'
    options_file = args.options if args.options else args.data_dir + '/geography.answer_options.csv'
    ab_values_file = args.ab_values if args.ab_values else args.data_dir + '/geography.ab_value.csv'
    answer_ab_values_file = args.answer_ab_values if args.answer_ab_values else args.data_dir + '/geography.answer_ab_values.csv'
    place_file = args.places if args.places else args.data_dir + '/geography.place.csv'
    if not path.exists(options_file):
        options_file = None
    if not path.exists(ab_values_file):
        ab_values_file = None
    if not path.exists(answer_ab_values_file):
        answer_ab_values_file = None
    data = answer.from_csv(
        answer_csv=answers_file,
        answer_options_csv=options_file,
        answer_ab_values_csv=answer_ab_values_file,
        ab_value_csv=ab_values_file,
        place_csv=place_file,
        should_sort=False)
    data = decorator_optimization(data)
    write_cache(args, data, 'geography.answer')
    return data


def load_difficulty(args, data_all):
    difficulty = read_cache(args, 'difficulty')
    if difficulty is not None or data_all is None:
        return proso.geography.difficulty.dataframe_to_difficulty(difficulty) if difficulty is not None else None
    difficulty = proso.geography.difficulty.prepare_difficulty(data_all)
    write_cache(args, proso.geography.difficulty.difficulty_to_dataframe(difficulty), 'difficulty')
    gc.collect()
    return difficulty


def load_prior_skill(args, data_all, difficulty):
    prior_skill = read_cache(args, 'prior_skill')
    if data_all is None or difficulty is None or prior_skill is not None:
        return proso.geography.user.dataframe_to_prior_skill(prior_skill) if prior_skill is not None else None
    prior_skill = proso.geography.user.prior_skill(data_all, difficulty)
    write_cache(args, proso.geography.prior_skill.prior_skill_to_dataframe(prior_skill), 'prior_skill')
    gc.collect()
    return prior_skill


def get_destination(args, prefix=''):
    dest_file = args.destination + '/' + prefix + data_hash(args)
    if not path.exists(dest_file):
        makedirs(dest_file)
    return dest_file


def savefig(args, figure, name, prefix=''):
    figure.savefig(get_destination(args, prefix) + '/' + name + '.' + args.output, bbox_inches='tight')


def is_group(args, group):
    return (not args.groups or group in args.groups) and (not args.skip_groups or group not in args.skip_groups)


def is_any_group(args, groups):
    return any([is_group(args, group) for group in groups])


def _is_required(required, name):
    return required is not None and name in required
