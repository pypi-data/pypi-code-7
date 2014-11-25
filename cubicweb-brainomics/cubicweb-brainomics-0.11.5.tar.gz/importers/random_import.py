# -*- coding: utf-8 -*-
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
from random import randrange
from optparse import OptionParser
from datetime import timedelta, datetime

import numpy.random as nr

from cubicweb.dataimport import SQLGenObjectStore

from cubes.brainomics.importers.helpers import (get_image_info, import_genes,
                                                import_chromosomes, import_snps)

#http://www.housemd-guide.com/characters/houserules.php
DR_HOUSE_QUOTES = (u"We treat it. If she[he] gets better we know that we're right.",
                   u"Patients always want proof, we're not making cars here, we don't give guarantees.",
                   u"Pretty much all the drugs I prescribe are addictive and dangerous.",
                   u"Patients sometimes get better. You have no idea why, but unless you give a reason they won't pay you. Anybody notice if there's a full moon? ... let's rule out the lunar god and go from there.",
                   u"Occam's Razor.  The simplest explanation is almost always somebody screwed up.",
                   u"I take risks, sometimes patients die. But not taking risks causes more patients to die, so I guess my biggest problem is I've been cursed with the ability to do the math.",
                   u"Idiopathic, from the Latin meaning we're idiots cause we can't figure out what's causing it.",
                   u"If he gets better, I'm right, if he dies, you're right.",
                   u"The eyes can mislead, the smile can lie, but the shoes always tell the truth.",
                   u"Hang up a shingle and condemn the narrowness and greed of Western medicine, you'd make a damn fine living.",
                   u"It is the nature of medicine that you are going to screw up.",
                   u"Right and wrong do exist. Just because you don't know what the right answer is — maybe there's even no way you could know what the right answer is — doesn't make your answer right or even okay. It's much simpler than that. It's just plain wrong.",
                   u"You know what's worse than useless? Useless and oblivious.",
                   u"It is in the nature of medicine that you are gonna screw up. You are gonna kill someone. If you can't handle that reality, pick another profession. Or finish medical school and teach.",
                   u"If it works, we're right. If he dies, it was something else.",
                   u"If her DNA was off by one percentage point she'd be a dolphin.",)

DR_HOUSE_QUOTES_CONCLUSIONS = (u"Never met a diagnostic study I couldn't refute.",
                               u"Never trust doctors.",
                               u"That's a catchy diagnosis, you could dance to that.",
                               u"Tragedies happen.",
                               u"Weird works for me.",
                               u"In case I'm wrong. It has happened.",
                               u"It does tell us something. Though I have no idea what.",
                               u"I solved the case, my work is done.",
                               u"Tests take time. Treatment's quicker.",
                               u"Welcome to the end of the thought process.",
                               u"Sometimes we can't see why normal isn't normal.",
                               u"You want to make things right? Too bad. Nothing's ever right.",
                               u"New is good. Because old ended in death.")


###############################################################################
### DATA GENERATION CONFIGURATION #############################################
###############################################################################
NB_SUBJECTS = 1000
NB_SUBJECTS_GROUPS = 5
AGE_DATETIMES = (datetime.strptime('1/1/1930 1:30 PM', '%m/%d/%Y %I:%M %p'),
                 datetime.strptime('1/1/1990 4:50 AM', '%m/%d/%Y %I:%M %p'))
PROJECT_DATETIMES = (datetime.strptime('1/1/2010 1:30 PM', '%m/%d/%Y %I:%M %p'),
                     datetime.strptime('1/1/2013 4:50 AM', '%m/%d/%Y %I:%M %p'))
SEX = {0: u'male', 1: u'female'}
HANDEDNESS = {0: u'right', 1: u'left', 2: u'ambidextrous', 3: u'mixed'}


###############################################################################
### UTILITY FUNCTIONS #########################################################
###############################################################################
def random_date(_type=None, start=None, end=None):
    """
    This function will return a random datetime between two datetime
    objects.
    From http://stackoverflow.com/questions/553303/generate-a-random-date-between-two-other-dates
    """
    if start:
        end = PROJECT_DATETIMES[1]
    elif _type=='age':
        start, end = AGE_DATETIMES[0], AGE_DATETIMES[1]
    else:
        start, end = PROJECT_DATETIMES[0], PROJECT_DATETIMES[1]
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return (start + timedelta(seconds=random_second))

