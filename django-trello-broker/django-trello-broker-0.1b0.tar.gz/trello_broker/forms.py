from django import forms
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from .models import BitBucketRepo, BitBucketRule


class BitBucketRepoAdminForm(forms.ModelForm):
    class Meta:
        model = BitBucketRepo
        fields = ('name', 'slug', 'access_key', 'trello_board')

    def clean_access_key(self):
        access_key = self.cleaned_data.get('access_key')
        slug = self.cleaned_data.get('slug')
        if slug:
            query = Q(slug=slug) & Q(access_key=access_key)
            if hasattr(self, 'instance'):
                query &= ~Q(pk=self.instance.pk)
            if BitBucketRepo.objects.filter(query).exists():
                raise forms.ValidationError(_(
                    'There is already a BitBucket Repo stored with the '
                    'same slug & access_key.'
                ))
        return access_key


class BitBucketRuleAdminForm(forms.ModelForm):
    class Meta:
        model = BitBucketRule
        fields = ('repo', 'action', 'update', 'archive', 'move', 'trello_list')

    def __init__(self, *args, **kwargs):
        super(BitBucketRuleAdminForm, self).__init__(*args, **kwargs)

    def clean_action(self):
        if 'action' not in self.cleaned_data:
            raise forms.ValidationError(_('This field is required.'))

        action = self.cleaned_data['action']
        query = Q(repo=self.cleaned_data['repo']) & \
                Q(action=action)
        if hasattr(self, 'instance'):
            query &= ~Q(pk=self.instance.pk)

        if BitBucketRule.objects.filter(query).exists():
            raise forms.ValidationError(_(
                'A matching rule already exists for this BitBucketRepo'
            ))
        return action

    def clean_trello_list(self):
        trello_list = self.cleaned_data.get('trello_list')
        if trello_list:
            if not self.cleaned_data.get('move', False):
                raise forms.ValidationError(_(
                    'Rule must have "Move" checked to select a Trello list'
                ))
        else:
            if self.cleaned_data.get('move', False):
                raise forms.ValidationError(_(
                    'This field is required when "Move" is checked.'
                ))
        return trello_list
