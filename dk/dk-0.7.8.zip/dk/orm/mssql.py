
#
#  compile time (AST) objects.
#

import datetime, decimal


class Field(object):
    pass


typeconversion = {
    'int': int,
    'smallint': int,
    'tinyint': int,
    'bigint': int,
    'float': float,
    'bit': bool,
    'varchar': unicode,
    'nvarchar': unicode,
    'char': str,  # Y/N fields
    'datetime': datetime.datetime,
    'date': datetime.date,
    'decimal': decimal.Decimal,
    'text': unicode,
    }

typecnvstr = {  # maps to runtime functions (defined in base.py)
                # ::> function to apply to db data to create Python object.
    'int': 'int',
    'smallint': 'int',
    'tinyint': 'int',
    'bigint': 'int',
    'float': 'float',
    'bit': 'bool',
    'varchar': 'unicode',
    'nvarchar': 'unicode',
    'char': 'str',
    'datetime': 'datetime.datetime',
    'date': 'datetime.date',
    'decimal': 'decimal.Decimal',
    'text': 'unicode',
    'DATE': 'datetime2date',
    'TSQLDATE': 'tsqldate2date',
    'EMAIL': 'identity',
    'PHONE': 'identity',
    'BOOL': 'yesno2bool',
    'NOBOOL': 'yesno2bool',
    }

revtypecnv = {  # maps to runtime functions (defined in base.py)
                # ::> function to apply to Python object to get db data.
    'DATE': 'date2datetime',
    'TSQLDATE': 'date2tsqldate',
    'EMAIL': 'identity',
    'PHONE': 'identity',
    'BOOL': 'bool2yesno',
    'NOBOOL': 'bool2janei',
    }


def default_value(inforec):
    dfltval = inforec['COLUMN_DEFAULT']
    if dfltval == '(getdate())':
        return 'None'
    elif dfltval == '(NULL)':
        return 'None'
    return dfltval


class MSSqlField(Field):
    def __init__(self, inforec, cnvt, utf8extraction):
        self.dbname = inforec['COLUMN_NAME']
        self.name = self.dbname.lower()
        self.utf8 = utf8extraction
        self.dbtype = inforec['DATA_TYPE']
        self.position = inforec['ORDINAL_POSITION']
        self.null_allowed = inforec['IS_NULLABLE'] == 'YES'
        self.max_length = inforec['CHARACTER_MAXIMUM_LENGTH']
        self.default_value_literal = default_value(inforec)
        self.precision = inforec['NUMERIC_PRECISION']
        self.scale = inforec['NUMERIC_SCALE']
        self.dbencoding = inforec['CHARACTER_SET_NAME']
        self.pytype = typeconversion[self.dbtype]  # not needed?
        self.pytypestr = typecnvstr[self.dbtype]
        self.revtype = None
        self.uitype = self.dbtype
        
        self.convert = self.name in cnvt
        if self.convert:
            self.pytypestr = typecnvstr[cnvt[self.name]]
            self.revtype = revtypecnv[cnvt[self.name]]
            self.uitype = cnvt[self.name]  # #ui_type_conv.get(cnvt[self.name])

        self.pk = False   # will be set externally

    def __repr__(self):
        props = [k for k,v in self.__dict__.items()
                 if type(v) != type(self.__repr__)]
        return 'Field(\n  ' + '\n  '.join('%s = %s' % (p, repr(getattr(self, p))) for p in props) + '\n)\n'

    def doc(self):
        return self.dbname

    def marker(self):
        return  {
            'int': '%d',
            'float': '%f',
            'smallint': '%d',
            'tinyint': '%d',
            'bigint': '%d',
            'bit': '%d',
            'varchar': '%s',
            'char': '%s',
            'datetime': '%s',
            'decimal': '%s',
            'text': '%s', 
            }[self.dbtype]

    def select(self):
        if self.utf8 and (self.dbtype in ('varchar', 'text')):
            dbfield = 'dbo.utf2latin(%s)' % self.dbname
        else:
            dbfield = self.dbname
        return "%s as %s" % (dbfield, self.name)


"""
datatypes:
    int, varchar, bit, datetime, text
"""