def create_protocol(store, study, identifier):
    """ Create a protocol """
    date = random_date()
    protocol_eid = store.create_entity('Protocol', identifier=identifier,
                                       start_datetime=date).eid
    store.relate(protocol_eid, 'related_study', study, subjtype='Protocol')
    return protocol_eid

def import_questionnaire(store, subject_eid, center_eid, study_eid,
                         questionnaire_eid, questions, label, protocol_eid):
    date = random_date()
    assessment = store.create_entity('Assessment', datetime=date)
    store.relate(assessment.eid, 'protocols', protocol_eid, subjtype='Assessment')
    store.relate(assessment.eid, 'related_study', study_eid, subjtype='Assessment')
    store.relate(center_eid, 'holds', assessment.eid)
    store.relate(subject_eid, 'concerned_by', assessment.eid)
    user_ident = nr.randint(10)
    user_ident = u'parent' if user_ident>8 else u'subject'
    q_qrun = store.create_entity('QuestionnaireRun',
                                   user_ident=user_ident, datetime=date,
                                   iteration=1, completed=True, valid=True,
                                   instance_of=questionnaire_eid)
    store.relate(q_qrun.eid, 'related_study', study_eid, subjtype='QuestionnaireRun')
    store.relate(q_qrun.eid, 'concerns', subject_eid, subjtype='QuestionnaireRun')
    store.relate(assessment.eid, 'generates', q_qrun.eid, subjtype='Assessment')
    for name, (question, _min, _max) in questions.iteritems():
        score_value = store.create_entity('Answer', value=nr.randint(_min, _max),
                                          question=question, datetime=date,
                                          questionnaire_run=q_qrun.eid)

def import_genomic(store, subject_eid, center_eid, study_eid, platform, type, protocol_eid):
    date = random_date()
    assessment = store.create_entity('Assessment', datetime=date)
    store.relate(assessment.eid, 'protocols', protocol_eid, subjtype='Assessment')
    store.relate(assessment.eid, 'related_study', study_eid, subjtype='Assessment')
    store.relate(center_eid, 'holds', assessment.eid)
    store.relate(subject_eid, 'concerned_by', assessment.eid)
    measure = store.create_entity('GenomicMeasure', type=type,
                                  platform=platform if platform else None,
                                  completed=True, valid=True, related_study=study_eid)
    _file = store.create_entity('ExternalFile', name='genomic_%s' % subject_eid,
                                absolute_path=False, filepath=u'%s/genomics.tar.gz' % subject_eid)
    store.relate(measure.eid, 'results_files', _file.eid)
    store.relate(measure.eid, 'concerns', subject_eid, subjtype='GenomicMeasure')
    store.relate(assessment.eid, 'generates', measure.eid, subjtype='Assessment')
    return measure.eid

def create_genomic_region(store):
    """ Add a GenomicRegion """
    start = nr.randint(1000000)
    stop = nr.randint(start, 1000000)
    chromosome = store.rql('Any X ORDERBY RANDOM() LIMIT 1 WHERE X is Chromosome')
    entity = store.create_entity('GenomicRegion', start=start, stop=stop,
                                 width=stop-start,
                                 cytoband_start=u'q+%s' % start,
                                 cytoband_stop=u'q+%s' % stop,
                                 chromosome=chromosome[0][0])
    for gene in store.rql('Any X ORDERBY RANDOM() LIMIT 100 WHERE X is Gene, '
                          'X chromosomes Y, Y eid %(e)s', {'e': chromosome[0][0]}):
        store.relate(entity.eid, 'genes', gene[0], subjtype='GenomicRegion')
    return entity.eid

def import_cgh_results(store, subject_eid, center_eid, study_eid, platform, protocol_eid):
    """ Add CGH results """
    measure = import_genomic(store, subject_eid, center_eid, study_eid,
                             platform, u'CGH', protocol_eid)
    for region in range(nr.randint(100)):
        region = create_genomic_region(store)
        store.create_entity('CghResult', cgh_ratio=nr.random(), log2_ratio=nr.random(),
                            status=(u'L', u'G')[nr.randint(1)],
                            numprobes=nr.randint(100),
                            related_measure=measure, genomic_region=region)

def import_sequencing_results(store, subject_eid, center_eid, study_eid, platform, protocol_eid):
    """ Add CGH results """
    measure = import_genomic(store, subject_eid, center_eid, study_eid,
                             platform, u'Sequencing', protocol_eid)
    for mutation in range(nr.randint(100)):
        gene = store.rql('Any X ORDERBY RANDOM() LIMIT 1 WHERE X is Gene')[0][0]
        store.create_entity('Mutation', position_in_gene=nr.randint(1000),
                            mutation_type=u'SNP', ploidy=(u'Het', u'Hom')[nr.randint(1)],
                            biological_classification=u'Substitution',
                            related_measure=measure,
                            related_gene=gene,
                            reference_base=(u'A', u'T', u'G', u'C')[nr.randint(3)],
                            variant_base=(u'A', u'T', u'G', u'C')[nr.randint(3)],
                            variant_frequency=100*nr.random())

