'''dossier.fc Feature Collections

.. This software is released under an MIT/X11 open source license.
   Copyright 2012-2014 Diffeo, Inc.

'''
from operator import itemgetter
import sys

from dossier.fc import StringCounter, FeatureCollectionChunk


def key_sorted_dict_str(mset):
    return ', '.join(['%s: %d' % (k, mset[k])
                      for k in sorted(mset.iterkeys())])


def repr_feature(feature, max_keys=100, indent=8, lexigraphic=False):
    '''
    generate a pretty-printed string for a feature

    Currently implemented:
      * StringCounter

    @max_keys: truncate long counters

    @indent: indent multi-line displays by this many spaces

    @lexigraphic: instead of sorting counters by count (default), sort
    keys lexigraphically
    '''
    if isinstance(feature, StringCounter):
        if lexigraphic:
            recs = list(feature.iteritems())
            recs.sort(key=itemgetter(0))
            recs = recs[:max_keys]
        else:
            recs = feature.most_common(max_keys)
    elif isinstance(feature, unicode):
        return feature
    else:
        raise Exception('repr_feature(%r) not yet implemented' % type(feature))

    joiner = ', '
    if isinstance(feature, StringCounter):
        ## might have very long keys, e.g. whole sentences or URLs
        longest_key = max(map(len, map(itemgetter(0), recs)))
        if longest_key > 20:
            recs = map(lambda x: '%d: %r' % (x[1], x[0]), recs)
            joiner = '\n' + ' ' * indent
        else:
            recs = map(lambda x: '%r: %d' % (x[0], x[1]), recs)
            joiner = ', '

    len_feature = len(feature)
    if len_feature > max_keys:
        recs.append(' truncated at %d' % max_keys)
    recs.insert(0, ' (%d keys)' % len_feature)
    return joiner.join(recs)


def detailed_view(fc, features_to_show=None, max_keys=100, lexigraphic=False):
    '''
    returns a pretty-printed string describing a
    :class:`dossier.fc.FeatureCollection`.
    
    @features_to_show: list of features to include, defaults to None
    meaning include all.

    @lexigraphic: passed to repr_feature
    '''
    if 'NAME' in fc:
        top_lines = ['NAME: %r' % key_sorted_dict_str( fc.get('NAME') )]
    elif 'NOM' in fc:
        top_lines = ['NOM: %r' % key_sorted_dict_str( fc.get('NOM') )]
    else:
        top_lines = ['no-NAME, no-NOM']
    bottom_lines = []
    feature_names = fc.keys()
    feature_names.sort()
    for key in feature_names:
        if key in fc and fc[key]:
            if features_to_show and key not in features_to_show:
                continue
            repr = repr_feature(fc[key], max_keys=max_keys, lexigraphic=lexigraphic)
            if '\n' in repr:
                ## save these for the end
                # use four spaces, smaller than indent=8 above
                bottom_lines.append( '    %s: %s' % (key, repr) )
            else:
                top_lines.append( '    %s: %s' % (key, repr))
    return '\n'.join(top_lines + bottom_lines)


def only_specific_multisets(ent, multisets_to_show):
    '''
    returns a pretty-printed string for specific features in a FeatureCollection
    '''
    out_str = []
    for mset_name in multisets_to_show:
        for key, count in ent[mset_name].items():
            out_str.append( '%s - %d: %s' % (mset_name, count, key) )
    return '\n'.join(out_str)


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='Shows the features for each feature FeatureCollection in a Chunk',
        usage='dossier_feature_dump file.fc')
    parser.add_argument(
        'input', metavar='file.fb', nargs='?', default='-',
        help='defaults to stdin')
    parser.add_argument(
        '-o', '--out', default=None,
        dest='output', help='file to write output to, default stdout')
    parser.add_argument(
        '-f', '--feature', metavar='FEATURE_NAME', default=[],
        dest='features_to_show', action='append', help='only print these features')
    parser.add_argument(
        '--column-view', default=False, action='store_true', 
        help='include this multiset in print out')
    parser.add_argument(
        '--max-keys', default=100, type=int, 
        help='number of keys to show in counters')
    parser.add_argument(
        '--lexigraphic', default=False, action='store_true', 
        help='sort counter keys lexigraphically instead of by count')
    parser.add_argument(
        '--limit', default=None, type=int, metavar='LIMIT',
        help='stop after reading LIMIT records')
    args = parser.parse_args()

    if args.output:
        out = open(args.output, 'w')
    else:
        out = sys.stdout

    if args.input == '-':
        i_chunk = FeatureCollectionChunk(file_obj=sys.stdin)
    else:
        ## this allows Chunk to detect .xz and .gpg
        i_chunk = FeatureCollectionChunk(args.input)

    if  args.features_to_show:
        args.features_to_show = set(args.features_to_show)

    count = 0
    for fc in i_chunk:
        if args.column_view:
            out_str = only_specific_multisets(fc, args.features_to_show)
        else:
            out_str = detailed_view(
                fc, features_to_show=args.features_to_show, 
                max_keys=args.max_keys, lexigraphic=args.lexigraphic)
        if out_str:
            out.write(out_str.encode('utf-8'))
            out.write('\n')
        count += 1
        if (args.limit is not None) and (count >= args.limit):
            break

if __name__ == '__main__':
    main()
