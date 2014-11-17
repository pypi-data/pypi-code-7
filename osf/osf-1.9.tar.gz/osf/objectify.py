from .grammar import *
from .timeutils import hhmmss_to_milliseconds
from .classes import OSFLine, ParentlessNoteError


def objectify_line_time(line, osf_line, time_offset=0):
    time_hhmmss = line.find(HHMMSSTime)
    time_unix = line.find(UnixTime)

    if time_hhmmss:
        hun = time_hhmmss.find(HHMMSSHundredthsComponent)
        hun_val = 0
        if hun:
            hun_val = hun.string

        osf_line.time = hhmmss_to_milliseconds(time_hhmmss.find(HHMMSSTimeHourComponent).string,
                                               time_hhmmss.find(HHMMSSTimeMinuteComponent).string,
                                               time_hhmmss.find(HHMMSSSecondComponent).string,
                                               hun_val)
    elif time_unix:
        osf_line.time = (int(time_unix.string) - time_offset) * 1000
    else:
        osf_line.time = None


def objectify_line_text(line, osf_line):
    osf_line.text = line.find(Text).string


def objectify_line_link(line, osf_line):
    link = line.find(Link)
    if link:
        osf_line.link = link[1].string


def f7(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if not (x in seen or seen_add(x))]


def objectify_line_tags(line, osf_line):
    tags = line.find_all(Tag)
    osf_line.tags = f7([tag[1].string for tag in tags])


def objectify_line(line, time_offset=0):
    osf_line = OSFLine()

    if hasattr(line, '_line'):
        osf_line._line = line._line

    objectify_line_time(line, osf_line, time_offset)
    objectify_line_text(line, osf_line)
    objectify_line_link(line, osf_line)
    objectify_line_tags(line, osf_line)

    return osf_line, len(line.find_all(Indentation))


def objectify_lines(lines):
    if not lines:
        return []

    time_offset = 0

    if not isinstance(lines[0], ParseError):
        unix_time = lines[0].find(UnixTime)

        if unix_time:
            time_offset = int(unix_time.string)

    # root notes (depth 0)
    notes = []
    # last known note at depth n
    depth_note = {}
    # maximum depth found (used to partially clear depth_note when needed)
    max_depth = 0
    # depth of the note before the current one
    last_depth = 0

    for line in lines:
        if isinstance(line, modgrammar.ParseError):
            notes.append(line)
        else:
            note, n_depth = objectify_line(line, time_offset)

            if n_depth == 0:
                # add root notes to the main list
                notes.append(note)
            else:
                # find the nearest note above this one
                # It is not possible to skip from D to B here, because
                # B (depth 1) gets deleted once C (depth 0) is encountered.
                #    A
                #    - B
                #    C
                #    -- D
                # instead, D will be added to C.
                parent_depth = n_depth - 1

                while parent_depth not in depth_note and parent_depth > -1:
                    parent_depth -= 1

                if parent_depth < 0:
                    # we failed to find a proper parent..
                    if not hasattr(note, '_line'):
                        raise ParentlessNoteError()
                    else:
                        notes.append(ParentlessNoteError(note._line))
                    continue
                else:
                    depth_note[parent_depth].notes.append(note)

            depth_note[n_depth] = note

            # if the current note is less deep then a last one clear all
            # known notes deeper than this one. This is needed so a note
            # is never attached to the wrong parent. See the example above.
            if n_depth < last_depth:
                for d in range(n_depth + 1, max_depth + 1):
                    if d in depth_note:
                        del depth_note[d]

            if n_depth > max_depth:
                max_depth = n_depth

            last_depth = n_depth

    return notes