def import_anat_images(store, subject_eid, center_eid, study_eid, mri_1, mri_2, protocol_eid):
    date = random_date()
    assessment = store.create_entity('Assessment', datetime=date)
    store.relate(assessment.eid, 'protocols', protocol_eid, subjtype='Assessment')
    store.relate(assessment.eid, 'related_study', study_eid, subjtype='Assessment')
    store.relate(center_eid, 'holds', assessment.eid)
    store.relate(subject_eid, 'concerned_by', assessment.eid)
    device = nr.randint(1)
    mri_data = store.create_entity('MRIData',
                                   shape_x=128, shape_y=128, shape_z=64,
                                   sequence=u'T1',
                                   voxel_res_x=1.5, voxel_res_y=1.5, voxel_res_z=1.5).eid
    scan_data = store.create_entity('Scan', has_data=mri_data,
                                    related_study=study_eid,
                                    label=u'anatomy', type=u'normalized T1',
                                    format=u'nii.gz',
                                    uses_device=mri_1 if device else mri_2,
                                    completed=True, valid=True).eid
    _file = store.create_entity('ExternalFile', name='anat_%s' % subject_eid,
                                absolute_path=False, filepath=u'%s/anat.nii.gz' % subject_eid)
    store.relate(scan_data, 'results_files', _file.eid)
    store.relate(scan_data, 'concerns', subject_eid, subjtype='Scan')
    store.relate(assessment.eid, 'generates', scan_data, subjtype='Assessment')

def import_fmri_images(store, subject_eid, center_eid, study_eid, mri_1, mri_2, protocol_eid):
    date = random_date()
    assessment = store.create_entity('Assessment', datetime=date)
    store.relate(assessment.eid, 'protocols', protocol_eid, subjtype='Assessment')
    store.relate(assessment.eid, 'related_study', study_eid, subjtype='Assessment')
    store.relate(center_eid, 'holds', assessment.eid)
    store.relate(subject_eid, 'concerned_by', assessment.eid)
    device = nr.randint(1)
    mri_data = store.create_entity('MRIData',
                                   sequence=u'EPI',
                                   shape_x=128, shape_y=128, shape_z=64, shape_t=256,
                                   voxel_res_x=1.5, voxel_res_y=1.5, voxel_res_z=1.5).eid
    scan_data = store.create_entity('Scan', has_data=mri_data,
                                    related_study=study_eid,
                                    label=u'bold', type=u'preprocessed fMRI',
                                    format=u'nii.gz',
                                    uses_device=mri_1 if device else mri_2,
                                    completed=True, valid=True).eid
    _file = store.create_entity('ExternalFile', name='bold_%s' % subject_eid,
                                absolute_path=False, filepath=u'%s/bold.nii.gz' % subject_eid)
    store.relate(scan_data, 'results_files', _file.eid)
    store.relate(scan_data, 'concerns', subject_eid, subjtype='Scan')
    store.relate(assessment.eid, 'generates', scan_data, subjtype='Assessment')

def import_constrat_images(store, subject_eid, center_eid, study_eid, mri_1, mri_2, protocol_eid):
    date = random_date()
    assessment = store.create_entity('Assessment', datetime=date)
    store.relate(assessment.eid, 'protocols', protocol_eid, subjtype='Assessment')
    store.relate(assessment.eid, 'related_study', study_eid, subjtype='Assessment')
    store.relate(center_eid, 'holds', assessment.eid)
    store.relate(subject_eid, 'concerned_by', assessment.eid)
    for ind, label in enumerate((u'Audio-Video', u'Text reading', u'Video reading',
                                 u'Social behavior', u'Audio interaction')):
        for smap in (u'c map', u't map'):
            mri_data = store.create_entity('MRIData',
                                           sequence=u'EPI',
                                           shape_x=128, shape_y=128, shape_z=64,
                                           voxel_res_x=1.5, voxel_res_y=1.5, voxel_res_z=1.5).eid
            scan_data = store.create_entity('Scan', has_data=mri_data,
                                            related_study=study_eid,
                                            label=label, type=smap,
                                            format=u'nii.gz',
                                            completed=True, valid=True).eid
            filepath = '%s/%s_%s.nii.gz' % (smap.replace(' ', ''), subject_eid, ind)
            _file = store.create_entity('ExternalFile', name='scan_%s_%s' % (subject_eid, ind),
                                        absolute_path=False, filepath=filepath)
            store.relate(scan_data, 'results_files', _file.eid)
            store.relate(scan_data, 'concerns', subject_eid, subjtype='Scan')
            store.relate(assessment.eid, 'generates', scan_data, subjtype='Assessment')


