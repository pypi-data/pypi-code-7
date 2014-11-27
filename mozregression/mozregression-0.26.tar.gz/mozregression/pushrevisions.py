# first draft at something we may find useful later
def getPushRevisions(startRev, endRev, tree):
    if tree == 'mozilla-inbound':
        baseURL = 'https://hg.mozilla.org/integration/mozilla-inbound/'
    elif tree == 'mozilla-central':
        baseURL = 'https://hg.mozilla.org/mozilla-central/'
    else:
        raise Exception("Unknown tree '%s'" % tree)

    revisions = []
    r = requests.get('%sjson-pushes?fromchange=%s&tochange=%s'% (baseURL,
                                                                 startRev,
                                                                 endRev))
    pushlog = json.loads(r.content)
    for pushid in sorted(pushlog.keys()):
        push = pushlog[pushid]
        revisions.append((push['changesets'][-1], push['date']))

