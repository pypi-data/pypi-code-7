from simuPOP.demography import *
from simuPOP import *
import math

class SettlementOfNewWorldModel_event(EventBasedModel):
    '''A dempgraphic model for settlement of the new world of Americans, as defined
    in Gutenkunst 2009, Plos Genetics. The model is depicted in Figure 3, and the 
    default parameters are listed in Table 2 of this paper. '''
    def __init__(self,
        T0,
        N_A=7300,
        N_AF=12300,
        N_B=2100,
        N_EU0=1500,
        r_EU=0.0023,
        N_AS0=590,
        r_AS=0.0037,
        N_MX0=800,
        r_MX=0.005,
        m_AF_B=0.00025,
        m_AF_EU=0.00003,
        m_AF_AS=0.000019,
        m_EU_AS=0.0000135,
        T_AF=220000//25, 
        T_B=140000//25, 
        T_EU_AS=26400//25, 
        T_MX=21600//25,
        f_MX=0.48,
        ops=[],
        infoFields=[],
        outcome='MXL',
        scale=1
        ):
        '''Counting **backward in time**, this model evolves a population for ``T0``
        generations. The ancient population ``A`` started at size ``N_A`` and
        expanded at ``T_AF`` generations from now, to pop ``AF`` with size ``N_AF``.
        Pop ``B`` split from pop ``AF`` at ``T_B`` generations from now, with
        size ``N_B``; Pop ``AF`` remains as ``N_AF`` individuals. Pop ``EU`` and 
        ``AS`` split from pop ``B`` at ``T_EU_AS`` generations from now; with 
        size ``N_EU0`` individuals and ``N_ASO`` individuals, respectively. Pop
        ``EU`` grew exponentially with final population size ``N_EU``; Pop
        ``AS`` grew exponentially with final populaiton size ``N_AS``. Pop ``MX``
        split from pop ``AS`` at ``T_MX`` generations from now with size ``N_MX0``,
        grew exponentially to final size ``N_MX``. Migrations are allowed between
        populations with migration rates ``m_AF_B``, ``m_EU_AS``, ``m_AF_EU``,
        and ``m_AF_AS``. At the end of the evolution, the ``AF`` and ``CHB``
        populations are removed, and the ``EU`` and ``MX`` populations are merged
        with ``f_MX`` proportion for ``MX``. The Mexican American<F19> sample could
        be sampled from the last single population. Additional operators could
        be added to ``ops``. Information fields required by these operators 
        should be passed to ``infoFields``. If a scaling factor ``scale``
        is specified, all population sizes and generation numbers will be divided by
        a factor of ``scale``. This demographic model by default only returns the
        mixed Mexican America model (``outputcom='MXL'``) but you can specify any
        combination of ``AF``, ``EU``, ``AS``, ``MX`` and ``MXL``.

        This model merges all subpopulations if it is applied to an initial population
        with multiple subpopulation.
        '''
        if T0 < T_AF:
            raise ValueError('Length of evolution T0=%d should be more than T_AF=%d' % (T0, T_AF))
        #
        scale = float(scale)
        EventBasedModel.__init__(self,
            T = int(T0/scale),
            N0 = (int(N_A/scale), 'Ancestral'),
            infoFields = 'migrate_to',
            events = [
                # resize ancestral to AF
                ResizeEvent(at= -int(T_AF/scale), subPops='Ancestral',
                    sizes=int(N_AF/scale), names='AF'),
                # split B from AF
                SplitEvent(at=-int(T_B/scale), subPops='AF',
                    sizes=(1.0, int(N_B/scale)), names=('AF', 'B')),
                # migration between AF and B
                DemographicEvent(
                    ops=Migrator(rate=[
                        [m_AF_B, 0],
                        [0, m_AF_B]]), 
                    begin=-int(T_B/scale), 
                    end=-int(T_EU_AS/scale)
                ),
                # split EU AS from B
                SplitEvent(at=-int(T_EU_AS/scale), subPops='B',
                    sizes=(int(N_EU0/scale), int(N_AS0/scale)),
                    names=('EU', 'AS')),
                # exponential growth 
                ExpansionEvent(begin=-int(T_EU_AS/scale),
                    subPops=('EU', 'AS'), 
                    rates=(r_EU*scale, r_AS*scale)),
                # split MX from AS
                SplitEvent(at=-int(T_MX/scale),
                    subPops='AS',
                    sizes=(1.0, int(N_MX0/scale)),
                    names=('AS', 'MX')),
                # expansion of MX
                ExpansionEvent(begin=-int(T_MX/scale),
                    subPops='MX',
                    rates=r_MX),
                # migration between AF, EU and AS
                DemographicEvent(
                    ops=Migrator(rate=[
                        [0, m_AF_EU, m_AF_AS],
                        [m_AF_EU, 0, m_EU_AS],
                        [m_AF_AS, m_EU_AS, 0]
                        ],
                    subPops=['AF', 'EU', 'AS']), 
                    begin=-int(T_EU_AS/scale),
                ),
                # admixture
                AdmixtureEvent(
                    at=-1,
                    subPops=['EU', 'MX'],
                    sizes=(1-f_MX, f_MX),
                    name='MXL'),
                # keep only selected populations
                ResizeEvent(at=-1, 
                    sizes=[float('AF' in outcome),
                        float('EU' in outcome),
                        float('AS' in outcome),
                        float('MX' in outcome),
                        float('MXL' in outcome)],
                    removeEmptySubPops=True)
            ]
        )

