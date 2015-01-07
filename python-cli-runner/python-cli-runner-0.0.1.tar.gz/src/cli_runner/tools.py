# encoding: utf-8


def unwrap_text(text):
    lines = text.splitlines()
    maximal_wrap = min(len(line) - len(line.lstrip())
                       for line in lines
                       if line.strip())
    return '\n'.join(line[maximal_wrap:] for line in lines)
