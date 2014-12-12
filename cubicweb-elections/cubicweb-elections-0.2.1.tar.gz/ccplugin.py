# -*- coding: utf-8 -*-
import urllib
import json
from xlrd import open_workbook

from logilab.common.textutils import unormalize

from cubicweb import AuthenticationError
from cubicweb import cwconfig
from cubicweb.server.utils import manager_userpasswd
from cubicweb.dbapi import in_memory_repo_cnx
from cubicweb.toolsutils import Command
from cubicweb.cwctl import CWCTL

from cubes.dataio.dataimport import MassiveObjectStore


class ElectionsImportCommand(Command):
    """
    Command for importing legislatives data.

    This command is used for pushing elections data.
    It is used as following:

    cubicweb-ctl elections-import <instance>
    """
    arguments = '<instance>'
    name = 'elections-import'
    DATA = {
        u'présidentiel': ((2012, 'http://static.data.gouv.fr/15/56da0680db5a23d2d1601aed81359f21e0dc8ed9f8abd49e2a7c66b5c02b6f.xls'),
                          (2007, 'http://static.data.gouv.fr/88/523001571e33cd204af5959a5387961121f2a1f765d2ea9197190fcdf02778.xls'),
                          ((2002, 1), 'http://static.data.gouv.fr/a4/27cbe1705dd8003e1783251be7b4da3a6a83763a2078a46b282742bf4685d9.xls'),
                          ((2002, 2), 'http://static.data.gouv.fr/1e/01293a8816a82e7a9ed972f638f9793eb3f1cd8a7bffbf76667013482770a4.xls')),
        u'législatif': ((2012, 'http://static.data.gouv.fr/e9/d21be5a4feca8a36a3bf17399ce7ebaeaf7588df0128fa4ad9f630c4b0ebf3.xls'),
                        ((2007, 1), 'http://static.data.gouv.fr/02/f2582a43be34cc1975fa364568d6e39d75c647fb50dcc4b4bd19d3321d16e0.xls'),
                        ((2007, 2), 'http://static.data.gouv.fr/8b/ef74da610af0f2850d5e2917a6ff88d4c6635d5bf6409f8d8b20cea1080fb9.xls'),
                        ((2002, 1), 'http://static.data.gouv.fr/61/621e84bb83c77c3ffe5e449f53eb0c9ca9c5b92a57e9369877fefcba75a491.xls'),
                        ((2002, 2), 'http://static.data.gouv.fr/d2/b378f7f05bbff9ea69e9aa5d5015d520b902d4467a77a38a3a075576d45e7f.xls'),),
        u'municipal': ((2008, ('http://static.data.gouv.fr/18/22c3d2b3c8e3abb0fb447515ce23ad4858ad8b3522749d9924acc218f7b7a9.xls',
                               'http://static.data.gouv.fr/0c/3db24502775bd8c6c3a4d1670b5a43353d848efe0857af1b07ee7d069b54e8.xls',
                               'http://static.data.gouv.fr/0b/6af04d2d1b52a4735fc0b0171d5d94e7dfe0deeacab0e8075e33fa4a75245d.xls'),),
                       # Does not work for now (different shape of files...)
                       ## ((2014, 1), ('https://www.data.gouv.fr/storage/f/2014-03-25T16-22-14/muni-2014-resultats-com-moins-1000-t1.txt',
                       ##             'https://www.data.gouv.fr/storage/f/2014-03-25T16-11-54/muni-2014-elus-com-1000-et-plus-t1.txt',)),
                       ## ((2014, 2), ('https://www.data.gouv.fr/storage/f/2014-03-31T09-49-28/muni-2014-resultats-com-1000-et-plus-t2.txt',
                       ##              'https://www.data.gouv.fr/storage/f/2014-03-31T09-51-08/muni-2014-resultats-com-moins-1000-t2.txt',)),
                       )

            }

    def _init_cw_connection(self, appid):
        config = cwconfig.instance_configuration(appid)
        sourcescfg = config.sources()
        config.set_sources_mode(('system',))
        cnx = repo = None
        while cnx is None:
            try:
                login = sourcescfg['admin']['login']
                pwd = sourcescfg['admin']['password']
            except KeyError:
                login, pwd = manager_userpasswd()
            try:
                repo, cnx = in_memory_repo_cnx(config, login=login, password=pwd)
            except AuthenticationError:
                print 'wrong user/password'
            else:
                break
        return cnx, repo._get_session(cnx.sessionid)

    def run(self, args):
        appid = args.pop(0)
        cw_cnx, session = self._init_cw_connection(appid)
        session.set_pool()
        # Initiate the store
        store = MassiveObjectStore(session, autoflush_metadata=False, commit_at_flush=False)
        scrutins = store.rql('Any X WHERE X is Scrutin, X type T, X annee A').entities()
        store.scrutins = dict([((e.type, e.annee), e) for e in scrutins])
        tours = store.rql('Any X WHERE X is Tour, X scrutin S, X valeur A, '
                          'S type T, S annee A').entities()
        store.tours = dict([((e.scrutin[0].type, e.scrutin[0].annee, e.valeur), e)
                            for e in scrutins])
        rset_candidats = store.rql('Any X, N, P WHERE X nom N, X prenom P')
        store.candidats = dict([(self.get_candidat_key(row[1], row[2]), row[0])
                                for row in rset_candidats])
        departements =  store.rql('Any X WHERE X is Departement').entities()
        store.departements = dict([(e.insee, e) for e in departements])
        communes = store.rql('Any X, C WHERE X is Commune, X insee C').entities()
        store.communes = dict([(e.insee, e) for e in communes])
        secteurs = store.rql('Any X, C WHERE X is Secteur, X code C').entities()
        store.secteurs = dict([(e.code, e) for e in secteurs])
        store.etiquettes = dict(store.rql('Any N, X WHERE X is Etiquette, X nom N'))
        listes = store.rql('Any X, N, C WHERE X is Liste, X nom N, X commune C').entities()
        store.listes = dict([((e.nom, e.commune[0].eid), e) for e in listes])
        circonscriptions = store.rql('Any X, C, CU, S WHERE X is Circonscription, X code C, '
                                     'X commune CU, X scrutin S')
        store.circonscriptions = dict([((row[1], row[2], row[3]), row[0])
                                       for row in circonscriptions])
        # Push data
        for scrutin_type, data_infos in self.DATA.iteritems():
            for infos, urls in data_infos:
                if not isinstance(urls, tuple):
                    urls = (urls,)
                for url in urls:
                    print 'Fetching data from', url
                    filename, headers = urllib.urlretrieve(url)
                    book = open_workbook(filename)
                    if isinstance(infos, tuple):
                        annee, tour = infos
                    else:
                        annee, tour = infos, None
                    for ind_sheet, sheet in enumerate(book.sheets()):
                        if 'tour 1' in sheet.name.lower():
                            tour = 1
                        elif 'tour 2' in sheet.name.lower():
                            tour = 2
                        print sheet.name, tour, annee, url
                        data = [sheet.row_values(i) for i in range(1, sheet.nrows)]
                        self.import_data(store, data, scrutin_type, annee, tour)
                        store.flush()
        # Final flush and commit
        store.flush_meta_data()
        store.cleanup()

    def get_scrutin_and_tour(self, store, type, annee, tour):
        """ Get or screate a scrutin """
        key = (type, annee)
        # Scrutin
        if key in store.scrutins:
            scrutin = store.scrutins[key]
        else:
            scrutin = store.create_entity('Scrutin', type=type, annee=annee)
            store.scrutins[key] = scrutin
        # Tour
        key = (type, annee, tour)
        if key in store.tours:
            tour = store.tours[key]
        else:
            tour = store.create_entity('Tour', valeur=tour, scrutin=scrutin.eid)
            store.tours[key] = tour
        return scrutin, tour


    def get_departement(self, store, code):
        """ Get a departement from code """
        # Remove trailing .0
        code = code.split('.')[0]
        code = code if len(code) != 1 else '0'+code
        if code in ('ZA', 'ZB', 'ZC', 'ZD', 'ZM', 'ZN', 'ZP', 'ZS', 'ZW', 'ZX', 'ZZ'):
            # Do not consider these departements for now (not in insee)
            return
        return store.departements[code]

    def get_commune(self, store, code_postal, departement, nom):
        """ Get a commune from postal code """
        try:
            code_postal = departement.insee + '%03d' % int(code_postal)
            if code_postal in store.communes:
                return store.communes[code_postal]
            else:
                print 'Unknown commune', code_postal, ' ????'
                return
        except ValueError:
            # This may be a secteur
            try:
                if code_postal in store.secteurs:
                    return store.secteurs[code_postal]
                for part in ('SN', 'AR', 'SR'):
                    if part in code_postal:
                        _code_postal = departement.insee + '%03d' % int(code_postal.split(part)[0].lstrip('0'))
                        if _code_postal not in store.communes:
                            print 'Unknown commune for secteur', code_postal, _code_postal, ' ????'
                            return
                        commune = store.communes[_code_postal]
                        secteur = store.create_entity('Secteur', code=code_postal,
                                                      nom=nom, commune=commune.eid)
                        store.secteurs[code_postal] = secteur
                        print 'Create secteur', code_postal
                        return secteur
                print 'Unknown secteur', code_postal, ' ????'
                return
            except ValueError:
                return

    def get_circonscription(self, store, code, scrutin, departement, commune):
        """ Get a circonscription from code """
        key = (code, commune.eid, scrutin.eid)
        if key in store.circonscriptions:
            return store.circonscriptions[key]
        else:
            circonscription = store.create_entity('Circonscription', code=code,
                                                  departement=departement.eid,
                                                  commune=commune.eid,
                                                  scrutin=scrutin.eid).eid
            store.circonscriptions[key] = circonscription
            return circonscription

    def get_candidat_key(self, nom, prenom):
        """ Get a candidat key """
        return '%s%s' % (unormalize(nom.lower().replace('-', ''), '_'),
                         unormalize(prenom.lower().replace('-', ''), '_'))

    def get_candidat(self, store, candidat):
        """ Get a candidat from infos """
        key = self.get_candidat_key(candidat['nom'], candidat['prenom'])
        if key in store.candidats:
            return store.candidats[key]
        else:
            candidat = store.create_entity('Candidat', **candidat).eid
            store.candidats[key] = candidat
            return candidat

    def get_etiquette(self, store, etiquette):
        """ Get an etiquette """
        if etiquette in store.etiquettes:
            return store.etiquettes[etiquette]
        else:
            etiquette_eid = store.create_entity('Etiquette', nom=etiquette).eid
            store.etiquettes[etiquette] = etiquette_eid
            return etiquette_eid

    def get_liste(self, store, liste, commune_eid):
        """ Get an liste """
        key = (liste, commune_eid)
        if key in store.listes:
            return store.listes[key]
        else:
            if isinstance(liste, basestring):
                liste_eid = store.create_entity('Liste', nom=liste, commune=commune_eid).eid
                store.listes[key] = liste_eid
                return liste_eid

    def build_candidat(self, store, scrutin, candidat_info, inscrits):
        """ Build a candidat """
        # Candidat
        try:
            if scrutin.type in (u'présidentiel', u'législatif'):
                c_info = candidat_info[:3]
            else:
                # Municipal
                if len(candidat_info) == 9:
                    c_info = candidat_info[1:4]
                else:
                    c_info = candidat_info[2:]
            candidat = {'sexe': c_info[0],
                        'nom': c_info[1].capitalize(),
                        'prenom': c_info[2].capitalize()}
            # Candidat and Resultat
            if scrutin.type in (u'présidentiel', u'législatif'):
                resultat = {'voix': int(candidat_info[-3]),
                            'fraction_voix_inscrits': candidat_info[-2],
                            'fraction_voix_exprimes': candidat_info[-1]}
            elif scrutin.type == 'municipal' and len(candidat_info) == 9:
                resultat = {'voix': int(candidat_info[-3]),
                            'sieges': int(candidat_info[-4]),
                            'fraction_voix_inscrits': candidat_info[-2],
                            'fraction_voix_exprimes': candidat_info[-1]}
            else:
                # Municipal
                frac_voix_inscrits = 100.*candidat_info[0]/inscrits
                resultat = {'voix':int( candidat_info[0]),
                            'fraction_voix_inscrits': frac_voix_inscrits,
                            'fraction_voix_exprimes': candidat_info[1]}
            # Etiquette
            if scrutin.type == u'législatif':
                etiquette = candidat_info[3]
            elif scrutin.type == 'municipal' and len(candidat_info) == 9:
                # Remove first "L" (liste)
                etiquette = candidat_info[0][1:]
            else:
                etiquette = None
            # Liste
            if scrutin.type == 'municipal' and len(candidat_info) == 9:
                liste = candidat_info[4]
            else:
                liste = None
            return candidat, resultat, etiquette, liste
        except:
            print 'ERROR in', candidat_info
            return

    def build_all_candidats(self, store, scrutin, candidats_infos, candidat_size, inscrits=None):
        """ Build all candidats infos """
        candidats = []
        for ind in range(int(len(candidats_infos)/candidat_size)):
            candidat_info = candidats_infos[ind*candidat_size:(ind+1)*candidat_size]
            if not sum(bool(i) for i in candidat_info):
                continue
            info = self.build_candidat(store, scrutin, candidat_info, inscrits)
            if info:
                candidats.append(info)
            else:
                continue
        return candidats

    def build_statistique(self, store, stat_infos, tour_eid, commune_eid):
        """ Build a stat infos """
        if len(stat_infos) == 11:
            fraction_nuls_inscrits = stat_infos[6]
            fraction_exprimes_votants = stat_infos[10]
        else:
            # Municipal
            fraction_nuls_inscrits = 100*float(stat_infos[5])/stat_infos[0]
            fraction_exprimes_votants = 100*float(stat_infos[7])/stat_infos[0]
        return store.create_entity('Statistique',
                                   commune=commune_eid,
                                   tour=tour_eid,
                                   inscrits=int(stat_infos[0]),
                                   abstentions=int(stat_infos[1]),
                                   fraction_abstentions_inscrits=stat_infos[2],
                                   votants=int(stat_infos[3]),
                                   fraction_votants_inscrits=stat_infos[4],
                                   blancs_nuls=int(stat_infos[5]),
                                   fraction_nuls_inscrits=fraction_nuls_inscrits,
                                   fraction_nuls_votants=stat_infos[6],
                                   exprimes=int(stat_infos[7]),
                                   fraction_exprimes_inscrits=stat_infos[8],
                                   fraction_exprimes_votants=fraction_exprimes_votants)

    def import_data(self, store, data, scrutin_type, annee, tour):
        """ Import presidentielle election data
        """
        print '----->', repr(scrutin_type), annee, tour
        if tour is not None:
            scrutin, tour_entity = self.get_scrutin_and_tour(store, scrutin_type,
                                                             annee, tour)
        seen_communes = set()
        seen_candidatures = {}
        for ind, infos in enumerate(data):
            # Get scrutin
            if tour is None:
                # Row dependant scrutin - Municipales
                scrutin, tour_entity = self.get_scrutin_and_tour(store, scrutin_type,
                                                                 annee, int(infos[4]))
            # Departement
            departement = self.get_departement(store, str(infos[0]))
            if not departement:
                continue
            # Commune
            if scrutin.type == u'présidentiel':
                code_postal, nom = infos[2], infos[3]
            elif scrutin.type == u'municipal' and tour is not None:
                code_postal, nom = infos[2], infos[3]
            else:
                code_postal, nom = infos[4], infos[5]
            commune = self.get_commune(store, code_postal, departement, nom)
            if not commune:
                continue
            # Circonscription
            if scrutin.type == u'législatif':
                circonscription_eid = self.get_circonscription(store, int(infos[2]),
                                                               scrutin, departement, commune)
            else:
                circonscription_eid = None
            # Statistiques
            if scrutin.type == u'présidentiel':
                stats_infos = infos[4:15]
            elif scrutin.type == u'législatif':
                stats_infos = infos[6:17]
            elif scrutin.type == u'municipal':
                if tour is None:
                    stats_infos = infos[5:14]
                else:
                    # Cities bigger than 3500 habitants
                    stats_infos = infos[4:15]
            if not (scrutin.type == u'municipale' and commune.eid in seen_communes):
                statistique = self.build_statistique(store, stats_infos,
                                                     tour_entity.eid, commune.eid)
                seen_communes.add(commune.eid)
            # Candidat
            if scrutin.type == u'présidentiel':
                candidats = self.build_all_candidats(store, scrutin, infos[15:], 6, None)
            elif scrutin.type == u'législatif':
                candidats = self.build_all_candidats(store, scrutin, infos[17:], 7, None)
            elif scrutin.type == u'municipal' and tour is None:
                candidat = self.build_candidat(store, scrutin, infos[14:], statistique.inscrits)
                candidats = [candidat,] if candidat else []
            elif scrutin.type == u'municipal' and tour is not None:
                candidats = self.build_all_candidats(store, scrutin, infos[15:], 9, None)
            for candidat, resultat, etiquette, liste in candidats:
                # Candidat
                candidat_eid = self.get_candidat(store, candidat)
                # Etiquette
                etiquette_eid = self.get_etiquette(store, etiquette) if etiquette else None
                # Liste
                liste_eid = self.get_liste(store, liste, commune.eid) if liste else None
                # Candidature
                candidature_key = (etiquette_eid, liste_eid, candidat_eid, scrutin.eid)
                if candidature_key in seen_candidatures:
                    candidature_eid = seen_candidatures[candidature_key]
                else:
                    candidature_eid = store.create_entity('Candidature',
                                                          etiquette=etiquette_eid,
                                                          liste=liste_eid,
                                                          candidat=candidat_eid,
                                                          scrutin=scrutin.eid).eid
                    seen_candidatures[candidature_key] = candidature_eid
                # Resultat
                resultat['tour'] = tour_entity.eid
                resultat['commune'] = commune.eid
                resultat['departement'] = departement.eid
                resultat['candidature'] = candidature_eid
                resultat['circonscription'] = circonscription_eid
                resultat = store.create_entity('Resultat', **resultat).eid
            if ind % 10000 == 0:
                store.flush()
        # Final flush
        store.flush()


CWCTL.register(ElectionsImportCommand)
