

refset = session.create_entity('QueryDataSet',
                               title=u'Dbpedia cities 100',
                               autocast=True,
                               datatype=u'sparql',
                               source=u'http://demo.cubicweb.org/sparql',
                               query=u'''PREFIX dbonto:<http://dbpedia.org/ontology/>
                               SELECT ?p ?n ?c WHERE {?p a dbonto:PopulatedPlace.
                               ?p dbonto:country dbpedia:France.
                               ?p foaf:name ?n.
                               ?p dbpprop:insee ?c}LIMIT 100 ''')


target_set = session.create_entity('QueryDataSet',
                                   title=u'INSEE cities 100',
                                   autocast=True,
                                                    datatype=u'sparql',
                                   source=u'http://rdf.insee.fr/sparql',
                                   query=u'''PREFIX igeo:<http://rdf.insee.fr/def/geo#>
                                   SELECT ?commune ?nom ?code WHERE {?commune igeo:codeCommune ?code.
                                   ?commune igeo:nom ?nom} LIMIT 100 ''')

norm = session.find_one_entity('Normalization', name=u'SimplifyNormalizer')
ref_normalizer = session.create_entity('NormalizationRun', function=norm.eid, index=1)
target_normalizer = session.create_entity('NormalizationRun', function=norm.eid, index=1)

distance = session.find_one_entity('Distance', name=u'DifflibProcessing')
processing = session.create_entity('DistanceRun',
                                   function=distance.eid,
                                   refset_index=1,
                                   targetset_index=1)

alignment = session.create_entity('Alignment',
                                  name=u'test',
                                  reference_set=refset,
                                  target_set=target_set)
alignment.cw_set(processings=processing)
alignment.cw_set(ref_normalizers=ref_normalizer)
alignment.cw_set(target_normalizers=target_normalizer)
