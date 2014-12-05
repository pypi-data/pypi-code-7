from collections import defaultdict, namedtuple
from itertools import product
import re

import emzed
from algorithms import assign_components, find_closed_components


"""
restrictions: negative mode gemessen
"""


MainPeak = namedtuple('MainPeak', 'id_, mz_main, rt_main, z, elements')


def dump(graph, vertices):
    for in_, outs in graph.items():
        for out in outs:
            for v0, v1 in vertices.get((in_, out)):
                print in_, "->", out, ":", v0, "->", v1


def restrict_dict(dd, sub_key_set):
    return dict((k, v) for (k, v) in dd.items() if k in sub_key_set)


def restrict_graph(vertices, nodes):
    sub_graph = defaultdict(list)
    for n1 in nodes:
        for n2 in nodes:
            vertex = vertices.get((n1, n2))
            if vertex:
                sub_graph[n1].append(n2)
    return sub_graph


def build_sub_graph(graph, vertices, assignment):
    """ create sub graph which is consistent with the current assignment
        that is: only one edge per pair of nodes, not multiples """
    sub_graph = defaultdict(set)
    for in_node, out_nodes in graph.items():
        for out_node in out_nodes:
            for (a0, a1) in vertices.get((in_node, out_node), []):
                # only add vertex if current assignment allows this:
                if assignment[in_node] == a0 and assignment[out_node] == a1:
                    sub_graph[in_node].add(out_node)
    return sub_graph


def create_all_assignments(possible_adducts, nodes):
    """ parameter possible_adducts: maps (node -> list of possible adducts)
    """
    # iterate over crossproducts:
    for assignment in product(*[possible_adducts[k] for k in nodes]):
        if len(set(assignment)) < len(assignment):
            # assignment if same adduct to two isotope clustes
            continue
        assignment = dict(zip(nodes, assignment))
        yield assignment


