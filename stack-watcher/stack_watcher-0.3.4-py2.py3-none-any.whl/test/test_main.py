# coding: utf-8

import time
import unittest

from stack_watcher import (ClassLoader, Notifier, Question, Retriever,
                           RulesMixin)

# Python 3
try:
    from urllib.parse import parse_qs
    from urllib import parse as urllib
    from unittest import mock
    from pathlib import Path
# Python 2
except ImportError:
    import urllib as urllib
    from urlparse import parse_qs
    import mock
    from unipath import Path


def read_file(path):
    path = str(Path(__file__, '..', 'resources', path).resolve())

    with open(path) as fp:
        return fp.read().strip()


class Quest(RulesMixin, Question):
    """
    A question with rules, which it can use to determine whether it's valid.
    """
    pass


class SubRetriever(Retriever):
    """
    Only exists for unit testing the `ClassLoader` class.
    """
    pass


class SubNotifier(Notifier):
    """
    Only exists for unit testing the `ClassLoader` class.
    """
    pass


class LoadableClass(object):
    """
    Only exists to for unit testing the `ClassLoader` class.
    """
    loaded = True


class RetrieverTest(unittest.TestCase):

    def test_retriever_class_exists(self):
        """
        Does the `Retriever` class exist?
        """
        self.assertTrue('Retriever' in globals())

    def test_feed_url(self):
        """
        Does the `feed_url` property exist and work correctly?
        """
        retriever = Retriever()
        base_url, query = urllib.splitquery(retriever.feed_url)
        params = parse_qs(query)

        self.assertTrue(hasattr(retriever, 'feed_url'))

        # check default parameters
        self.assertFalse(params.get('tagged'))
        self.assertEqual('desc', params.get('order')[0])
        self.assertEqual('creation', params.get('sort')[0])
        self.assertEqual('stackoverflow', params.get('site')[0])

        retriever = Retriever(tag='professionalism', site='workplace')
        base_url, query = urllib.splitquery(retriever.feed_url)
        params = parse_qs(query)

        # check custom parameters
        self.assertEqual('professionalism', params.get('tagged')[0])
        self.assertEqual('desc', params.get('order')[0])
        self.assertEqual('creation', params.get('sort')[0])
        self.assertEqual('workplace', params.get('site')[0])

    @mock.patch('stack_watcher.requests.get', autospec=True)
    def test_get_feed_retrieves_feed(self, mock_requests):
        """
        Does `_get_feed` retrieve the feed?
        """
        retriever = Retriever()
        retriever._get_feed()
        mock_requests.assert_called_with(
            retriever.get_base_url(),
            params=retriever.params,
        )

    @mock.patch('stack_watcher.time.time', autospec=True)
    @mock.patch('stack_watcher.requests.get', autospec=True)
    def test_get_feed_updates_last_retrieved(self, mock_requests, mock_time):
        """
        Does `_get_feed` update the `last_retrieved` time?
        """
        mock_time.return_value = 123

        retriever = Retriever()
        retriever._get_feed()

        self.assertEqual(retriever.last_retrieved, 123)

    def test_parse_response(self):
        """
        Does `_parse_response` accept a HTTP requests response from the feed
        URL and return a list of question dicts?
        """
        mock_response = mock.Mock(**{
            'content.decode.return_value': read_file('feed.json'),
        })

        items = Retriever()._parse_response(mock_response)

        self.assertEqual(items[0]['question_id'], 22887117)
        self.assertEqual(len(items), 5)

    def test_custom_question_class(self):
        """
        Can we use a custom `Question` class?
        """
        retriever = Retriever(question_cls=mock.Mock)
        self.assertTrue(isinstance(retriever.question_cls(), mock.Mock))

    @mock.patch.object(Retriever, '_get_feed',  autospec=True)
    @mock.patch.object(Retriever, '_parse_response', autospec=True)
    def test_get_questions_from_feed_calls_get_feed(
        self,
        mock_parse_response,
        mock_get_feed,
    ):
        """
        Does `get_questions_from_feed` update the feed by calling `_get_feed`?
        """
        Retriever()._get_questions_from_feed()
        self.assertTrue(mock_get_feed.called)

    @mock.patch('stack_watcher.requests.get', autospec=True)
    def test_get_questions_from_feed_uses_custom_class(self, mock_requests):
        """
        Does `get_questions_from_feed` create `Question`-like instances with
        the correct question class?
        """
        mock_response = mock.Mock(**{
            'content.decode.return_value': read_file('feed.json'),
        })
        mock_requests.return_value = mock_response

        custom_type = type(
            'CustomQuestion',
            (Question, ),
            {'fantastic': True, }
        )

        retriever = Retriever(question_cls=custom_type)
        questions = retriever._get_questions_from_feed()

        self.assertTrue(isinstance(questions[0], custom_type))
        self.assertTrue(getattr(questions[0], 'fantastic'))

    def test_filter_new_questions(self):
        """
        Does `_filter_new_questions` return only the questions that haven't
        been seen?
        """
        retriever = Retriever()
        questions = [Question(question_id=id) for id in range(5)]

        self.assertListEqual(
            questions,
            retriever._filter_new_questions(questions),
        )

        self.assertListEqual(
            [],
            retriever._filter_new_questions(questions),
        )

    def test_filter_new_questions_empty_list(self):
        """
        Does `_filter_new_questions` work ok if passed an empty list?
        """
        self.assertListEqual([], Retriever()._filter_new_questions([]))

    @mock.patch.object(Retriever, '_get_questions_from_feed',  autospec=True)
    @mock.patch.object(Retriever, '_filter_new_questions', autospec=True)
    def test_disable_retriever(
        self,
        mock_filter_new_questions,
        mock_get_questions_from_feed,
    ):
        """
        Does `disable_retriever` stop questions from being retrieved?
        """
        retriever = Retriever()

        retriever.disable_retriever()
        retriever.questions()

        self.assertFalse(mock_get_questions_from_feed.called)
        self.assertFalse(mock_filter_new_questions.called)

    @mock.patch.object(Retriever, '_get_questions_from_feed',  autospec=True)
    @mock.patch.object(Retriever, '_filter_new_questions', autospec=True)
    def test_enable_retriever(
        self,
        mock_filter_new_questions,
        mock_get_questions_from_feed,
    ):
        """
        Does `enable_retriever` enable question retrieval?
        """
        retriever = Retriever()
        mock_filter_new_questions.return_value = [Question(), ]

        retriever._active = False
        retriever.questions()

        self.assertFalse(mock_get_questions_from_feed.called)
        self.assertFalse(mock_filter_new_questions.called)

        retriever.enable_retriever()

        for question in retriever.questions():
            retriever._active = False
            break

        self.assertTrue(mock_get_questions_from_feed.called)
        self.assertTrue(mock_filter_new_questions.called)

    @mock.patch('stack_watcher.requests.get', autospec=True)
    def test_questions(self, mock_requests):
        """
        Does the `questions` generator yield question objects correctly?
        """
        retriever = Retriever()

        mock_response = mock.Mock(**{
            'content.decode.return_value': read_file('feed.json'),
        })
        mock_requests.return_value = mock_response

        questions = []
        ids = [22887117, 22826113, 23460057, 23606124, 23431351]

        for question in retriever.questions():
            questions.append(question)

            if len(questions) == 5:
                retriever._active = False

        self.assertEqual(len(questions), 5)
        self.assertListEqual(ids, [q['question_id'] for q in questions])

    @mock.patch('stack_watcher.time.time', autospec=True)
    def test_delay_is_active(self, mock_time):
        """
        Does the `delay_is_active` property work correctly?
        """
        mock_time.return_value = -100
        self.assertTrue(Retriever().delay_is_active)

        mock_time.return_value = 100
        self.assertFalse(Retriever().delay_is_active)

    @mock.patch('stack_watcher.requests.get', autospec=True)
    @mock.patch('stack_watcher.time.sleep', autospec=True)
    @mock.patch.object(Retriever, '_get_questions_from_feed',  autospec=True)
    @mock.patch.object(Retriever, '_filter_new_questions', autospec=True)
    def test_questions_delay_interval(
        self,
        mock_get_questions_from_feed,
        mock_filter_new_questions,
        mock_sleep,
        mock_requests,
    ):
        """
        Does the `questions` generator enforce a delay interval?
        """
        r = Retriever()

        prop = mock.PropertyMock()
        prop.side_effect = [i != r.interval for i in range(r.interval + 1)]

        with mock.patch.object(Retriever, 'delay_is_active', prop):
            for i, question in enumerate(r.questions()):
                if i == 1:
                    break

        self.assertEqual(mock_sleep.call_count, r.interval)

    @mock.patch('stack_watcher.requests.get', autospec=True)
    def test_get_feed_no_throttling(self, mock_requests):
        """
        Does `_get_feed` return ok if there is no throttling?
        """
        mock_requests.return_value = True
        Retriever()._get_feed()

        self.assertEqual(mock_requests.called, 1)

    @mock.patch('stack_watcher.requests.get', autospec=True)
    @mock.patch('stack_watcher.time.sleep', autospec=True)
    def test_get_feed_throttled_not_implemented(
        self,
        mock_sleep,
        mock_requests,
    ):
        """
        Does `_get_feed` sleep when we're throttled and there is no
        `throttled` method implemented?
        """
        mock_requests.side_effect = iter([False, True])
        Retriever()._get_feed()

        self.assertEqual(mock_requests.call_count, 2)
        self.assertTrue(mock_sleep.called)

    @mock.patch('stack_watcher.requests.get', autospec=True)
    @mock.patch('stack_watcher.time.sleep', autospec=True)
    @mock.patch.object(Retriever, 'throttled', autospec=True)
    def test_get_feed_throttled(
        self,
        mock_throttled,
        mock_sleep,
        mock_requests,
    ):
        """
        Does `_get_feed` call the `throttled` method with no delay if it's
        implemented ok?
        """
        mock_requests.side_effect = iter([False, True])
        Retriever()._get_feed()

        self.assertEqual(mock_requests.call_count, 2)
        self.assertFalse(mock_sleep.called)
        self.assertTrue(mock_throttled.called)


