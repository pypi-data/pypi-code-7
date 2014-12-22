class TestExec(object):
    def __init__(self):
        return
    
    def run_this(self):
        x = 1
        y = 2
        self.z = x + y
        return

    def run_that(self):
        self.x = 1
        self.y = 2
        return

    def run_this_and_that(self):
        self.run_this()
        self.run_that()
        return
# end TestExec    