###############################################################################
### IMPORT ####################################################################
###############################################################################
if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-c", "--chromosomes", dest="chromosomes",
                      help="Json file of chromosomes")
    parser.add_option("-g", "--genes", dest="genes",
                      help="Json file of genes")
    parser.add_option("-s", "--snps", dest="snps",
                      help="Json file of snps")
    (options, args) = parser.parse_args(__args__)

    store = SQLGenObjectStore(session)


    ###############################################################################
    ### GENETICS DATA #############################################################
    ###############################################################################
    platform = None
    if options.chromosomes:
        chrs = import_chromosomes(options.chromosomes)
        chr_map = {}
        for _chr in chrs:
            print 'chr', _chr['name']
            _chr = store.create_entity('Chromosome', **_chr)
            chr_map.setdefault(_chr['name'], _chr.eid)
        store.flush()
        if options.genes:
            genes = import_genes(options.chromosomes, options.genes)
            for gene in genes:
                print 'gene', gene['name'], gene['chromosome']
                chromosome = gene.pop('chromosome')
                chromosome = chr_map.get(chromosome)
                if not chromosome:
                    continue
                gene = store.create_entity('Gene', **gene)
                store.relate(gene.eid, 'chromosomes', chromosome)
            store.flush()
        if options.snps:
            snps = import_snps(options.chromosomes, options.snps)
            snp_eids = []
            for ind, snp in enumerate(snps):
                print 'snp', snp['rs_id']
                snp['chromosome'] = chr_map[snp['chromosome']]
                snp = store.create_entity('Snp', **snp)
                snp_eids.append(snp.eid)
                if ind and ind % 100000 == 0:
                    store.flush()
            store.flush()
        else:
            snp_eids = []
        # Platform
        platform = {'identifier': 'Affymetrix_6.0'}
        platform = store.create_entity('GenomicPlatform', **platform).eid
        for snp_eid in snp_eids:
            store.relate(platform, 'related_snps', snp_eid)
        store.flush()

    ###############################################################################
    ### STUDY/PI/CENTERS ##########################################################
    ###############################################################################
    study = store.create_entity('Study', name=u'Demo study',
                                data_filepath=u'/tmp/demo_data',
                                description=u'Demo study with random data',
                                keywords=u'demo;random;semantic').eid
    pi_1 = store.create_entity('Investigator', identifier=u'pi_1',
                               firstname=u'Angus', lastname=u'Young', title=u'PhD',
                               institution=u'Research Center', department=u'Cognitive Sciences').eid
    pi_2 = store.create_entity('Investigator', identifier=u'pi_2',
                               firstname=u'Malcom', lastname=u'Young', title=u'MD',
                               institution=u'Research Center', department=u'Cognitive Sciences').eid
    pi_3 = store.create_entity('Investigator', identifier=u'pi_3',
                               firstname=u'Brian', lastname=u'Jonhson', title=u'PhD',
                               institution=u'Research Center', department=u'IT').eid
    pi_4 = store.create_entity('Investigator', identifier=u'pi_4',
                               firstname=u'Phil', lastname=u'Rudd', title=u'PhD',
                               institution=u'Research Center', department=u'IT').eid
    center = store.create_entity('Center', identifier=u'center', name=u'Demo center',
                                 department=u'Medical research', city=u'Paris',
                                 country=u'France').eid
    mri_1 = store.create_entity('Device', name=u'Magnetom', model=u'Trio',
                                manufacturer=u'Siemens',
                                serialnum=1234, hosted_by=center).eid
    mri_2 = store.create_entity('Device', name=u'Ingenia', model=u'3.0 T',
                                manufacturer=u'Philips',
                                serialnum=4321, hosted_by=center).eid


    ###############################################################################
    ### SCOREDEFS #################################################################
    ###############################################################################
    score_defs = {}
    possible_values = u'0 = Control; 1 = Autism; 2 = Aspergers; 3 = PDD-NOS; 4 = Aspergers or PDD-NOS'
    score_defs['dsm_iv_tr'] = (store.create_entity('ScoreDefinition', name=u'DSM-IV-TR Diagnostic Category', category=u'biological', type=u'numerical', possible_values=possible_values).eid, 0, 4)
    score_defs['scq_total'] = (store.create_entity('ScoreDefinition', name=u'Social Communication Questionnaire Total', category=u'behavioral', type=u'numerical', possible_values=u'0-39').eid, 0, 39)
    score_defs['aq_total'] = (store.create_entity('ScoreDefinition', name=u'Total Raw Score of the Autism Quotient', category=u'behavioral', type=u'numerical', possible_values=u'0-50').eid, 0, 50)
    score_defs['fiq_WASI'] = (store.create_entity('ScoreDefinition', name=u'FIQ Standard Score - WASI', category=u'FIQ', type=u'numerical').eid, 50, 160)
    score_defs['viq_WASI'] = (store.create_entity('ScoreDefinition', name=u'VIQ Standard Score - WASI', category=u'VIQ', type=u'numerical').eid, 55, 160)
    score_defs['piq_WASI'] = (store.create_entity('ScoreDefinition', name=u'PIQ Standard Score - WASI', category=u'PIQ', type=u'numerical').eid, 53, 160)


    store.flush()


    ###############################################################################
    ### QUESTIONNAIRES ############################################################
    ###############################################################################
    # ADOS
    name = u'Autism Diagnostic Observation Schedule Module (ADOS)'
    ados_questionnaire_eid = store.create_entity('Questionnaire', name=name, language=u'en', version=u'v 0.2.1', identifier=u'ados', type=u'behavioral').eid
    ados_questions = {}
    text = u'Autism Diagnostic Observation Schedule Module'
    ados_questions['ados_module'] = (store.create_entity('Question', identifier=u'ados_module', position=0, text=text, type=u'numerical', questionnaire=ados_questionnaire_eid, possible_answers=u'1-4').eid, 1, 4)
    text = u'Classical Total ADOS Score (Communication subscore + Social Interaction subscore)'
    ados_questions['ados_total'] = (store.create_entity('Question', identifier=u'ados_total', position=1, text=text, type=u'numerical', questionnaire=ados_questionnaire_eid, possible_answers=u'0-22').eid, 0, 22)
    text = u'Communication Total Subscore of the Classic ADOS'
    ados_questions['ados_comm'] = (store.create_entity('Question', identifier=u'ados_comm', position=2, text=text, type=u'numerical', questionnaire=ados_questionnaire_eid, possible_answers=u'0-8').eid, 0, 8)
    text = u'Social Total Subscore of the Classic ADOS'
    ados_questions['ados_social'] = (store.create_entity('Question', identifier=u'ados_social', position=3, text=text, type=u'numerical', questionnaire=ados_questionnaire_eid, possible_answers=u'0-14').eid, 0, 14)
    text = u'Stereotyped Behaviors and Restricted Interests Total Subscore of the Classic ADOS'
    ados_questions['ados_stereo_behav'] = (store.create_entity('Question', identifier=u'ados_stereo_behav', position=4, text=text, type=u'numerical', questionnaire=ados_questionnaire_eid, possible_answers=u'0-8').eid, 0, 8)
    text = u'Was ADOS scored and administered by research reliable personnel?'
    possible_answers = u'0 = not research reliable; 1 = research reliable'
    ados_questions['ados_rsrch_reliable'] = (store.create_entity('Question', identifier=u'ados_rsrch_reliable', position=5, text=text, type=u'boolean', questionnaire=ados_questionnaire_eid, possible_answers=possible_answers).eid, 0, 1)
    text = u'Social Affect Total Subscore for Gotham Algorithm of the ADOS'
    ados_questions['ados_gotham_soc_affect'] = (store.create_entity('Question', identifier=u'ados_gotham_soc_affect', position=6, text=text, type=u'numerical', questionnaire=ados_questionnaire_eid, possible_answers=u'0-20').eid, 0, 20)
    text = u'Restrictive and Repetitive Behaviors Total Subscore for Gotham Algorithm of the ADOS'
    ados_questions['ados_gotham_rrb'] = (store.create_entity('Question', identifier=u'ados_gotham_rrb', position=7, text=text, type=u'numerical', questionnaire=ados_questionnaire_eid, possible_answers=u'0-8').eid, 0, 8)
    text = u'Social Affect Total + Restricted and Repetitive Behaviors Total'
    ados_questions['ados_gotham_total'] = (store.create_entity('Question', identifier=u'ados_gotham_total', position=8, text=text, type=u'numerical', questionnaire=ados_questionnaire_eid, possible_answers=u'0-28').eid, 0, 28)
    text = u'Individually Calibrated Severity Score for Gotham Algorithm of the ADOS'
    ados_questions['ados_gotham_severity'] = (store.create_entity('Question', identifier=u'ados_gotham_severity', position=9, text=text, type=u'numerical', questionnaire=ados_questionnaire_eid, possible_answers=u'1-10').eid, 1, 10)

    # VINELAND
    vineland_questionnaire_eid = store.create_entity('Questionnaire', name=u'Vineland Adaptive Behavior Scales', identifier=u'vineland', language=u'fr', version=u'v 0.1.0', type=u'behavioral').eid
    vineland_questions = {}
    text = u'Vineland Adaptive Behavior Scales Receptive Language V Scaled Score'
    vineland_questions['vineland_receptive_v_scaled'] = (store.create_entity('Question', identifier=u'vineland_receptive_v_scaled', position=0, text=text, type=u'numerical', questionnaire=vineland_questionnaire_eid, possible_answers=u'1-24').eid, 1, 24)
    text = u'Vineland Adaptive Behavior Scales Expressive Language V Scaled Score'
    vineland_questions['vineland_expressive_v_scaled'] = (store.create_entity('Question', identifier=u'vineland_expressive_v_scaled', position=1, text=text, type=u'numerical', questionnaire=vineland_questionnaire_eid, possible_answers=u'1-24').eid, 1, 24)
    text = u'Vineland Adaptive Behavior Scales Written Language V Scaled Score'
    vineland_questions['vineland_written_v_scaled'] = (store.create_entity('Question', identifier=u'vineland_written_v_scaled', position=2, text=text, type=u'numerical', questionnaire=vineland_questionnaire_eid, possible_answers=u'1-24').eid, 1, 24)
    text = u'Vineland Adaptive Behavior Scales Communication Standard Score'
    vineland_questions['vineland_communication_standard'] = (store.create_entity('Question', identifier=u'vineland_communication_standard', position=3, text=text, type=u'numerical', questionnaire=vineland_questionnaire_eid, possible_answers=u'20-160').eid, 20, 160)
    text = u'Vineland Adaptive Behavior Scales Personal Daily Living Skills V Scaled Score'
    vineland_questions['vineland_personal_v_scaled'] = (store.create_entity('Question', identifier=u'vineland_personal_v_scaled', position=4, text=text, type=u'numerical', questionnaire=vineland_questionnaire_eid, possible_answers=u'1-24').eid, 1, 24)
    text = u'Vineland Adaptive Behavior Scales Domestic Daily Living Skills V Scaled Score'
    vineland_questions['vineland_domestic_v_scaled'] = (store.create_entity('Question', identifier=u'vineland_domestic_v_scaled', position=5, text=text, type=u'numerical', questionnaire=vineland_questionnaire_eid, possible_answers=u'1-24').eid, 1, 24)
    text = u'Vineland Adaptive Behavior Scales Community Daily Living Skills V Scaled Score'
    vineland_questions['vineland_community_v_scaled'] = (store.create_entity('Question', identifier=u'vineland_community_v_scaled', position=6, text=text, type=u'numerical', questionnaire=vineland_questionnaire_eid, possible_answers=u'1-24').eid, 1, 24)
    text = u'Vineland Adaptive Behavior Scales Daily Living Skills Standard Score'
    vineland_questions['vineland_dailylvng_standard'] = (store.create_entity('Question', identifier=u'vineland_dailylvng_standard', position=7, text=text, type=u'numerical', questionnaire=vineland_questionnaire_eid, possible_answers=u'20-160').eid, 20, 160)
    text = u'Vineland Adaptive Behavior Scales Interpersonal Relationships V Scaled Score'
    vineland_questions['vineland_interpersonal_v_scaled'] = (store.create_entity('Question', identifier=u'vineland_interpersonal_v_scaled', position=8, text=text, type=u'numerical', questionnaire=vineland_questionnaire_eid, possible_answers=u'1-24').eid, 1, 24)
    text = u'Vineland Adaptive Behavior Scales Play and Leisure Time V Scaled Score'
    vineland_questions['vineland_play_v_scaled'] = (store.create_entity('Question', identifier=u'vineland_play_v_scaled', position=9, text=text, type=u'numerical', questionnaire=vineland_questionnaire_eid, possible_answers=u'1-24').eid, 1, 24)
    text = u'Vineland Adaptive Behavior ScalesCoping Skills V Scaled Score'
    vineland_questions['vineland_coping_v_scaled'] = (store.create_entity('Question', identifier=u'vineland_coping_v_scaled', position=10, text=text, type=u'numerical', questionnaire=vineland_questionnaire_eid, possible_answers=u'1-24').eid, 1, 24)
    text = u'Vineland Adaptive Behavior Scales Socialization Standard Score'
    vineland_questions['vineland_social_standard'] = (store.create_entity('Question', identifier=u'vineland_social_standard', position=11, text=text, type=u'numerical', questionnaire=vineland_questionnaire_eid, possible_answers=u'20-160').eid, 20, 160)
    text = u'Sum of Vineland Standard Scores (Communication + Daily Living Skills + Socialization)'
    vineland_questions['vineland_sum_scores'] = (store.create_entity('Question', identifier=u'vineland_sum_scores', position=12, text=text, type=u'numerical', questionnaire=vineland_questionnaire_eid, possible_answers=u'76-480').eid, 76, 480)
    text = u'Vineland Adaptive Behavior Composite Standard score'
    vineland_questions['vineland_abc_standard'] = (store.create_entity('Question', identifier=u'vineland_abc_standard', position=13, text=text, type=u'numerical', questionnaire=vineland_questionnaire_eid, possible_answers=u'20-160').eid, 20, 160)
    text = u'Vineland Adaptive Behavior Scales Informant'
    vineland_questions['vineland_informant'] = (store.create_entity('Question', identifier=u'vineland_informant', position=14, text=text, type=u'numerical', questionnaire=vineland_questionnaire_eid, possible_answers=u'1 = parent; 2 = self').eid, 1, 2)

    store.flush()

    ###############################################################################
    ### SUBJECTS ##################################################################
    ###############################################################################
    groups = []
    for ind in range(NB_SUBJECTS_GROUPS):
        groups.append(store.create_entity('SubjectGroup', identifier=u'demo_group_%s' % ind,
                                          name=u'Demo group of subjects %s' % ind).eid)
    subjects = []
    for ind in range(NB_SUBJECTS):
        print ind
        date = random_date('age')
        subject = store.create_entity('Subject', identifier='demo_subject_%s' % ind,
                                      gender=SEX[nr.randint(len(SEX))],
                                      date_of_birth=date,
                                      handedness=HANDEDNESS[nr.randint(len(HANDEDNESS))]).eid
        subjects.append(subject)
        store.relate(subject, 'related_studies', study)
        store.relate(subject, 'related_groups', groups[nr.randint(len(groups))])
        # Scores
        for name, (score, _min, _max) in score_defs.iteritems():
            score_value = store.create_entity('ScoreValue', definition=score,
                                              datetime=random_date(), value=nr.randint(_min, _max)).eid
            store.relate(subject, 'related_infos', score_value)
        # Admissions
        admdate = random_date()
        if nr.randint(3):
            enddate = random_date(start=admdate)
        else:
            enddate = None
        admission = store.create_entity('Admission',
                                        admission_date=admdate,
                                        admission_end_date=enddate,
                                        admission_of=subject,
                                        admission_in=study)
        for i in range(nr.randint(5)):
            admdate = random_date(start=admdate)
            step = store.create_entity('AdmissionStep',
                                       step_date=admdate,
                                       name=u'Step %s' % i,
                                       step_of=admission.eid)
    store.flush()
    store.commit()


    ###############################################################################
    ### QUESTIONNAIRE RUNS ########################################################
    ###############################################################################
    protocol_eid = create_protocol(store, study, u'Demo questionnaire protocol')
    for subject_eid in subjects:
        print subject_eid, 'questionnaire'
        import_questionnaire(store, subject_eid, center, study,
                             ados_questionnaire_eid, ados_questions,
                             'ados', protocol_eid)
        import_questionnaire(store, subject_eid, center, study,
                             vineland_questionnaire_eid, vineland_questions,
                             'vineland', protocol_eid)
    store.flush()
    store.commit()


    ###############################################################################
    ### GENOMIC MEASURES ##########################################################
    ###############################################################################
    protocol_eid = create_protocol(store, study, u'Demo genomics protocol')
    for subject_eid in subjects:
        print subject_eid, 'genomics'
        measure = import_genomic(store, subject_eid, center, study, platform, u'SNP', protocol_eid)

    store.flush()
    store.commit()

    chromosome = store.rql('Any X ORDERBY RANDOM() LIMIT 1 WHERE X is Chromosome')
    if chromosome:
        for subject_eid in subjects:
            # Only few subject
            if nr.randint(10):
                print subject_eid, 'cgh'
                measure = import_cgh_results(store, subject_eid, center, study,
                                             platform, protocol_eid)
        store.flush()
        store.commit()

        for subject_eid in subjects:
            # Only few subject
            if nr.randint(10):
                print subject_eid, 'sequencing'
                measure = import_sequencing_results(store, subject_eid, center, study,
                                                    platform, protocol_eid)
        store.flush()
        store.commit()


    ###############################################################################
    ### IMAGES MEASURES ###########################################################
    ###############################################################################
    anat_eid = create_protocol(store, study, u'Demo anat protocol')
    fmri_eid = create_protocol(store, study, u'Demo fmri protocol')
    cmap_eid = create_protocol(store, study, u'Demo cmap protocol')
    for subject_eid in subjects:
        print subject_eid, 'images'
        import_anat_images(store, subject_eid, center, study, mri_1, mri_2, anat_eid)
        import_fmri_images(store, subject_eid, center, study, mri_1, mri_2, fmri_eid)
        import_constrat_images(store, subject_eid, center, study, mri_1, mri_2, cmap_eid)
    store.flush()
    store.commit()


    ###############################################################################
    ### DISEASE/THERAPY ###########################################################
    ###############################################################################
    diseases = [r[0] for r in store.rql('Any X ORDERBY RANDOM() LIMIT 10 '
                                        'WHERE X is Disease')]
    locations = [r[0] for r in store.rql('Any X ORDERBY RANDOM() LIMIT 20 '
                                         'WHERE X is BodyLocation')]
    techs = [r[0] for r in store.rql('Any X ORDERBY RANDOM() LIMIT 20 '
                                     'WHERE X is MedicalTechnique')]
    drugs = [r[0] for r in store.rql('Any X ORDERBY RANDOM() LIMIT 20 '
                                         'WHERE X is Drug')]
    if diseases:
        for subject_eid in subjects:
            disease = diseases[nr.randint(len(diseases))]
            location = locations[nr.randint(len(locations))]
            tech = techs[nr.randint(len(techs))]
            # Diagnostic
            diag_date = random_date()
            quote = DR_HOUSE_QUOTES_CONCLUSIONS[nr.randint(len(DR_HOUSE_QUOTES_CONCLUSIONS))]
            quote = u'``%s [...]`` [Dr House' % quote[:200]
            diag = store.create_entity('Diagnostic', diagnostic_date=diag_date,
                                       diagnostic_location=location,
                                       diagnosed_disease=disease,
                                       technique_type=tech,
                                       conclusion=quote).eid
            store.relate(subject_eid, 'related_diagnostics', diag)
            measure = store.rql('Any X WHERE X concerns S, S eid %(e)s', {'e': subject_eid})
            if measure:
                store.relate(diag, 'based_on', measure[0][0])
            # Therapy
            drug = drugs[nr.randint(len(drugs))]
            store.relate(subject_eid, 'related_diseases', disease)
            if nr.randint(3):
                store.relate(subject_eid, 'related_lesions', location)
            start_date = random_date(start=diag_date)
            stop_date = random_date(start=start_date)
            therapy = store.create_entity('Therapy',
                                          start_date=start_date,
                                          stop_date=stop_date if nr.randint(2)
                                          else None)
            store.relate(therapy.eid, 'therapy_for', disease)
            store.relate(therapy.eid, 'based_on_diagnostic', diag)
            store.relate(diag, 'leads_to_therapies', therapy.eid)
            store.relate(subject_eid, 'related_therapies', therapy.eid)
            stop_date = random_date(start=start_date)
            drugtake = store.create_entity('DrugTake',
                                           start_taking_date=start_date,
                                           stop_taking_date=stop_date if nr.randint(2)
                                           else None,
                                           taken_in_therapy=therapy.eid,
                                           drug=drug)
            # TechnicalAnalysis
            quote = DR_HOUSE_QUOTES[nr.randint(len(DR_HOUSE_QUOTES))]
            quote = u'``%s [...]`` [Dr House' % quote[:200]
            tech = store.create_entity('TechnicalAnalysis', analysis_date=random_date(diag_date),
                        conclusion=quote,
                        technique_type=techs[nr.randint(len(techs))]).eid
            store.relate(tech, 'performed_in_therapy', therapy.eid)
    store.flush()
    store.commit()

