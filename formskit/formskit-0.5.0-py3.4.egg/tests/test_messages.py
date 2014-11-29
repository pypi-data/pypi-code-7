from formskit.messages import Message
from formskit.tests.base import FormskitTestCase


class MessageTests(FormskitTestCase):

    def test_casting(self):
        class InheritedMessage(Message):
            pass

        message = Message()
        message.init('text', 'one', two='two')

        casted = InheritedMessage(message)

        assert casted.text == 'text'
        assert casted.args == ('one',)
        assert casted.kwargs == {'two': 'two'}

    def test_normaln_translating(self):
        message = Message()
        message.init('text {0} {two}', 'one', two='two')

        assert message() == 'text one two'

    def test_inherited_translation(self):
        class InheritedMessage(Message):

            def translate(self):
                return self.text + 'something'

        message = Message()
        message.init('text {0} {two}', 'one', two='two')

        casted = InheritedMessage(message)
        assert casted() == 'text one twosomething'