class QuestionTest(unittest.TestCase):

    def setUp(self):
        self.question = {
            'question_id': 12345678,
            'title': 'Judith',
            'link': 'http://dirtymonkey.co.uk/judith',
            'score': 123,
            'is_answered': False,
            'view_count': 8000,
            'creation_date': int(time.time()),
            'text': "You're such an inspiration for the ways that I'll never…",
            'tags': [
                'maynard',
                'judith',
            ],
            'owner': {
                'user_id': 1,
                'display_name': 'Maynard James Keenan',
                'link': 'http://puscifer.com',
                'reputation': 1000000,
                'accept_rate': 100,
            },
        }

    def create_valid_question(self):
        """
        Utility function to create a Question that adheres to all rules.
        """
        question = Quest.from_dict(dict(**self.question))
        question.positive_tags = self.question['tags']

        return question

    def question_dict_equal(self, q, d=None):
        """
        Utility function to compare a question instance to a dict.
        """
        d = self.question if not d else d

        # maps `Question` attributes to our dict values in `question`
        attribute_map = [
            (q.question_id, d['question_id']),
            (q.title, d['title']),
            (q.link, d['link']),
            (q.score, d['score']),
            (q.answered, d['is_answered']),
            (q.view_count, d['view_count']),
            (q.creation_date, d['creation_date']),
            (q.text, d['text']),
            (q.tags, d['tags']),
            (q.owner_id, d['owner']['user_id']),
            (q.owner_display_name, d['owner']['display_name']),
            (q.owner_link, d['owner']['link']),
            (q.owner_reputation, d['owner']['reputation']),
            (q.owner_accept_rate, d['owner']['accept_rate']),
        ]

        return all([v[0] == v[1] for v in attribute_map])

    def test_question_class_exists(self):
        """
        Does the `Question` class exist?
        """
        self.assertTrue('Question' in globals())

    def test_question_has_tags(self):
        """
        If initialised with tags, does the question have them?
        """
        tags = ['django', 'reinhardt']
        self.assertEqual(Question(tags=tags).tags, tags)

    def test_tags_always_exist(self):
        """
        If initialised without tags, does it still exist?
        """
        question = Question()

        self.assertTrue(hasattr(question, 'tags'))
        self.assertEqual(question.tags, [])

    def test_always_has_question_attributes(self):
        """
        Does a question have the required attributes?
        """
        question = Question()

        question_attributes = [
            'question_id',
            'title',
            'link',
            'score',
            'answered',
            'view_count',
            'creation_date',
            'text',
            'owner_id',
            'owner_display_name',
            'owner_link',
            'owner_reputation',
            'owner_accept_rate',
        ]

        for attribute in question_attributes:
            self.assertTrue(hasattr(question, attribute))

    def test_attributes_passed_and_set(self):
        """
        Do attributes get set properly?
        """
        title = 'I Walk on Guilded Splinters'
        self.assertEqual(Question(title=title).title, title)

    def test_question_is_subscriptable(self):
        """
        Can question attributes be accessed in the same way as a dict?
        """
        title = 'I Walk on Guilded Splinters'
        self.assertEqual(Question(title=title)['title'], title)

    def test_create_question_instance_from_dict(self):
        """
        Can we create instances of `Question` using a dict?
        """
        self.assertTrue(
            self.question_dict_equal(
                Question.from_dict(dict(**self.question)),
            ),
        )

    def test_create_question_instances_from_list(self):
        """
        Can we create multiple instances of `Question` using a list of dicts?
        """
        questions = Question.from_list(
            [dict(**self.question) for _ in range(2)],
        )

        self.assertTrue(
            all([self.question_dict_equal(q) for q in questions]),
        )

    def test_rules_attribute(self):
        """
        Has the `rules` attribute been added via Question's meta class?
        """
        question = Question.from_dict(self.question)
        self.assertTrue(hasattr(question, 'rules'))

    def test_adheres_to_rules_check_every_rule(self):
        """
        Does `adheres_to_rules` retrieve every property whose name starts
        with `is_`?
        """
        question = Question.from_dict(self.question)
        property_mock = mock.PropertyMock()
        properties = [p for p in Question.__dict__ if p.startswith('is_')]

        for prop in properties:
            with mock.patch.object(Question, prop, property_mock):
                question.adheres_to_rules

        self.assertEqual(property_mock.call_count, len(properties))

    def test_adheres_to_rules_false(self):
        """
        Does `adheres_to_rules` work correctly and return False if any single
        property whose name begins with `is_` returns False?
        """
        question = Question.from_dict(self.question)
        false_property = mock.PropertyMock(return_value=False)
        properties = [p for p in Question.__dict__ if p.startswith('is_')]

        for prop in properties:
            with mock.patch.object(Question, prop, false_property):
                self.assertFalse(question.adheres_to_rules)

    def test_adheres_to_rules_true(self):
        """
        Does `adheres_to_rules` work correctly and return True if every single
        property whose name begins with `is_` returns True?
        """
        question = self.create_valid_question()
        self.assertTrue(question.adheres_to_rules)

    def test_is_not_answered_rule(self):
        """
        Does the `is_not_answered` rule exist and work correctly?
        """
        self.question['is_answered'] = True
        answered_question = Quest.from_dict(dict(**self.question))

        self.question['is_answered'] = False
        unanswered_question = Quest.from_dict(dict(**self.question))

        self.assertTrue(hasattr(Quest(), 'is_not_answered'))
        self.assertTrue(unanswered_question.is_not_answered)
        self.assertFalse(answered_question.is_not_answered)

    def test_is_new_rule(self):
        """
        Does the `is_new` rule exist and work correctly?
        """
        new_question = self.create_valid_question()

        self.question['creation_date'] = int(time.time()) - (60 * 60 * 6)
        old_question = Quest.from_dict(dict(**self.question))

        self.assertTrue(new_question.is_new)
        self.assertFalse(old_question.is_new)

    def test_is_including_positive_tags_rule(self):
        """
        Does the `is_including_positive_tags` rule exist and work correctly?
        """
        includes_positive_tags = self.create_valid_question()

        self.question['tags'] = []
        excludes_positive_tags = Quest.from_dict(dict(**self.question))

        self.assertTrue(includes_positive_tags.is_including_positive_tags)
        self.assertFalse(excludes_positive_tags.is_including_positive_tags)

    def test_is_excluding_negative_tags_rule(self):
        """
        Does the `is_excluding_negative_tags` rule exist and work correctly?
        """
        excludes_negative_tags = self.create_valid_question()

        self.question['tags'] = ['Russell Crowe', 'Golf', 'Bono']
        includes_negative_tags = Quest.from_dict(dict(**self.question))
        includes_negative_tags.negative_tags = self.question['tags']

        self.assertTrue(excludes_negative_tags.is_excluding_negative_tags)
        self.assertFalse(includes_negative_tags.is_excluding_negative_tags)

    def test_subclass_with_mixin_has_rules(self):
        """
        Do `Question` subclasses with rules mixed in have the `rules`
        attribute?
        """
        self.assertEqual(len(Quest().rules), 4)

    def test_get_short_link(self):
        """
        Does the `get_short_link` method work correctly?
        """
        pre = 'http://stackoverflow.com/questions/'

        urls = [
            (
                pre + '1327369/extract-contents-of-regex',
                pre + '1327369/',
            ),
            (
                pre + '23606124/python-django-bidi-brackets-issue-in-html-sel',
                pre + '23606124/',
            ),
            (
                pre + '24197506/how-to-get-1-100-between-numbers-in-python',
                pre + '24197506/',
            ),
            (
                pre + '24196040/retrieving-array-values-in-autohotkey-script',
                pre + '24196040/',
            ),
            (
                pre + '24197437/geektool-not-working-with-python3',
                pre + '24197437/',
            ),
            (
                pre + '4/when-setting-a-forms-opacity-should-i-use-a-decimal',
                pre + '4/',
            ),
            (
                'http://dirtymonkey.co.uk',
                'http://dirtymonkey.co.uk',
            ),
            (
                '',
                '',
            ),
        ]

        for url in urls:
            self.assertEqual(Quest(link=url[0]).get_short_link(), url[1])

    def test_get_short_title(self):
        """
        Does the `get_short_title` method work correctly?
        """
        titles = [
            ('', ''),
            ('Matt', 'Matt'),
            ('Matt Deacalion Stevens', 'Matt ...'),
            ('On this Day I Complete my Thirty-Sixth Year', 'On th...'),
            ('And Did Those Feet In Ancient Time', 'And D...'),
            ('Auguries of Innocence', 'Augur...'),
        ]

        for title in titles:
            self.assertEqual(
                Quest(title=title[0]).get_short_title(length=5),
                title[1],
            )

    def test_question_string_representation(self):
        """
        Does `Question` implement `__str__` so it shows a short URL and title?
        """
        question = Quest(
            link='http://stackoverflow.com/questions/1327369/extract-contents',
            title='A really long title... ' * 10,
        )

        self.assertEqual(len(str(question)), 117)


