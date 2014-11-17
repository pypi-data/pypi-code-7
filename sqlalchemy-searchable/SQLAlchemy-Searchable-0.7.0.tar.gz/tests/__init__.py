# -*- coding: utf-8 -*-
import itertools as it
import inspect

import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.query import Query
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils.types import TSVectorType
from sqlalchemy_searchable import (
    make_searchable, SearchQueryMixin, search_manager
)


make_searchable()


class TestCase(object):
    remove_symbols = '-@.'
    search_trigger_name = '{table}_{column}_trigger'
    search_index_name = '{table}_{column}_index'
    search_trigger_function_name = '{table}_{column}_update'

    def setup_method(self, method):
        self.engine = create_engine(
            'postgres://postgres@localhost/sqlalchemy_searchable_test'
        )
        self.Base = declarative_base()
        self.create_models()
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.create_tables()

    @property
    def options(self):
        return {
            'remove_symbols': self.remove_symbols,
            'search_trigger_name': self.search_trigger_name,
            'search_index_name': self.search_index_name,
            'search_trigger_function_name': self.search_trigger_function_name
        }

    def create_tables(self):
        self.Base.metadata.create_all(self.engine)

    def drop_tables(self):
        self.Base.metadata.drop_all(self.engine)

    def teardown_method(self, method):
        search_manager.processed_columns = []

        self.session.expunge_all()
        self.session.close_all()
        #self.session.remove()
        self.drop_tables()
        self.engine.dispose()

    def create_models(self):
        class TextItemQuery(Query, SearchQueryMixin):
            pass

        class TextItem(self.Base):
            __tablename__ = 'textitem'

            id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)

            name = sa.Column(sa.Unicode(255))

            search_vector = sa.Column(
                TSVectorType('name', 'content', **self.options)
            )

            content = sa.Column(sa.UnicodeText)

        class Order(self.Base):
            __tablename__ = 'order'
            id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
            name = sa.Column(sa.Unicode(255))
            search_vector = sa.Column(
                TSVectorType('name', **self.options)
            )

        class Article(TextItem):
            __tablename__ = 'article'
            id = sa.Column(
                sa.Integer, sa.ForeignKey(TextItem.id), primary_key=True
            )
            created_at = sa.Column(sa.DateTime)

        self.TextItemQuery = TextItemQuery
        self.TextItem = TextItem
        self.Order = Order
        self.Article = Article


class SchemaTestCase(TestCase):
    should_create_indexes = []
    should_create_triggers = []

    def test_creates_search_index(self):
        rows = self.session.execute(
            """SELECT relname
            FROM pg_class
            WHERE oid IN (
                SELECT indexrelid
                FROM pg_index, pg_class
                WHERE pg_class.relname='textitem'
                    AND pg_class.oid=pg_index.indrelid
                    AND indisunique != 't'
                    AND indisprimary != 't'
            ) ORDER BY relname"""
        ).fetchall()
        assert self.should_create_indexes == list(map(lambda a: a[0], rows))

    def test_creates_search_trigger(self):
        rows = self.session.execute(
            """SELECT DISTINCT trigger_name
            FROM information_schema.triggers
            WHERE event_object_table = 'textitem'
            AND trigger_schema NOT IN
                ('pg_catalog', 'information_schema')
            ORDER BY trigger_name"""
        ).fetchall()
        assert self.should_create_triggers == list(map(lambda a: a[0], rows))


setting_variants = {
    'remove_hyphens': [
        True,
        False
    ],
    'search_trigger_name': [
        '{table}_{column}_trigger',
        '{table}_{column}_trg'
    ],
    'search_index_name': [
        '{table}_{column}_index',
        '{table}_{column}_idx',
    ],
    'search_trigger_function_name': [
        '{table}_{column}_update_trigger',
        '{table}_{column}_update'
    ]
}


def create_test_cases(base_class, setting_variants=setting_variants):
    """
    Function for creating bunch of test case classes for given base class
    and setting variants. Number of test cases created is the number of linear
    combinations with setting variants.

    :param base_class:
        Base test case class, should be in format 'xxxTestCase'
    :param setting_variants:
        A dictionary with keys as versioned configuration option keys and
        values as list of possible option values.
    """
    names = sorted(setting_variants)
    combinations = [
        dict(zip(names, prod))
        for prod in
        it.product(*(setting_variants[name] for name in names))
    ]

    # Get the module where this function was called in.
    frm = inspect.stack()[1]
    module = inspect.getmodule(frm[0])

    class_suffix = base_class.__name__[0:-len('TestCase')]
    for index, combination in enumerate(combinations):
        class_name = 'Test%s%i' % (class_suffix, index)
        # Assign a new test case class for current module.
        setattr(
            module,
            class_name,
            type(
                class_name,
                (base_class, ),
                combination
            )
        )
