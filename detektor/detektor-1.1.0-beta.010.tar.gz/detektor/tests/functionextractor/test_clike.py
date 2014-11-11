import unittest
from detektor.functionextractor.clike import ClikeFunctionExtractor


class TestClikeFunctionExtractor(unittest.TestCase):

    def test_extract_function(self):
        keywords = {
            'if', 'while'
        }
        functions = ClikeFunctionExtractor(keywords).extract("""
            void main(int i) {
                // Some code here
            }

            int[] test() {
            }

            Array<String> anotherTest() {
                if(i == 10) {
                    while(true) {
                        print("Something");
                    }
                }
            }
        """)
        self.assertEquals(len(functions), 3)
        self.assertEquals(functions[0].name, 'void main(int i)')
        self.assertEquals(functions[1].name, 'int[] test()')
        self.assertEquals(functions[2].name, 'Array<String> anotherTest()')
        self.assertEquals(functions[0].sourcecode.strip(), '// Some code here')
