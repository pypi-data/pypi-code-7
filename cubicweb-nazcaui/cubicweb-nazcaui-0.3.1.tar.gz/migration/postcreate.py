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

"""cubicweb-nazcaui postcreate script, executed at instance creation time or when
the cube is added to an existing instance.

You could setup site properties or a workflow here for example.
"""

def push_parameters(session, parameters, executable):
    for par, t in parameters:
        name = '%s - %s' % (executable.name, par)
        param = session.create_entity('ParameterDefinition',
                                      name=name,
                                      reverse_parameters=executable,
                                      value_type=t)


# Example of site property change
set_property('ui.site-title', "Nazca demo")



# Card
create_entity('Card', content_format=u'text/html', title=u'index',
              content=u"""<div class='row-fluid'>
              <div class='span12'>
              <h1>Welcome on Nazca !</h1><blockquote>
              <p><h3>What is it for ?</h3>
Nazca is a python library aiming to help you to align data. But, what does “align data” mean? For instance, you have a list of cities, described by their name and their country and you would like to find their URI on dbpedia to have more information about them, as the longitude and the latitude. If you have two or three cities, it can be done with bare hands, but it could not if there are hundreds or thousands cities. Nazca provides you all the stuff we need to do it.
</p>
<p><h3>See more</h3>
<ul>
<li><a href='https://www.logilab.org/112574'>Nazca Project</a></li>
<li><a href='http://www.logilab.org/blogentry/115136'>Blog post on Nazca</a></li>
<li><a href='http://www.cubicweb.org'>CubicWeb</a></li>
</ul></p>
</blockquote></div></div>""")




NAZCA_DISTANCES = ((u'ExactMatchProcessing', ()),
                   (u'LevenshteinProcessing', ()),
                   (u'GeographicalProcessing', ((u'units', u'String'),)),
                   (u'SoundexProcessing', ((u'language', u'String'),)),
                   (u'JaccardProcessing', ()),
                   (u'DifflibProcessing', ()),
                   (u'TemporalProcessing', ((u'granularity', u'String'),)),
                   )

for name, parameters in NAZCA_DISTANCES:
    executable = session.create_entity('Distance', name=name)
    push_parameters(session, parameters, executable)


NAZCA_BLOCKINGS = ((u'KeyBlocking', ((u'callback', u'String'),)),
                   (u'NGramBlocking', ((u'ngram_size', u'Int'),
                                      (u'depth', u'Int')),),
                   (u'SortedNeighborhoodBlocking', ((u'key_func', u'String'),
                                                   (u'window_with', u'Int')),),
                   (u'KmeansBlocking', ((u'n_clusters', u'Int'),)),
                   (u'KdTreeBlocking', ((u'threshold', u'Int'),)),
                   (u'MinHashingBlocking', ((u'threshold', u'Int'),
                                           (u'kwordsgram', u'Int'),
                                           (u'siglen', u'Int')),))

for name, parameters in NAZCA_BLOCKINGS:
    executable = session.create_entity('Blocking', name=name)
    push_parameters(session, parameters, executable)


NAZCA_NORMALIZERS = ((u'UnicodeNormalizer', ((u'substitute', u'String'),)),
                     (u'SimplifyNormalizer', ((u'remove_stopwords', u'Boolean'),)),
                     (u'TokenizerNormalizer', ((u'regexp', u'Regexp'),)),
                     (u'LemmatizerNormalizer', ()),
                     (u'RoundNormalizer', ((u'ndigits', u'Int'),)),
                     (u'RegexpNormalizer', ((u'regexp', u'Regexp'),
                                            (u'output', u'String'))),
                     )

for name, parameters in NAZCA_NORMALIZERS:
    executable = session.create_entity('Normalization', name=name)
    push_parameters(session, parameters, executable)