class SettlementOfNewWorldModel_outcome(MultiStageModel):
    '''A dempgraphic model for settlement of the new world of Americans, as defined
    in Gutenkunst 2009, Plos Genetics. The model is depicted in Figure 3, and the 
    default parameters are listed in Table 2 of this paper. '''
    def __init__(self,
        T0,
        N_A=7300,
        N_AF=12300,
        N_B=2100,
        N_EU0=1500,
        r_EU=0.0023,
        N_AS0=590,
        r_AS=0.0037,
        N_MX0=800,
        r_MX=0.005,
        m_AF_B=0.00025,
        m_AF_EU=0.00003,
        m_AF_AS=0.000019,
        m_EU_AS=0.0000135,
        T_AF=220000//25, 
        T_B=140000//25, 
        T_EU_AS=26400//25, 
        T_MX=21600//25,
        f_MX=0.48,
        ops=[],
        infoFields=[],
        outcome='MXL',
        scale=1
        ):
        '''Counting **backward in time**, this model evolves a population for ``T0``
        generations. The ancient population ``A`` started at size ``N_A`` and
        expanded at ``T_AF`` generations from now, to pop ``AF`` with size ``N_AF``.
        Pop ``B`` split from pop ``AF`` at ``T_B`` generations from now, with
        size ``N_B``; Pop ``AF`` remains as ``N_AF`` individuals. Pop ``EU`` and 
        ``AS`` split from pop ``B`` at ``T_EU_AS`` generations from now; with 
        size ``N_EU0`` individuals and ``N_ASO`` individuals, respectively. Pop
        ``EU`` grew exponentially with final population size ``N_EU``; Pop
        ``AS`` grew exponentially with final populaiton size ``N_AS``. Pop ``MX``
        split from pop ``AS`` at ``T_MX`` generations from now with size ``N_MX0``,
        grew exponentially to final size ``N_MX``. Migrations are allowed between
        populations with migration rates ``m_AF_B``, ``m_EU_AS``, ``m_AF_EU``,
        and ``m_AF_AS``. At the end of the evolution, the ``AF`` and ``CHB``
        populations are removed, and the ``EU`` and ``MX`` populations are merged
        with ``f_MX`` proportion for ``MX``. The Mexican American<F19> sample could
        be sampled from the last single population. Additional operators could
        be added to ``ops``. Information fields required by these operators 
        should be passed to ``infoFields``. If a scaling factor ``scale``
        is specified, all population sizes and generation numbers will be divided by
        a factor of ``scale``. This demographic model by default only returns the
        mixed Mexican America model (``outputcom='MXL'``) but you can specify any
        combination of ``AF``, ``EU``, ``AS``, ``MX`` and ``MXL``.

        This model merges all subpopulations if it is applied to an initial population
        with multiple subpopulation.
        '''
        if T0 < T_AF:
            raise ValueError('Length of evolution T0=%d should be more than T_AF=%d' % (T0, T_AF))
        #

        ##
        ##
        # try to figure out how to mix two populations
        N_EU=int(N_EU0*math.exp(r_EU*T_EU_AS))
        N_MX=int(N_MX0*math.exp(r_MX*T_MX))
        #
        #
        # for python 2.x and 3.x compatibility
        if isinstance(outcome, str):
            outcome = [outcome]
        if 'MXL' in outcome:
            # with admixture
            final_subpops = [None, None, None, None, None]
            for (idx, name) in enumerate(['AF', 'EU', 'AS', 'MX', 'MXL']):
                if name not in outcome:
                    final_subpops[idx] = 0
            #
            admixtureStage = [
                AdmixtureModel(T=1,
                    N0=[None, None, None, None],
                    # mixing European and Mexican population
                    model=['HI', 1, 3, 1-f_MX, 'MXL']),
                InstantChangeModel(T=1,
                    N0=final_subpops,
                    removeEmptySubPops=True)
                ]
        else:
            final_subpops = [None, None, None, None]
            for (idx, name) in enumerate(['AF', 'EU', 'AS', 'MX']):
                if name not in outcome:
                    final_subpops[idx] = 0
            admixtureStage = [
                InstantChangeModel(T=1,
                    N0=final_subpops,
                    removeEmptySubPops=True)
                ]
        #
        scale = float(scale)
        MultiStageModel.__init__(self, [
            InstantChangeModel(
                T=int((T0-T_B)/scale),
                N0=(int(N_A/scale), 'Ancestral'),
                # change population size twice, one at T_AF, one at T_B
                G=[int((T0-T_AF)/scale)],
                NG=[(int(N_AF/scale), 'AF')] 
            ),
            #
            # at T_B, split to population B from subpopulation 1
            InstantChangeModel(
                T=int((T_B - T_EU_AS)/scale),
                # change population size twice, one at T_AF, one at T_B
                N0=[None, (int(N_B/scale), 'B')],
                ops=Migrator(rate=[
                    [m_AF_B, 0],
                    [0, m_AF_B]])
                ),
            ExponentialGrowthModel(
                T=int((T_EU_AS - T_MX)/scale),
                N0=[None,
                    # split B into EU and AS at the beginning of this
                    # exponential growth stage
                    [(int(N_EU0/scale), 'EU'), (int(N_AS0/scale), 'AS')]],
                r=[0, r_EU*scale, r_AS*scale],
                infoFields='migrate_to',
                ops=Migrator(rate=[
                    [0, m_AF_EU, m_AF_AS],
                    [m_AF_EU, 0, m_EU_AS],
                    [m_AF_AS, m_EU_AS, 0]
                    ])
                ),
            ExponentialGrowthModel(T=int(T_MX/scale),
                N0=[None,
                    # initial population size has to be calculated
                    # because we only know the final population size of
                    # EU and AS
                    None,
                    # split MX from AS
                    [(None, 'AS'), (int(N_MX0//scale), 'MX')]],
                r=[0, r_EU*scale, r_AS*scale, r_MX*scale],
                infoFields='migrate_to',
                ops=Migrator(rate=[
                    [0, m_AF_EU, m_AF_AS],
                    [m_AF_EU, 0, m_EU_AS],
                    [m_AF_AS, m_EU_AS, 0]
                    ],
                    # the last MX population does not involve in 
                    # migration
                    subPops=[0, 1, 2],
                    toSubPops=[0, 1, 2])
                )
            ] + admixtureStage,
            ops=ops, infoFields=infoFields
        )


SettlementOfNewWorldModel_outcome(10000).plot()
#SettlementOfNewWorldModel_event(10000, scale=1).plot()