class AdductAssigner(object):

    def __init__(self, mode, mz_tolerance=8e-4, rt_tolerance=5, cl_only_as_adduct=True,
                 allow_acetate=False):

        assert mode == "negative_mode", "other modes not implemented yet"
        self.mode = mode
        self.mz_tolerance = mz_tolerance
        self.rt_tolerance = rt_tolerance
        self.cl_only_as_adduct = cl_only_as_adduct
        self.allow_acetate = allow_acetate

    def process(self, table):

        col_names = table.getColNames()

        assert "isotope_cluster_id" in col_names
        assert "mass_corr" in col_names
        assert "unlabeled_isotope_shift" in col_names
        assert "carbon_isotope_shift" in col_names
        assert "mz" in col_names
        assert "rt" in col_names
        assert "area" in col_names
        assert "z" in col_names

        peaks = self._extract_main_peaks(table)
        graph, vertices = self._build_graph(peaks)
        adduct_cluster_assignment, reverted_assignment = assign_components(graph)
        assigned_adducts = self._resolve_adducts(vertices, reverted_assignment)
        self._enrich_table(table, adduct_cluster_assignment, assigned_adducts)

        for j, adducts in assigned_adducts.items():
            if len(adducts) > 1:
                print "isotope_cluster= %5d" % j, "alternatives=", adducts

    @staticmethod
    def find_consistent_assignments(graph, vertices):

        """
        we consider the nodes of the graph as variables and each connection
        represents an constraint.
        so we iterate over all possible variable assignments and check
        the constraints.

        we assume a symmetric graph, that is each starting node occurs in another
        nodes target nodes and vice versa.
        """


        nodes = set(graph.keys())
        TO_OBSERVE = 84 # None
        DEBUG = TO_OBSERVE in nodes

        if DEBUG:
            import pprint
            dump(graph, vertices)

        # we iterativliy look for components which have max size and are consistent
        # with the adduct asignment hypthesises

        possible_adducts = defaultdict(set)
        for in_, outs in graph.items():
            for out in outs:
                for a0, a1 in vertices.get((in_, out), []):
                    possible_adducts[in_].add(a0)
                    possible_adducts[out].add(a1)

        if not(possible_adducts):
            # might happen if nodes are not connected
            return

        # now we iterate over each possible node assignment setting
        # and try to find the best one, aka the one which creates the largest sub graph

        partial_solutions = []
        for assignment in create_all_assignments(possible_adducts, nodes):

            restricted_graph = build_sub_graph(graph, vertices, assignment)

            partial_solution = []
            for component in find_closed_components(restricted_graph):
                reduced_assignment = restrict_dict(assignment, sub_key_set=component)
                partial_solution.append(reduced_assignment)

            partial_solutions.append((len(partial_solution), partial_solution))

        if partial_solutions:
            lmax, __ = max(partial_solutions)
            for l, solution in partial_solutions:
                if l == lmax:
                    for assignment in solution:
                        yield assignment

    def _extract_main_peaks(self, table):
        peaks = []
        table.sortBy("isotope_cluster_id")
        for group in table.splitBy("isotope_cluster_id"):
            if group.z.uniqueValue() == 0:
                continue
            id_ = group.isotope_cluster_id.uniqueValue()
            main_peak = group.filter(group.area == group.area.max)
            mz_main = main_peak.mz.values[0]
            rt_main = main_peak.rt.values[0]
            z = group.z.values[0]

            reg_exp = re.compile("([A-Z][a-z]?){\d+,\d+}")
            isos = [isotope_shifts for isotope_shifts in group.unlabeled_isotope_shift
                                   if isotope_shifts is not None]

            elements = [el_name for isotope_shifts in list(group.unlabeled_isotope_shift)
                                if isotope_shifts is not None
                                for el_name in reg_exp.findall(isotope_shifts)]
            elements = set(elements)

            peak = MainPeak(id_, mz_main, rt_main, z, elements)
            peaks.append(peak)

        return peaks

    def _build_graph(self, peaks):
        """
        vertices in this graph connect isotope clusters which could represent the
        same adduct
        """
        graph = defaultdict(list)
        vertices = defaultdict(list)

        if self.mode == "negative_mode":
            adducts = emzed.adducts.negative.adducts
        else:
            adducts = emzed.adducts.positive.adducts

        adducts = [(name, delta, abs(z)) for (name, delta, z) in adducts
                                         if self.allow_acetate or name != "M+CH3COO"]

        rt_tolerance = self.rt_tolerance
        mz_tolerance = self.mz_tolerance

        for i, peak_i in enumerate(peaks):

            mz_i = peak_i.mz_main
            id_i = peak_i.id_
            for (name_i, delta_m_i, z_i) in adducts:
                if self.cl_only_as_adduct:
                    if "Cl" in peak_i.elements and "Cl" not in name_i:
                        continue
                if z_i != peak_i.z:
                    continue
                m0_i = mz_i * z_i - delta_m_i
                if m0_i < 0:
                    continue
                for j, peak_j in enumerate(peaks):
                    if i <= j:
                        continue
                    id_j = peak_j.id_
                    mz_j = peak_j.mz_main
                    if abs(peak_j.rt_main - peak_i.rt_main) < rt_tolerance:
                        for (name_j, delta_m_j, z_j) in adducts:
                            if self.cl_only_as_adduct:
                                if "Cl" in peak_j.elements and "Cl" not in name_j:
                                    continue
                            if z_j != peak_j.z:
                                continue
                            m0_j = mz_j * z_j - delta_m_j
                            if m0_j < 0:
                                continue
                            if abs(m0_i - m0_j) <= mz_tolerance:
                                graph[id_i].append(id_j)
                                graph[id_j].append(id_i)
                                vertices[id_i, id_j].append((name_i, name_j))
                                vertices[id_j, id_i].append((name_j, name_i))
        return graph, vertices


    def _resolve_adducts(self, vertices, reverted_assignment):
        """
        the graph may contain multiple vertices between two nodes, where each vertex
        represents an adduct assignment for theses nodes.
        this method determines all consistent adduct assignments within each group.
        """

        assigned_adducts = defaultdict(list)

        for group_id in reverted_assignment.keys():
            nodes = reverted_assignment[group_id]

            sub_graph = restrict_graph(vertices, nodes)

            full_assignments = []
            for assignment in self.find_consistent_assignments(sub_graph, vertices):
                if len(assignment) == len(nodes):
                    full_assignments.append(assignment)

            # if the assignemnt is unique we add this information
            if len(full_assignments):
                for full_assignment in full_assignments:
                    for k, v in full_assignment.items():
                        assigned_adducts[k].append(v)

        return assigned_adducts

    def _enrich_table(self, table, adduct_cluster_assignment, assigned_adducts):
        """
        adds the calculated assignments as columns to the table
        """

        # only assign a adduct cluster if we found consitend adduct assignment:
        cluster_id_to_group_map = dict()
        for iso_cluster_id, adduct_cluster_id in adduct_cluster_assignment.items():
            if assigned_adducts.get(adduct_cluster_id):
                cluster_id_to_group_map[iso_cluster_id] = adduct_cluster_id

        if cluster_id_to_group_map:
            max_id = max(cluster_id_to_group_map.values())
        else:
            max_id = -1

        class AdductGroupAssigner(object):

            """mimmics stateful function"""

            def __init__(self, next_id=max_id + 1):
                self.next_id = next_id

            def __call__(self, id_):
                """ if we succeeded in assigning adducts to cluster we return the corresponding
                cluster id. else we count up for new_ids.
                """
                group_id = cluster_id_to_group_map.get(id_)
                if group_id is not None:
                    return group_id
                group_id = self.next_id
                cluster_id_to_group_map[id_] = group_id
                self.next_id += 1
                return group_id

        def assign_adducts(id_):
            adducts = assigned_adducts.get(id_)
            if adducts:
                return ", ".join(adducts)
            return None

        table.addColumn("adduct_group",
                        table.isotope_cluster_id.apply(AdductGroupAssigner()),
                        insertAfter="isotope_cluster_id")

        if assigned_adducts:
            table.addColumn("possible_adducts",
                            table.isotope_cluster_id.apply(assign_adducts),
                            insertAfter="adduct_group")
        else:
            table.addColumn("possible_adducts",
                            None,
                            insertAfter="adduct_group",
                            type_=str)


