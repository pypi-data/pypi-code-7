"""
Generate a random sample of rows from a relational database that preserves
referential integrity - so long as constraints are defined, all parent rows
will exist for child rows.

Good for creating test/development databases from production.  It's slow, 
but how often do you need to generate a test/development database?

Usage::

    rdbms-subsetter <source SQLAlchemy connection string> <destination connection string> <fraction of rows to use>

Example::

    rdbms-subsetter postgresql://:@/bigdb postgresql://:@/littledb 0.05

Valid SQLAlchemy connection strings are described 
`here <docs.sqlalchemy.org/en/latest/core/engines.html#database-urls#database-urls>`_.

``rdbms-subsetter`` promises that each child row will have whatever parent rows are 
required by its foreign keys.  It will also *try* to include most child rows belonging
to each parent row (up to the supplied ``--children`` parameter, default 3 each), but it
can't make any promises.  (Demanding all children can lead to infinite propagation in
thoroughly interlinked databases, as every child record demands new parent records,
which demand new child records, which demand new parent records...)

When row numbers in your tables vary wildly (tens to billions, for example),
consider using the ``-l`` flag, which reduces row counts by a logarithmic formula.  If ``f`` is
the fraction specified, and ``-l`` is set, and the original table has ``n`` rows,
then each new table's row target will be::

    math.pow(10, math.log10(n)*f)

A fraction of ``0.5`` seems to produce good results, converting 10 rows to 3,
1,000,000 to 1,000,000, and 1,000,000,000 to 31,622.

rdbms-subsetter guarantees that your child rows have the necessary parent rows to
satisfy the foreign keys.  It also *tries* to ensure that your parent rows have
child keys, but that becomes tricky when you have a complex web of foreign keys.
Creating children for a parent may require creating more parent rows in multiple
tables, each of which may call for their own children... that process can propagate
endlessly.  rdbms-subsetter cuts the propagation off eventually, but you can 
guarantee that specific tables will always have children by naming those tables
with ``require-children=<tablename>``.

Rows are selected randomly, but for tables with a single primary key column, you
can force rdbms-subsetter to include specific rows (and their dependencies) with
``force=<tablename>:<primary key value>``.

rdbms-subsetter only performs the INSERTS; it's your responsibility to set
up the target database first, with its foreign key constraints.  The easiest
way to do this is with your RDBMS's dump utility.  For example, for PostgreSQL,

::

    pg_dump --schema-only -f schemadump.sql source_database
    createdb partial_database
    psql -f schemadump.sql partial_database

Currently rdbms-subsetter takes no account of schema names and simply assumes all
tables live in the same schema.  This will probably cause horrible errors if used
against databases where foreign keys span schemas.

"""
import argparse
import logging
from collections import OrderedDict, deque
import math
import random
import types
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

__version__ = '0.1.2'

def _find_n_rows(self, estimate=False):
    self.n_rows = 0
    if estimate:
        try:
            if self.db.engine.driver in ('psycopg2', 'pg8000',):
                qry = """SELECT reltuples FROM pg_class 
	                 WHERE oid = '%s'::regclass""" % self.name
            elif 'oracle' in self.db.engine.driver:
                qry = """SELECT num_rows FROM all_tables
	                 WHERE table_name='%s'""" % self.name
            else:
                raise NotImplementedError("No approximation known for driver %s"
                                          % self.db.engine.driver)
            self.n_rows = self.db.conn.execute(qry).fetchone()[0]
        except Exception as e:
            logging.debug("failed to get approximate rowcount for %s\n%s" %
                          (self.name, str(e)))
    if not self.n_rows:
        self.n_rows = self.db.conn.execute(self.count()).fetchone()[0]

def _random_row_gen_fn(self):
    """
    Random sample of *approximate* size n
    """
    if self.n_rows:
        while True:
            n = self.target.n_rows_desired
            if self.n_rows > 1000:
                fraction = n / float(self.n_rows)
                qry = sa.sql.select([self,]).where(sa.sql.functions.random() < fraction)
                results = self.db.conn.execute(qry).fetchall()
                # we may stop wanting rows at any point, so shuffle them so as not to 
                # skew the sample toward those near the beginning 
                random.shuffle(results)
                for row in results:
                    yield row
            else:
                qry = sa.sql.select([self,]).order_by(sa.sql.functions.random()).limit(n)
                for row in self.db.conn.execute(qry):
                    yield row

