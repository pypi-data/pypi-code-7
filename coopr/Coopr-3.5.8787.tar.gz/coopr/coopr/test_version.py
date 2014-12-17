import pyutilib.th as unittest
import coopr.coopr as coopr

class TestCooprVersion(unittest.TestCase):

    def test_releaselevel(self):
        self.assertTrue(coopr.version_info[3] in ('trunk','VOTD','final'))

    def test_version(self):
        try:
            import pkg_resources
            version = pkg_resources.get_distribution('coopr').version
        except:
            self.skipTest('pkg_resources is not available')

        if coopr.version_info[3] == 'final':
            self.assertEquals(coopr.version, version)
        #else:
            #self.assertEquals(coopr.version.split(' ')[0], version)

        elif coopr.version_info[3] == 'trunk':
            self.assertEquals( tuple(int(x) for x in version.split('.')),
                               coopr.version_info[:2] )
            self.assertEquals( coopr.version_info[2], 0 )
        else:
            self.assertEquals( tuple(int(x) for x in version.split('.')),
                               coopr.version_info[:2] )
            self.assertNotEquals( coopr.version_info[2], 0 )
            
