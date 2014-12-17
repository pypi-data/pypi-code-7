import json
import logging
from collections import defaultdict


class LogFileHandler(logging.Handler):

    def __init__(self, filename, format, **kwargs):
        assert format in ('json', 'plain'), \
            'format has to be either "json" or "plain"'
        logging.Handler.__init__(self, **kwargs)
        self.filename = filename
        self.formatter = (
            self.render_plain
            if format == 'plain'
            else self.render_json)
        self.queries = defaultdict(list)
        self.current_test = None

    def render_plain(self, fp, queries):
        queries_list = queries.keys()
        queries_list.sort()
        for query in queries_list:
            for test in queries[query]:
                fp.write("-- %s\n" % str(test))
            fp.write(query.replace('\n', ' ').strip() + '\n')

    def render_json(self, fp, queries):
        json.dump(queries, fp)

    def emit(self, record):
        if (record.msg.startswith('SELECT') and
                self.current_test not in self.queries[record.msg]):
            self.queries[record.msg].append(self.current_test)

    def close(self):
        with open(self.filename, 'w') as fp:
            self.formatter(fp, self.queries)