def _next_row(self):
    try:
        return self.target.requested.popleft()
    except IndexError:
        try:
            return next(self.random_rows)
        except StopIteration:
            return None

def _filtered_by(self, **kw):
    slct = sa.sql.select([self,])
    slct = slct.where(sa.sql.and_((self.c[k] == v) for (k, v) in kw.items()))
    return slct

def _pk_val(self, row):
    if self.pk:
        return row[self.pk[0]]
    else:
        return None

def _by_pk(self, pk):
    pk_name = self.db.inspector.get_primary_keys(self.name)[0]
    slct = self.filtered_by(**({pk_name:pk}))
    return self.db.conn.execute(slct).fetchone()

def _exists(self, **kw):
    return bool(self.db.conn.execute(self.filtered_by(**kw)).first())

def _completeness_score(self):
    result = ( (self.n_rows / (self.n_rows_desired or 1))**0.33 - 
              (len(self.requested) / float(self.n_rows or 1 )) )
    return result
                  
class Db(object):

    def __init__(self, sqla_conn, args):
        self.args = args
        self.sqla_conn = sqla_conn
        self.engine = sa.create_engine(sqla_conn)
        self.meta = sa.MetaData(bind=self.engine)
        self.meta.reflect()
        self.inspector = Inspector(bind=self.engine)
        self.conn = self.engine.connect()
        self.tables = OrderedDict()
        for tbl in self.meta.sorted_tables:
            tbl.db = self
            tbl.find_n_rows = types.MethodType(_find_n_rows, tbl)
            tbl.fks = self.inspector.get_foreign_keys(tbl.name)
            tbl.pk = self.inspector.get_primary_keys(tbl.name)
            tbl.filtered_by = types.MethodType(_filtered_by, tbl)
            tbl.by_pk = types.MethodType(_by_pk, tbl)
            tbl.pk_val = types.MethodType(_pk_val, tbl)
            tbl.exists = types.MethodType(_exists, tbl)
            tbl.child_fks = []
            tbl.find_n_rows(estimate=True)
            self.tables[tbl.name] = tbl
        for (tbl_name, tbl) in self.tables.items():
            for fk in tbl.fks:
                fk['constrained_table'] = tbl_name
                self.tables[fk['referred_table']].child_fks.append(fk)

    def __repr__(self):
        return "Db('%s')" % self.sqla_conn

    def assign_target(self, target_db):
        for (tbl_name, tbl) in self.tables.items():
            tbl._random_row_gen_fn = types.MethodType(_random_row_gen_fn, tbl)
            tbl.random_rows = tbl._random_row_gen_fn()
            tbl.next_row = types.MethodType(_next_row, tbl)
            target = target_db.tables[tbl_name]
            target.requested = deque()
            if tbl.n_rows:
                if self.args.logarithmic:
                    target.n_rows_desired = int(math.pow(10, math.log10(tbl.n_rows)
                                                * self.args.fraction)) or 1
                else:
                    target.n_rows_desired = int(tbl.n_rows * self.args.fraction) or 1
            else:
                target.n_rows_desired = 0
            target.source = tbl
            tbl.target = target
            target.completeness_score = types.MethodType(_completeness_score, target)
            logging.debug("assigned methods to %s" % target.name)
              
    def confirm(self):
        for tbl_name in sorted(self.tables):
            tbl = self.tables[tbl_name]
            print("Create %d rows from %d in %s" % (tbl.target.n_rows_desired, tbl.n_rows, tbl_name))
        if self.args.yes:
            return True
        response = input("Proceed? (Y/n) ").strip().lower()
        return (not response) or (response[0] == 'y')
        

    def create_row_in(self, source_row, target_db, target, limit_children=True):
        logging.debug('create_row_in %s:%s ' % 
                      (target.name, target.pk_val(source_row)))

        if target.exists(**(dict(source_row))):
            logging.debug("Row already exists; not creating")
            return

            # make sure that all required rows1kkk are in parent table(s)
        for fk in target.fks: 
            target_parent = target_db.tables[fk['referred_table']]
            slct = sa.sql.select([target_parent,])
            any_non_null_key_columns = False
            for (parent_col, child_col) in zip(fk['referred_columns'], 
                                               fk['constrained_columns']):
                slct = slct.where(target_parent.c[parent_col] == 
                                  source_row[child_col])
                if source_row[child_col] is not None:
                    any_non_null_key_columns = True
            if any_non_null_key_columns:
                target_parent_row = target_db.conn.execute(slct).first()
                if not target_parent_row:
                    source_parent_row = self.conn.execute(slct).first()
                    self.create_row_in(source_parent_row, target_db, target_parent)
        ins = target.insert().values(**source_row)
        target_db.conn.execute(ins)
        target.n_rows += 1

        for child_fk in target.child_fks:
            child = self.tables[child_fk['constrained_table']]
            slct = sa.sql.select([child,])
            for (child_col, this_col) in zip(child_fk['constrained_columns'], 
                                             child_fk['referred_columns']):
                slct = slct.where(child.c[child_col] == source_row[this_col])
            if limit_children:
                slct = slct.limit(self.args.children)
            for (n, desired_row )in enumerate(self.conn.execute(slct)):
                if n == 0:
                    child.target.requested.appendleft(desired_row) 
                else:
                    child.target.requested.append(desired_row) 

    def create_subset_in(self, target_db):
       
        for (tbl_name, pks) in self.args.force_rows.items():
            source = self.tables[tbl_name]
            for pk in pks:
                source_row = source.by_pk(pk)  
                if source_row:
                    self.create_row_in(source_row, target_db, source.target, limit_children=False)
                else:
                    logging.warn("requested %s:%s not found in source db,"
                                 "could not create" % (source.name, pk))
      
        while True: 
            targets = sorted(target_db.tables.values(), 
                             key=lambda t: t.completeness_score())
            try:
                target = targets.pop(0)
                while not target.source.n_rows:
                    target = targets.pop(0)
            except IndexError: # pop failure, no more tables
                return
            logging.debug("total n_rows in target: %d" % 
                          sum((t.n_rows for t in target_db.tables.values())))
            logging.debug("target tables with 0 n_rows: %s" % 
                          ", ".join(t.name for t in target_db.tables.values() 
                                    if not t.n_rows))
            logging.info("lowest completeness score (in %s) at %f" %
                         (target.name, target.completeness_score()))
            if target.completeness_score() > 0.97:
                return
            source_row = target.source.next_row()
            self.create_row_in(source_row, target_db, target)
        

