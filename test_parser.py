from unittest import TestCase
import parser


class VimColorschemeParserTest(TestCase):

    def testColorNumberLookup(self):
        assert parser.get_fg_color(['1']) == '#800000'
        assert parser.get_fg_color(['32']) == '#0087d7'
        assert parser.get_fg_color(['99']) == '#875fff'
        assert parser.get_fg_color(['1000']) == '1000' # unknown returns original

    def testColorNameLookup(self):
        assert parser.get_fg_color(['Orchid2']) == '#ff87d7'
        assert parser.get_fg_color(['Wheat1']) == '#ffffaf'
        assert parser.get_fg_color(['mediumorchid4']) == '#7a378b'
        assert parser.get_fg_color(['wahoo']) == 'wahoo' # unknown returns original

    def testHexLookup(self):
        assert parser.get_fg_color(['#ffffff']) == '#ffffff' # hex values are skipped
        assert parser.get_fg_color(['#ffffff']) != '#000000'