class NotifierTest(unittest.TestCase):

    def test_notifier_class_exists(self):
        """
        Does the `Notifier` class exist?
        """
        self.assertTrue('Notifier' in globals())


class ClassLoaderTest(unittest.TestCase):

    def test_class_loader_class_exists(self):
        """
        Does the `ClassLoader` class exist?
        """
        self.assertTrue('ClassLoader' in globals())

    def test_split_module_and_identifier(self):
        """
        Does the `split_import_path` method correctly divide a Python import
        path into the module and identifier components?
        """
        loader = ClassLoader()

        self.assertEqual(
            loader.split_import_path('stark'),
            ('', 'stark'),
        )
        self.assertEqual(
            loader.split_import_path('stark.lannister'),
            ('stark', 'lannister'),
        )
        self.assertEqual(
            loader.split_import_path('stark.lannister.baratheon'),
            ('stark.lannister', 'baratheon'),
        )

    def test_load_path_exception_wrong_path(self):
        """
        Does the `load` method raise an `ImportError` if the import fails?
        """
        loader = ClassLoader()

        with self.assertRaises(ImportError) as import_exception:
            loader.load('Lord.Baelish')

        self.assertEqual(
            str(import_exception.exception),
            'Could not import `Lord`, is it on sys.path?',
        )

    def test_load_path_exception_not_class(self):
        """
        Does the `load` method raise an `ImportError` if the identifier is not
        a class?
        """
        loader = ClassLoader()

        with self.assertRaises(ImportError) as import_exception:
            loader.load('re.IGNORECASE')

        self.assertEqual(
            str(import_exception.exception),
            '`IGNORECASE` must be a class',
        )

    def test_load_path_successfully_loads_class(self):
        """
        Does the `load` method return a Python class if everything is ok?
        """
        loader = ClassLoader()
        cls = loader.load('stack_watcher.test.test_main.LoadableClass')
        self.assertEqual(cls().loaded, True)

    def test_load_question_class_subclass_exception(self):
        """
        Does the `load_question_class` raise an exception if the identifier is
        not a subclass of `stack_watcher.Question`?
        """
        loader = ClassLoader()

        with self.assertRaises(ImportError) as import_exception:
            loader.load_question_class('io.StringIO')

        self.assertEqual(
            str(import_exception.exception),
            '`io.StringIO` must be a subclass of `stack_watcher.Question`.',
        )

    def test_load_question_class(self):
        """
        Does the `load_question_class` return a subclass of `Question` if
        everything is ok?
        """
        loader = ClassLoader()
        cls = loader.load_question_class(
            'stack_watcher.test.test_main.Quest',
        )
        self.assertEqual(cls.__name__, 'Quest')

    def test_load_retriever_class_subclass_exception(self):
        """
        Does the `load_retriever_class` raise an exception if the identifier is
        not a subclass of `stack_watcher.Retriever`?
        """
        loader = ClassLoader()

        with self.assertRaises(ImportError) as import_exception:
            loader.load_retriever_class('io.StringIO')

        self.assertEqual(
            str(import_exception.exception),
            '`io.StringIO` must be a subclass of `stack_watcher.Retriever`.',
        )

    def test_load_retriever_class(self):
        """
        Does the `load_retriever_class` return a subclass of `Retriever` if
        everything is ok?
        """
        loader = ClassLoader()
        cls = loader.load_retriever_class(
            'stack_watcher.test.test_main.SubRetriever',
        )
        self.assertEqual(cls.__name__, 'SubRetriever')

    def test_load_notifier_class_subclass_exception(self):
        """
        Does the `load_notifier_class` raise an exception if the identifier is
        not a subclass of `stack_watcher.Notifier`?
        """
        loader = ClassLoader()

        with self.assertRaises(ImportError) as import_exception:
            loader.load_notifier_class('io.StringIO')

        self.assertEqual(
            str(import_exception.exception),
            '`io.StringIO` must be a subclass of `stack_watcher.Notifier`.',
        )

    def test_load_notifier_class(self):
        """
        Does the `load_notifier_class` return a subclass of `Notifier` if
        everything is ok?
        """
        loader = ClassLoader()
        cls = loader.load_notifier_class(
            'stack_watcher.test.test_main.SubNotifier',
        )
        self.assertEqual(cls.__name__, 'SubNotifier')
