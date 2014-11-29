import logging
import unittest


def import_tests():
    from . import validators
    from . import field
    from . import form
    from . import formvalidators
    from . import errors


def get_all_test_suite():
    def start_logging():
        logging.basicConfig(level=logging.INFO, format="%(asctime)-15s:%(message)s", filename='test.log')
        logging.getLogger('formskit').info('\n\t*** TESTING STARTED ***')

    def create_test_suit():
        suite = unittest.TestLoader()
        prepered_all_test_cases = []
        for test_case in alltests:
            prepered_all_test_cases.append(
                suite.loadTestsFromTestCase(test_case)
            )
        return unittest.TestSuite(prepered_all_test_cases)

    start_logging()
    import_tests()
    return create_test_suit()
