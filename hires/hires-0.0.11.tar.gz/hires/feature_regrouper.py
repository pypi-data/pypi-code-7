# encoding: utf-8
from collections import defaultdict

import numpy as np
import emzed

from emzed.core.screen_utils import SectionPrinter, TimedPrinter, ProgressIndicator

from algorithms import assign_components, calculate_probable_iso_shifts


def match_traces(iso_shifts, distances, mz_tolerance):
    delta_C = emzed.mass.C13 - emzed.mass.C12

    ni, nj = distances.shape

    for transition_name, abundance, mass_shift in iso_shifts.rows:
        c_facs = np.round((distances - mass_shift) / delta_C)
        connection = np.abs(c_facs * delta_C - distances + mass_shift) < mz_tolerance
        for i in range(ni):
            for j in range(nj):
                if connection[i, j]:
                    nc = c_facs[i, j]
                    # either nc or transition
                    if nc and not transition_name:
                        yield i, j, transition_name, mass_shift, nc, abundance
                    elif not nc and transition_name:
                        yield i, j, transition_name, mass_shift, nc, abundance


def find_and_record_match(mzs_0, mzs_1, z, iso_shifts, ids_0, ids_1, graph, mz_tolerance,
                          stop_after_first_hit=False, max_c_gap=1):

    distances = (mzs_0[:, None] - mzs_1[None, :]) * z

    found_match = False

    for i, j, transition_name, mass_shift, nc, __ in match_traces(iso_shifts, distances, mz_tolerance):
        if abs(nc) > max_c_gap + 1:  # gap to big
            continue
        ii = ids_0[i]
        jj = ids_1[j]
        if ii == jj:
            continue
        graph[ii].add(jj)
        graph[jj].add(ii)
        found_match = True
        if stop_after_first_hit:
            return True, transition_name
    return found_match, None


