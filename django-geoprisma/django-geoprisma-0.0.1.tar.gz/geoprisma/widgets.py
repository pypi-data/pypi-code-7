from django import forms


class MyTextInput(forms.TextInput):

    def __init__(self):
        super(MyTextInput, self).__init__(attrs={'size': '50'})


class MyTypeNumberInput(forms.TextInput):
    input_type = 'number'

    def __init__(self):
        super(MyTypeNumberInput, self).__init__(attrs={'min': 10000})