def fraction(n):
    n = float(n)        
    if 0 < n <= 1:
        return n
    raise argparse.ArgumentError('Fraction must be greater than 0 and no greater than 1')

all_loglevels = "CRITICAL, FATAL, ERROR, DEBUG, INFO, WARN, WARNING"
def loglevel(raw):
    try:
        return int(raw)
    except ValueError:
        upper = raw.upper()
        if upper in all_loglevels:
            return getattr(logging, upper)
        raise NotImplementedError('log level "%s" not one of %s' % (raw, all_loglevels))

argparser = argparse.ArgumentParser(description='Generate consistent subset of a database')
argparser.add_argument('source', help='SQLAlchemy connection string for data origin',
                       type=str)
argparser.add_argument('dest', help='SQLAlchemy connection string for data destination',
                       type=str)
argparser.add_argument('fraction', help='Proportion of rows to create in dest (0.0 to 1.0)',
                       type=fraction)
argparser.add_argument('-l', '--logarithmic', help='Cut row numbers logarithmically; use 0.5 for fraction', 
                       action='store_true')
argparser.add_argument('--loglevel', type=loglevel, help='log level (%s)' % all_loglevels,
                       default='INFO')
argparser.add_argument('-f', '--force', help='<table name>:<primary_key_val> to force into dest',
                       type=str.lower, action='append')
argparser.add_argument('-c', '--children', 
                       help='Max number of child rows to attempt to pull for each parent row',
                       type=int, default=3)
argparser.add_argument('-y', '--yes', help='Proceed without stopping for confirmation', action='store_true')

def generate():
    args = argparser.parse_args()
    args.force_rows = {}
    for force_row in (args.force or []):
        (table_name, pk) = force_row.split(':')
        if table_name not in args.force_rows:
            args.force_rows[table_name] = []
        args.force_rows[table_name].append(pk)
    logging.getLogger().setLevel(args.loglevel)
    source = Db(args.source, args)
    target = Db(args.dest, args)
    source.assign_target(target)
    if source.confirm():
        source.create_subset_in(target)