def feature_regrouper(table, min_abundance=1e-3, halogens=["Cl"], max_c_gap=1, mz_tolerance=8e-4,
                      rt_tolerance=5):
    """
    postprocessor for features created by emzeds wrapper of openms metabo feature finder.
    here we split feature groups and / or merge them using high resolution mass differences.

    min_abundance is a threshold which determines the isotope shifts considered in this
    process.

    max_c_gap is the maximum delta_c gap allowed for grouping features, eg masses
    100, 102 + 2 * C{12,13} has a gap one.
    """

    SectionPrinter.print_("RUN FEATURE GROUPER")

    assert "feature_id" in table.getColNames(), table.getColNames()
    assert "rt" in table.getColNames(), table.getColNames()
    assert "mz" in table.getColNames(), table.getColNames()
    assert "z" in table.getColNames(), table.getColNames()
    assert "area" in table.getColNames(), table.getColNames()

    print
    printer = TimedPrinter()
    print
    print "considered isotope shifts:"
    print

    iso_shifts = calculate_probable_iso_shifts(min_abundance, ("H", "N", "O", "P", "S"), ("Cl", ))
    iso_shifts.print_()
    print

    features = list()
    proposed_group_id = dict()
    graph = defaultdict(set)

    #
    # build initial graph for each feature from metabo ff
    #

    printer.print_("build graph within each feature")

    progress_indicator = ProgressIndicator(len(set(table.feature_id.values)))

    class Feature(object):

        """
        this is a short hand replacement for
            namedtuple('Feature', 'fid ids mzs mz_min mz_max rt z')
        which does not allow modifiaction of attributes, which we introduces below
        """

        def __init__(self, fid, ids, mzs, mz_min, mz_max, rt, z):
            self.fid = fid
            self.ids = ids
            self.mzs = mzs
            self.mz_min = mz_min
            self.mz_max = mz_max
            self.rt = rt
            self.z = z

        def __iter__(self):
            """ mimics tuple unpacking """
            yield self.fid
            yield self.ids
            yield self.mzs
            yield self.mz_min
            yield self.mz_max
            yield self.rt
            yield self.z

        def __str__(self):
            return "Feature(fid=%d, ids=%s, mzs=%s, mz_min=%s, mz_max=%s, rt=%s, z=%s)" % tuple(self)

    for feature in table.splitBy("feature_id"):
        progress_indicator.next()

        feature.sortBy("id")

        fid = feature.feature_id.uniqueValue()

        ids = feature.id.values
        for id_ in ids:
            proposed_group_id[id_] = fid

        mzs = np.array(feature.mz.values)
        z = feature.z.uniqueValue()
        rt = feature.rt.uniqueValue()

        if len(mzs) == 1:
            z = 0

        features.append(Feature(fid, ids, mzs, min(mzs), max(mzs), rt, z))

        if z is None or z == 0 or len(mzs) == 1:
            continue

        find_and_record_match(mzs, mzs, z, iso_shifts, ids, ids, graph, mz_tolerance,
                              stop_after_first_hit=False, max_c_gap=0)

    progress_indicator.finish()
    print

    features.sort(key=lambda feat: feat.rt)

    #
    # add vertices for inter-feature dependences to graph
    #

    n = len(features)
    printer.print_("build global graph between features:")
    progress_indicator = ProgressIndicator(n)

    # maybe we transform z=0 to some other z if it fits:
    assigned_zs = dict()
    for feature in features:
        for id_ in feature.ids:
            assigned_zs[id_] = feature.z

    for i, feat_0 in enumerate(features):

        progress_indicator.set(i)

        fid_0, ids_0, mzs_0, mz_min_0, mz_max_0, rt_0, z_0 = feat_0
        for feat_1 in features[i + 1:]:
            fid_1, ids_1, mzs_1, mz_min_1, mz_max_1, rt_1, z_1 = feat_1
            if rt_1 > rt_0 + rt_tolerance:
                # this works because features are sorted by rt
                break

            if mz_min_1 > mz_max_0 + 20:
                continue

            if mz_min_0 > mz_max_1 + 20:
                continue

            if z_0 > 0 and z_1 > 0 and z_0 != z_1:
                continue

            if z_0 == z_1 and z_0 > 0:
                z = z_0
                find_and_record_match(mzs_0, mzs_1, z, iso_shifts, ids_0, ids_1, graph,
                                      mz_tolerance, stop_after_first_hit=True, max_c_gap=max_c_gap)
            elif z_0 == 0 and z_1 > 0 or z_0 > 0 and z_1 == 0:
                z = max(z_0, z_1)
                found, __ = find_and_record_match(mzs_0, mzs_1, z, iso_shifts, ids_0, ids_1, graph,
                                                  mz_tolerance, stop_after_first_hit=True,
                                                  max_c_gap=max_c_gap)
                if found:
                    for id_ in feat_0.ids:
                        assigned_zs[id_] = z
                    for id_ in feat_1.ids:
                        assigned_zs[id_] = z
                    feat_0.z = z
                    feat_1.z = z
                    z_0 = z
                    z_1 = z
            else:
                assert z_0 == 0 and z_1 == 0, (z_0, z_1)
                found_z = None
                # first we look for pure carbon shift starting with smaller gaps to larger gaps
                for z in (3, 2, 1):
                    found, transition_name = find_and_record_match(mzs_0, mzs_1, z, iso_shifts,
                                                                   ids_0, ids_1, graph,
                                                                   mz_tolerance,
                                                                   stop_after_first_hit=True,
                                                                   max_c_gap=0)
                    if found and transition_name == "":
                        found_z = z
                        break
                # if we need other natural abundces to explain the shift, we do not want to
                # prefer eg a double Cl shift with z=2 over a single Cl shift with z=1,
                # so we try z in a different order:
                if found_z is None:
                    for z in (1, 2, 3):
                        found, transition_name = find_and_record_match(mzs_0, mzs_1, z, iso_shifts,
                                                                       ids_0, ids_1, graph,
                                                                       mz_tolerance,
                                                                       stop_after_first_hit=True,
                                                                       max_c_gap=0)
                        if found:
                            found_z = z
                            break

                if found_z is not None:
                    for id_ in feat_0.ids:
                        assigned_zs[id_] = found_z
                    for id_ in feat_1.ids:
                        assigned_zs[id_] = found_z
                    feat_0.z = found_z
                    feat_1.z = found_z
                    z_0 = found_z
                    z_1 = found_z
                    break
    progress_indicator.finish()
    print

    #
    # calculate isotope_clusters and assign their ids to input table
    #

    printer.print_("decompose graph")
    assignments, __ = assign_components(graph, proposed_labels=proposed_group_id)

    printer.print_("update table")

    class Assigner(object):

        """
        Override __call__, so an instance of this class acts like a state full function.
        The state is the next isotope_cluster_id to assign if not found in self.assignments
        """

        def __init__(self, assignments):
            if len(assignments):
                self.max_isotope_cluster_id = max(assignments.values())
            else:
                self.max_isotope_cluster_id = 0
            self.assignments = assignments

        def __call__(self, id_):
            if id_ in self.assignments:
                return assignments[id_]
            self.max_isotope_cluster_id += 1
            return self.max_isotope_cluster_id

    assigner = Assigner(assignments)
    table.addColumn("isotope_cluster_id", table.id.apply(assigner), insertAfter="feature_id")
    table.replaceColumn("z", table.id.apply(assigned_zs.get))

    # fix z value for features with one masstrace:
    iso_cluster_col = table.isotope_cluster_id
    cluster_has_size_one = (iso_cluster_col.count.group_by(iso_cluster_col) == 1)
    table.replaceColumn("z", cluster_has_size_one.thenElse(0, table.z))

    progress_indicator = ProgressIndicator(len(set(table.isotope_cluster_id.values)))
    collected = []

    for feature in table.splitBy("isotope_cluster_id"):
        progress_indicator.next()
        zs = set(feature.z)
        assert len(zs) <= 1, "this should never happen, looks like a bug in the algorithm"
        z = zs.pop()
        if len(feature) == 1 or z == 0:
            n = len(feature)
            feature.addColumn("mass_corr", n * (None,), type_=float, format_="%+.5f",
                              insertBefore="mz")
            feature.addColumn("unlabeled_isotope_shift", n * (None,), type_=str,
                              insertAfter="isotope_cluster_id")
            feature.addColumn("carbon_isotope_shift", n * (None,), type_=str,
                              insertAfter="isotope_cluster_id")
            collected.append(feature)
            continue

        feature.sortBy("mz")

        # determine values for columns "isotope_shift" and "mass_corr"
        ids = feature.id.values
        mzs = np.array(feature.mz.values)
        distances = (mzs[:, None] - mzs[None, :]) * z
        masscorrs = [None] * len(ids)
        unlabeled_isotope_shifts = [None] * len(ids)
        carbon_isotope_shifts = [None] * len(ids)

        # first we assign positive carbon shifts and positive shifts caused by natural
        # abundances of other elements:
        delta_C = emzed.mass.C13 - emzed.mass.C12
        for i, j, transition_name, mass_shift, nc, abundance in match_traces(iso_shifts, distances, mz_tolerance):
            if nc == 0:
                # so we have a natural abundance of element != carbon:
                masscorrs[i] = mass_shift
                unlabeled_isotope_shifts[i] = "[%d] + %s" % (ids[j], transition_name)
            elif nc > 0:
                # we have a positive carbon shift
                masscorrs[i] = nc * delta_C
                if nc > 1:
                    carbon_isotope_shifts[i] = "[%d] + %d C{12,13}" % (ids[j], nc)
                elif nc == 1:
                    carbon_isotope_shifts[i] = "[%d] + C{12,13}" % (ids[j],)

        # second:
        # we try to assign "negative shifts" of natural isotopes shifts != carbon, but only
        # if we failed in step one above:
        for i, j, transition_name, mass_shift, nc, abundance in match_traces(iso_shifts, distances, mz_tolerance):
            if carbon_isotope_shifts[j] is not None:
                continue
            if unlabeled_isotope_shifts[j] is not None:
                continue
            if nc == 0:
                masscorrs[j] = -mass_shift
                unlabeled_isotope_shifts[j] = "[%d] - %s" % (ids[i], transition_name)

        feature.addColumn("mass_corr", masscorrs, type_=float, format_="%+.5f", insertBefore="mz")
        feature.addColumn("unlabeled_isotope_shift", unlabeled_isotope_shifts, type_=str,
                          insertAfter="isotope_cluster_id")
        feature.addColumn("carbon_isotope_shift", carbon_isotope_shifts, type_=str,
                          insertAfter="isotope_cluster_id")
        collected.append(feature)

    progress_indicator.finish()
    print
    printer.print_("merge tables")

    result = emzed.utils.mergeTables(collected)

    print
    printer.print_("finished calculation")

    SectionPrinter.print_("FINISHED FEATURE GROUPER")
    return result


if __name__ == "__main__":
    # t = emzed.io.loadTable("../tests/b1_ambiguous.table")
    # t = emzed.io.loadTable("for_test.table")
    # t = emzed.io.loadTable("isotope_regroup_problem.table")
    t = emzed.io.loadTable("/home/uweschmitt/tmp/gegrouped_awwa_z_is_null.table")
    t.dropColumns("isotope_cluster_id")
    t.dropColumns("carbon_isotope_shift")
    t.dropColumns("unlabeled_isotope_shift")
    t.dropColumns("mass_corr")

    t.info()
    # t = t.filter(t.mz <= 298 )
    # t = t.filter(t.mz >= 292 )
    # t = t.filter(t.feature_id == 0)
    # t = t.extractColumns("id", "feature_id", "mz", "z", "rt", "area")
    # emzed.io.storeTable(t, "for_test.table")
    # exit()
    # t.sortBy("id")
    # from annotate_transitions import annotate_isotope_shifts
    # t = annotate_isotope_shifts(t, halogens=("Cl",))
    # emzed.gui.inspect(t)
    t = feature_regrouper(t)
    emzed.io.storeTable(t, "to_test_annotated.table", True)
    emzed.gui.inspect(t)
