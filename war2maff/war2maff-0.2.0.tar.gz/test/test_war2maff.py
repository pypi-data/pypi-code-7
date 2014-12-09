import unittest
import war2maff
from lxml import etree as ET


class TestBasic(unittest.TestCase):
    SOUGHT_FOR_URL = \
        u'http://www.theatlantic.com/doc/print/194004/peter-viereck'
    BAD_ENC_URL = \
        u"http://news.bostonherald.com/localRegional/view.bg?articleid=41617"

    def test_parse_index_html(self):
        parser = war2maff.IndexURLParser('test/data/war_index.html')
        self.assertEqual(parser.url, self.SOUGHT_FOR_URL)

    def test_parse_index_html_no_metadata(self):
        parser = war2maff.IndexURLParser('test/data/war_index_NOMETA.html')
        self.assertEqual(parser.url, None)

    def test_parse_index_html_bad_encoding(self):
        parser = war2maff.IndexURLParser(
            'test/data/war_index_bad_encoding.html')
        self.assertEqual(parser.url, self.BAD_ENC_URL)

    def test_generated_rdf(self):
        in_html = 'test/data/war_index.html'
        relaxng = ET.RelaxNG(file="test/data/maff.rng")
        rdf = war2maff.generate_RDF(0, in_html)
        tree = ET.fromstring(rdf)
        relaxng.assertValid(tree)

if __name__ == '__main__':
    unittest.main()
