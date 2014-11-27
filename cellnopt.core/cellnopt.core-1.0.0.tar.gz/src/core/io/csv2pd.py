import os

import pandas as pd

__all__= ["SimpleDataFrame"]


class SimpleDataFrame(object):
    """This class provides aliases to pandas dataframe


        class MyClass(SimpleDataFrame):
            def __init__(self, filename, **kargs):
                super(MyClass, self).__init__(filename, **kargs)

        m = MyClass("test.csv")
        m.df # dataframe where is stored the contents of the CSV file
        m.columns #alias to m.df.columns
        m.index  # alias to m.df.index 

    """
    def __init__(self, filename, sheet=None, **kargs):
        self.filename = filename

        # extract the extension to dispatch the reader methods accordingly
        try:
            try:
                self._extension = os.path.splitext(filename)[1]
            except:
                raise ValueError("Could not extract the extension from {}".format(filename))

            # the dispatcher
            if self._extension == ".csv":
                self.read_csv(filename)
            elif self._extension == ".xlsx":
                # if xls document, the sheet name must be given
                if sheet == None:
                    raise ValueError("If an xlsx file is provided, sheet must be given")
                self.read_excel(filename, sheet)
            else:
                raise ValueError("Accepted file extension are .csv or .xlsx")
        except Exception, e:
            print(e)
            raise Exception

    def _get_df(self):
        return self.df
    data = property(_get_df)

    def _get_columns(self):
        return self.df.columns
    columns = property(_get_columns)

    def _get_index(self):
        return self.df.index
    index = property(_get_index)

    def read_csv(self, filename, **kargs):
        self.df = pd.read_csv(filename, **kargs)

    def read_excel(self, filename, sheet, **kargs):
        self.df = pd.read_excel(filename, sheet, **kargs)
