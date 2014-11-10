# -*- coding: utf-8 -*

def table2xml(keyphrases_table):
    res = "<table>\n"
    for keyphrase in sorted(keyphrases_table.keys()):
        res += '  <keyphrase value="%s">\n' % keyphrase
        for text in sorted(keyphrases_table[keyphrase].keys()):
            res += '    <text name="%s">' % text
            res += '%.3f' % keyphrases_table[keyphrase][text]
            res += '</text>\n'
        res += '  </keyphrase>\n'
    res += "</table>\n"
    return res


def table2csv(keyphrases_table):

    def quote(s):
        return '"' + s.replace('"', "'") + '"'

    keyphrases = sorted(keyphrases_table.keys())
    texts = sorted(keyphrases_table[keyphrases[0]].keys())
    res = "," + ",".join(map(quote, keyphrases)) + "\n"  # Heading
    for text in texts:
        scores = map(lambda score: u"%.3f" % score,
                     [keyphrases_table[keyphrase][text] for keyphrase in keyphrases])
        res += (quote(text) + "," + ",".join(scores) + "\n")
    return res


def graph2edges(graph):
    res = ""
    for node in graph:
        if graph[node]:
            res += "%s -> %s\n" % (node, ", ".join(graph[node]))
    return res


def graph2gml(graph):
    res = "graph\n[\n"
    i = 0
    node_ids = {}
    for i, node in enumerate(graph["nodes"]):
        res += '  node\n  [\n    id %i\n    label "%s"\n  ]\n' % (i, node["label"])
        node_ids[node["id"]] = i
        i += 1
    for edge in graph["edges"]:
        res += '  edge\n  [\n    source %i\n    target %i\n  ]\n' % (edge["source"],
                                                                     edge["target"])
    res += "]\n"
    return res
