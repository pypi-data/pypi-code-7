"""
Sphinx/docutils extension to create links to the SeqAn dox documentation using
a RestructuredText interpreted text role that looks like this:

    :dox:`seqan_link_text`

for example:

    :dox:`StringSet`

creates a link to the documentation entry of the Index class.

adapted from the traclinks extension.
"""

from __future__ import print_function

import json
import os.path
import sys
import urllib

from docutils import nodes, utils


# Keys expected in JSON.
KEYS = ('title', 'name', 'text', 'akas', 'subentries', 'loc', 'langEntity')

def makeSeqAnLink(name, rawtext, text, lineno, inliner,
                  options={}, content=[]):
    env = inliner.document.settings.env
    known_dox_names = env.known_dox_names
    dox_url = env.config.doxlinks_base_url

    # Parse the text in role argument.
    tokens = text.split()
    target = tokens[0]
    if known_dox_names and target not in known_dox_names:
        msg = inliner.reporter.error(
          'Referencing unknown dox item %s.' % target,
          lineno=lineno)
        prb = inliner.problematic(rawtext, rawtext, msg)
        return [prb], [msg]
    text = tokens[0]
    if len(tokens) == 1 and env.config.shorten_nested_names:
        if '::' in text:
            text = text.split('::')[-1]
        elif '#' in text:
            text = text.split('#')[-1]
    else:
        text = ' '.join(tokens[1:])
    ref = dox_url + '?p=' + urllib.quote(target, safe='#')
    node = nodes.reference(rawtext, utils.unescape(text), refuri=ref, **options)
    return [node],[]

def loadDoxJson(app):
    """Handler for 'builder-inited' event.

    Loads dox JSON as built for the search index.
    """
    env = app.builder.env
    # Skip if already loaded the known dox names.
    if hasattr(env, 'known_dox_names'):
        app.info('Already loaded known_dox_names')
        return
    # If the doxlinks_json_path is not given then register the known names as
    # "None".
    json_path = env.config.doxlinks_dox_json
    if not json_path:
        app.warn('No doxlinks_dox_json given.')
        env.known_dox_names = None
        return
    # Build set of known names from dox.
    known_dox_names = set()
    if os.path.isfile(json_path):
        app.info('Reading %s' % json_path)
        with open(json_path, 'rb') as f:
            fcontents = f.read()
            fcontents = fcontents[fcontents.find('['):]
            for key in KEYS:
                fcontents = fcontents.replace('{%s:' % key, '{\'%s\':' % key)
                fcontents = fcontents.replace(',%s:' % key, ',\'%s\':' % key)
            fcontents = fcontents.replace('\'', '"')
            fcontents = fcontents[:fcontents.rfind(',')] + ']'
            jsondata = json.loads(fcontents)
            for record in jsondata:
                known_dox_names.add(record['name'])
                for subentry in record['subentries']:
                    known_dox_names.add(subentry['name'])
    else:
        app.warn('Could not read json file %s' % json_path)
    env.known_dox_names = known_dox_names


# setup function to register the extension

def setup(app):
    # Base URL for dox links.
    app.add_config_value('doxlinks_base_url',
                         'http://docs.seqan.de/seqan/dev3/',
                         'env')
    # Path to "search.data.js" file with dox index.
    app.add_config_value('doxlinks_dox_json',
                         'seqan/dox/html/js/search.data.js',
                         'env')
    # Automatically shorten nested (interface/member) names.
    app.add_config_value('shorten_nested_names', True,
                         'env')

    # Register makeSeqAnLink for :dox: role.
    app.add_role('dox', makeSeqAnLink)
    # Load JSON after builder initialized.
    app.connect('builder-inited', loadDoxJson)

