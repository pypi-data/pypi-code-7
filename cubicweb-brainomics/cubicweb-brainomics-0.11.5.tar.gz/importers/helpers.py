# copyright 2012 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

import csv
import json
import pickle
import re
from itertools import chain


def get_image_info(image_path, get_tr=True):
    """Return the image info readed from the image using Nibabel"""
    import nibabel as nb
    img = nb.load(image_path)
    data = {}
    data['voxel_res_x'] = float(img.get_header()['pixdim'][1])
    data['voxel_res_y'] = float(img.get_header()['pixdim'][2])
    data['voxel_res_z'] = float(img.get_header()['pixdim'][3])
    data['shape_x'] = int(img.get_shape()[0])
    data['shape_y'] = int(img.get_shape()[1])
    data['shape_z'] = int(img.get_shape()[2])
    data['shape_t'] = int(img.get_shape()[3]) if len(img.get_shape()) == 4 else None
    data['affine'] = pickle.dumps(img.get_affine().tolist())
    desc = str(img.get_header()['descrip'])
    # Use desc ?
    try:
        if get_tr:
            tr, te = re.findall(
                'TR=(.*)ms.*TE=(.*)ms', desc)[0]
            data['tr'] = float(tr)
            data['te'] = float(te)
    except Exception, e:
        data['tr'] = None
        data['te'] = None

    return data


def import_genes(ref_chr_path, ref_gene_path):
    """Import genes"""
    chromosomes = json.load(open(ref_chr_path))
    ref_gene = []
    for row in csv.reader(open(ref_gene_path), delimiter='\t'):
        gene = {}
        gene['name'] = unicode(row[0])
        gene['gene_id'] = unicode(row[0])
        gene['uri'] = None
        gene['start_position'] = int(row[1])
        gene['stop_position'] = int(row[2])
        gene['chromosome'] = row[3].split('_')[0]
        ref_gene.append(gene)
    return ref_gene


def import_chromosomes(ref_chr_path):
    """Import chromosomes"""
    chromosomes = json.load(open(ref_chr_path))
    chrs = []
    for chr_id in chromosomes:
        chr = {}
        chr['name'] = u'chr%s' % chromosomes[chr_id].upper()
        chr['identifier'] = unicode(chr['name'])
        chrs.append(chr)
    return chrs


def import_snps(ref_chr_path, ref_snp_path):
    """Import snps"""
    chromosomes = json.load(open(ref_chr_path))
    snps = []
    for row in csv.reader(open(ref_snp_path), delimiter='\t'):
        snp = {}
        if row[0] == '0':
            continue
        chr_id = chromosomes[row[0]]
        snp['rs_id'] = unicode(row[1])
        snp['position'] = int(row[3])
        snp['chromosome'] = u'chr%s' % chr_id.upper()
        snps.append(snp)
    return snps


def generate_container_relations(session, cursor=None):
    """ Generate the relations required for container """
    # XXX Get the cursor of on the current cnx for sqlite tests...
    cursor = session.system_sql('SELECT * FROM cw_cwetype LIMIT 1')
    for rtype, rset in chain(_generate_of_subject_relations(session),
                             _generate_in_assessment_relations(session)):
        _push_container_relations(cursor, rtype, rset)
    session.commit()


def _push_container_relations(cursor, rtype, rset):
    """ Push the relations required by container """
    data = {}
    for meid, aeid, etype in rset:
        data.setdefault(etype,  []).append({'e': meid, 'a': aeid})
    for etype, eids in data.iteritems():
        cursor.executemany('UPDATE cw_%s SET cw_%s=%%(a)s WHERE cw_eid=%%(e)s'
                           % (etype.lower(), rtype), eids)


def _generate_in_assessment_relations(session):
    """ Generate the 'in_assessment' relations used for container """
    # Measures
    rset = session.execute('Any X, A, N WITH X, A, N BEING ('
                           '(Any X,A,N WHERE X is E, E name N, A generates X) '
                           'UNION (Any X,A,N WHERE X is E, E name N, A uses X))')
    yield ('in_assessment', rset)
    # Files
    rset = session.execute('Any X, A, N WITH X, A, N BEING ('
                           '(Any X,A,N WHERE X is E, E name N, M configuration_files X, '
                           'M in_assessment A) '
                           'UNION (Any X,A,N WHERE X is E, E name N, M results_files X, '
                           'M in_assessment A))')
    yield ('in_assessment', rset)
    # Measures relations
    for rtype in ('generates', 'uses'):
        rset = session.execute('Any X, A, N WITH X, A, N BEING ('
                               '(Any X,A,N WHERE X is E, E name N, X measure M, A %(r)s M) '
                               'UNION (Any X,A,N WHERE X is E, E name N, X comments M, '
                               'A %(r)s M))' % {'r': rtype})
        yield ('in_assessment', rset)
        # Assessment Files
        rset = session.execute('Any X, A, N WITH X, A, N BEING ('
                               '(Any X,A,N WHERE X is E, E name N, A %(r)s M, '
                               'M configuration_files X) '
                               'UNION (Any X,A,N WHERE X is E, E name N, A %(r)s M, '
                               'M results_files X))'
                                % {'r': rtype})
        yield ('in_assessment', rset)


def _generate_of_subject_relations(session):
    """ Generate the 'of_subject' relations used for container """
    # Diagnostic, Therapy
    rset = session.execute('Any X, A, N WITH X, A, N BEING ('
                           '(Any X, A, N WHERE A related_diagnostics X, X is E, E name N) '
                           'UNION (Any X, A, N WHERE A related_therapies X, X is E, E name N))')
    yield ('of_subject', rset)
    # Drug take
    rset = session.execute('Any X, A, N WITH X, A, N BEING ('
                           'Any X, A, N WHERE A related_therapies T, '
                           'X taken_in_therapy T, X is E, E name N)')
    yield ('of_subject', rset)
    # Admission
    rset = session.execute('Any X, A, N WITH X, A, N BEING ('
                           'Any X, A, N WHERE X admission_of A, X is E, E name N)')
    yield ('of_subject', rset)
    # Admission step
    rset = session.execute('Any X, A, N WITH X, A, N BEING ('
                           'Any X, A, N WHERE S admission_of A, X step_of S, X is E, E name N)')
    yield ('of_subject', rset)
    # Add samples
    rset = session.execute('Any X, A, N WITH X, A, N BEING ('
                           'Any X, A, N WHERE A related_samples X, X is E, E name N)')
    yield ('of_subject', rset)
