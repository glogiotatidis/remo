from happyforms import forms


class RangePollChoiceForm(forms.Form):
    """Range voting vote form."""
    def __init__(self, *args, **kwargs):
        """Initialize form

        Dynamically set fields for the participants in a range voting.
        """
        choices = kwargs.pop('extra')
        super(RangePollChoiceForm, self).__init__(*args, **kwargs)
        nominees = [(i, '%d' % i) for i in range(0, len(choices)+1)]
        for choice in choices:
            field_name = '%s %s' % (choice.nominee.first_name,
                                    choice.nominee.last_name)
            self.fields[str(choice.id) + '__' +
                        field_name] = forms.ChoiceField(widget=forms.Select(),
                                                        choices=nominees,
                                                        label=field_name)


class RadioPollChoiceForm(forms.Form):
    """Radio voting vote form."""
    def __init__(self, answers, *args, **kwargs):
        """Initialize form

        Dynamically set field for the answers in a radio voting.
        """
        super(RadioPollChoiceForm, self).__init__(*args, **kwargs)
        total_answers = []
        for i, answer in enumerate(answers):
            total_answers.append((i, answer))
        field_name = '%s' % answer
        self.fields[field_name] = forms.ChoiceField(widget=forms.Select(),
                                                    choices=total_answers,
                                                    label=field_name)
