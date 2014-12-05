from collections import defaultdict

import emzed


def assign_components(graph, proposed_labels=None):
    """
    assumes symmetric graph, no check for this yet.
    todo: evaluate if this function works for asymmetric graphs to and
          replace find_closed_components below if feasible.
    """

    # phase 1: flow like assignemnt of nodes to cluster names:
    # cluster name is the starting node
    assignment = dict()
    nodes = set(graph.keys())
    for start_node in nodes:
        if start_node not in assignment:
            if proposed_labels is not None:
                label = proposed_labels.get(start_node, start_node)
            else:
                label = start_node
            assignment[start_node] = label
            _assign_followers(start_node, graph, assignment)

    reverted_assignment = defaultdict(list)
    for node, group_id in assignment.items():
        reverted_assignment[group_id].append(node)

    return assignment, reverted_assignment


def _assign_followers(start_node, graph, assignment):
    for follower in graph.get(start_node, ()):
        if follower not in assignment:
            assignment[follower] = assignment[start_node]
            _assign_followers(follower, graph, assignment)


def find_closed_components(graph):
    nodes = set(graph.keys())
    seen = set()
    n = len(nodes)
    while len(seen) < n and nodes:
        start_with = nodes.pop()
        if start_with not in seen:
            # dfs search starting with 'start_with' node
            stack = [start_with]
            component = set()
            while stack:
                active_node = stack.pop()
                seen.add(active_node)
                component.add(active_node)
                for follower in graph[active_node]:
                    if follower not in seen and follower not in stack:
                        stack.append(follower)
            yield component


def calculate_probable_iso_shifts(min_abundance, elements=("C", "H", "N", "O", "P", "S"),
                                  halogens=("Cl", "Br")):
    """
    we assume natural abundance for C, H, N, O, P, S, Cl and for Br if given
    as parameters.
    """

    elements = list(elements)
    elements.extend(halogens)

    shifts = emzed.core.data_types.Table(("iso_shifts", "abundance", "mass_shift"),
                                         (str, float, float),
                                         ("%s", "%.6f", "%.5f"),
                                         [])

    for elem in elements:
        abundances = getattr(emzed.abundance, elem)
        items = sorted(abundances.items(), key=lambda item: -item[1])
        num_prot_0, __ = items[0]
        mass_0 = getattr(emzed.mass, "%s%d" % (elem, num_prot_0))
        for num_prot, abundance in items[1:]:
            if abundance < min_abundance:
                continue
            mass = getattr(emzed.mass, "%s%d" % (elem, num_prot))
            name = "%s{%d,%d}" % (elem, num_prot_0, num_prot)
            shifts.addRow([name, abundance, mass - mass_0])

    for i, (name_1, abundance_1, delta_m_1) in enumerate(shifts[:]):
        for (name_2, abundance_2, delta_m_2) in shifts[:i + 1]:
            abundance = abundance_1 * abundance_2
            if abundance > min_abundance:
                delta_m = delta_m_2 + delta_m_1
                shifts.addRow(["%s + %s" % (name_1, name_2), abundance, delta_m])

    shifts.addRow(["", 1.0, 0.0])
    shifts.sortBy("abundance", ascending=False)
    return shifts