def assign_adducts(table):
    """
    Groups isotope clusters in respect of different adducts.
    Current version only supports data measured in negative mode.

    Table needs to be processed by hires.feature_regrouper before.
    """
    AdductAssigner("negative_mode").process(table)



if __name__ == "__main__":

    #table = emzed.io.loadTable("S9_isotope_clustered.table")
    #cnames1 = table.getColNames()
    import glob
    #for p in glob.glob("201311*.table"):
    p = "20140122_adduct_grouping.table"
    p = "isotope_clustered.table"
    p = "to_test_annotated.table"
    if p:
        print p
        table = emzed.io.loadTable(p)
        table = table.filter(table.isotope_cluster_id.isIn((84, 192, 654, 0, 5, 127)))
        table = table.extractColumns("id", "feature_id", "isotope_cluster_id",
                "carbon_isotope_shift", "unlabeled_isotope_shift", "mass_corr", "mz",
                "rt", "z", "area")
        emzed.io.storeTable(table, "for_adduct_assign_test.table", True)
        #emzed.gui.inspect(table)
        #table.dropColumns("adduct_group", "possible_adducts")
        AdductAssigner("negative_mode").process(table)
        #emzed.gui.inspect(table)
        table.sortBy(["adduct_group", "possible_adducts", "isotope_cluster_id"])
        table = table.extractColumns("id", "feature_id", "isotope_cluster_id", "adduct_group",
                "possible_adducts")
        print table
        #emzed.io.storeTable(table, p, True)
