from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from . import api

Q = models.Q

STATUS_ACTIVE = 0
STATUS_ARCHIVED = 1
STATUS_CHOICES = (
    (STATUS_ACTIVE, _('Active')),
    (STATUS_ARCHIVED, _('Archived')),
)


class BaseModel(models.Model):
    created = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True

    def __unicode__(self):
        return getattr(self, 'name', u'')

    def save(self, *args, **kwargs):
        self.modified = timezone.now()
        super(BaseModel, self).save(*args, **kwargs)


class TrelloToken(BaseModel):
    name = models.CharField(
        max_length=100,
        help_text=_('Name of the account. Used for internal identification'),
    )
    api_key = models.CharField(
        max_length=100,
        help_text=_('Get this from https://trello.com/1/appKey/generate'),
    )
    api_token = models.CharField(
        max_length=100,
        help_text=_(
            'Get this from https://trello.com/1/authorize?'
            'key=YOUR_API_KEY&name=Your+App+Name&expiration=never&'
            'response_type=token&scope=read,write'
        ),
    )

    class Meta:
        verbose_name = 'Trello Token'
        verbose_name_plural = 'Trello Tokens'

    @property
    def client(self):
        if not hasattr(self, '_api_client'):
            self._api_client = api.get_client(self)
        return self._api_client


class TrelloBoard(BaseModel):
    trello_token = models.ForeignKey('trello_broker.TrelloToken')
    name = models.CharField(max_length=100, blank=True)
    status = models.PositiveIntegerField(
        default=STATUS_ACTIVE,
        choices=STATUS_CHOICES,
    )
    trello_id = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Trello Board'
        verbose_name_plural = 'Trello Boards'

    def get_trello_json(self):
        return api.get_trello_board(self.trello_token, self.trello_id)

    def update_from_json(self, json_data=None):
        if not json_data:
            json_data = self.get_trello_json()
        if not self.name == json_data['name']:
            self.name = json_data['name']
        if bool(self.status) != json_data['closed']:
            self.status = int(json_data['closed'])
        self.save()

    def populate_all_lists(self, json_data=None):
        if not json_data:
            json_data = api.get_all_trello_board_lists(
                self.trello_token,
                self.trello_id,
            )

        all_list_ids = set()
        for list_data in json_data:
            all_list_ids.add(list_data['id'])
            _list = \
                self.trello_lists.filter(trello_id=list_data['id']).first()
            if _list:
                _list.update_from_json(json_data=list_data)
            else:
                _list = TrelloList.objects.create(
                    trello_board=self,
                    trello_id=list_data['id'],
                    name=list_data['name'],
                    status=int(list_data['closed']),
                )

        # Delete any db lists that are no longer living on Trello
        query = Q(trello_board=self) & \
                ~Q(trello_id__in=all_list_ids)
        TrelloList.objects.filter(query).delete()


class TrelloList(BaseModel):
    trello_board = models.ForeignKey(
        'trello_broker.TrelloBoard',
        related_name='trello_lists',
    )
    name = models.CharField(max_length=100)
    status = models.PositiveIntegerField(
        default=STATUS_ACTIVE,
        choices=STATUS_CHOICES,
    )
    trello_id = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Trello List'
        verbose_name_plural = 'Trello Lists'

    def get_trello_json(self):
        return api.get_trello_list(self.trello_token, self.trello_id)

    def update_from_json(self, json_data=None):
        if not json_data:
            json_data = self.get_trello_json()
        if self.name != json_data['name']:
            self.name = json_data['name']
        if bool(self.status) != json_data['closed']:
            self.status = int(json_data['closed'])
        self.save()

    def __unicode__(self):
        return u'{0}: {1}'.format(self.trello_board.name, self.name)


class BitBucketRepo(BaseModel):
    name = models.CharField(
        max_length=100,
        help_text=_('Name of the repo. Used for internal identification'),
    )
    slug = models.SlugField(
        max_length=100,
        help_text=_('Slug ID given by BitBucket for this repository.'),
    )
    access_key = models.CharField(
        max_length=100,
        blank=True,
        help_text=_(
            'Secret key used to "authenticate" the request. If saved '
            'here the key must be appended to the BitBucket hook URL like '
            'so: http://yourserver.com/broker/?access_key=YOUR_ACCESS_KEY'
        ),
    )
    trello_board = models.ForeignKey(
        'trello_broker.TrelloBoard',
        limit_choices_to={'status': STATUS_ACTIVE},
        related_name='repos',
    )

    class Meta:
        verbose_name = 'BitBucket Repository'
        verbose_name_plural = 'BitBucket Repositories'
        unique_together = ('slug', 'access_key')

    @property
    def fix_rule(self):
        if not hasattr(self, '_fix_rule'):
            self._fix_rule = self.rules.filter(
                action=BitBucketRule.ACTION_FIXES,
            ).first()
        return self._fix_rule

    @property
    def ref_rule(self):
        if not hasattr(self, '_ref_rule'):
            self._ref_rule = self.rules.filter(
                action=BitBucketRule.ACTION_REFERENCED,
            ).first()
        return self._ref_rule


class BitBucketRule(BaseModel):
    ACTION_REFERENCED = 1
    ACTION_FIXES = 2
    ACTION_CHOICES = (
        (ACTION_REFERENCED, _('Referenced')),
        (ACTION_FIXES, _('Fixes / Closes')),
    )
    repo = models.ForeignKey(
        'trello_broker.BitBucketRepo',
        related_name='rules',
    )
    action = models.PositiveIntegerField(
        choices=ACTION_CHOICES,
    )
    update = models.BooleanField(
        default=True,
        help_text=_('If checked, card will be updated with commit comment.'),
    )
    archive = models.BooleanField(
        default=False,
        help_text=_('If checked, card will be archived.'),
    )
    move = models.BooleanField(
        default=False,
        help_text=_('If checked, card will be moved '
                    'to specified Trello List.'),
    )
    trello_list = models.ForeignKey(
        'trello_broker.TrelloList',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'BitBucket Rule'
        verbose_name_plural = 'BitBucket Rules'
        unique_together = ('repo', 'action')

    def __unicode__(self):
        return u'{0}: {1}'.format(self.repo.name, self.get_action_display())
