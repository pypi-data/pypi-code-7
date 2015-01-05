"""cubicweb-vcwiki application package

Version controlled wiki component for the CubicWeb framework
"""


def is_vfile_of_wiki(entity):
    return bool(entity._cw.execute(
            "Any W WHERE W content_repo R, X eid %(x)s, X from_repository R, "
            "W content_file_extension EXT, X name ~= ('%.' + EXT)",
            {'x': entity.eid}))


def is_vcontent_of_wiki(entity):
    return bool(entity._cw.execute(
            "Any W WHERE W content_repo R, X eid %(x)s, "
            "X content_for F, F from_repository R, "
            "W content_file_extension EXT, F name ~= ('%.' + EXT)",
            {'x': entity.eid}))
