from rflint.common import TestRule, KeywordRule, ERROR, WARNING

class PipePreceededByHash(TestRule, KeywordRule):
    '''Warn about pipe-separated statements that have been commented out

    If you are using pipe-separated format, you shouldn't comment out 
    steps. Delete the step if it's not being used. 
    '''
    severity = WARNING

    def apply(self, testcase):
        for row in testcase.rows:
            if row.raw_text.startswith("#|"):
                self.report(testcase, "Line has been commented out", row.linenumber)
                

