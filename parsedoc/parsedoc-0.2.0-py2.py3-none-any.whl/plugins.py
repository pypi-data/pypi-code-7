"""Various plugins for the parser

TODO figure out a more pluggable way to do this
"""
from __future__ import print_function, absolute_import, unicode_literals

import logging

logger = logging.getLogger(__name__)
_annotated = {}


def annotation_filter(parsed, args):
    """Parses a PHPdoc structure"""
    # --skip-empty-files is implied by --only-include-annotated
    args['--skip-empty-files'] |= args['--only-include-annotated']

    annotations = args['--annotations'].split(',')

    def recursive_filter_annotation(obj):
        obj.contains = [recursive_filter_annotation(child)
                        for child in obj.contains]
        obj.contains = list(filter(None, obj.contains))

        if len(obj.contains) == 0:
            for annotation in annotations:
                logging.debug("Looking for annotation %s", annotation)
                if annotation in obj.comment:
                    # index the annotation
                    if not _annotated.get(annotation):
                        _annotated[annotation] = {}
                    if not _annotated[annotation].get(parsed.name):
                        _annotated[annotation][parsed.name] = []
                    _annotated[annotation][parsed.name].append(obj.name)
                    return obj
            else:
                if args['--only-include-annotated']:
                    logging.debug("Didn't find annotations in this object, "
                                  "stripping")
                    return None
                else:
                    logging.debug("Returning object %s", repr(obj))
                    # we still need to return it because we're not cleaning
                    return obj
        else:
            return obj

    recursive_filter_annotation(parsed)


def comment_coverage_reporter(parsed, args):
    """Reports comment coverage"""
    def recursive_report_coverage(obj):
        if obj.comment == "":
            logger.warning("%s doesn't have a comment!", obj.name)

        for child in obj.contains:
            recursive_report_coverage(child)

    recursive_report_coverage(parsed)


def php_array_index(args):
    """Writes index created by annotation_filter to php file"""
    import json
    print(json.dumps(_annotated, indent=4))


preprocessing_plugins = [
    comment_coverage_reporter,
    annotation_filter,
]

postprocessing_plugins = [
    php_array_index
]
