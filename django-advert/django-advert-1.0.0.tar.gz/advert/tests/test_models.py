from django.contrib.auth import get_user_model
from django.test import TestCase
from advert.models import (STATUS_PUBLISHED, Advertiser, TextAdvertisement, 
                           BannerAdvertisement)

User = get_user_model()


class AdvertiserTestCase(TestCase):
    """ Test the Advertiser Model. """
    fixtures = ['./testproj/fixtures/data.json']

    def _create_advertiser(self, user, company_name, website):
        return Advertiser.objects.create(user=user, website=website, 
                                         company_name=company_name)

    def test_create_advertiser(self):
        """ Test Creating a new Advertiser. """
        company_name = 'Test Company'
        website = 'http://testcompany.com'
        user = User.objects.get(pk=1)
        advertiser = self._create_advertiser(user, company_name, website)
        self.assertEqual(advertiser.user, user)
        self.assertEqual(advertiser.__str__(), company_name)
        self.assertEqual(advertiser.company_name, company_name)
        self.assertEqual(advertiser.website, website)


    def test_delete_advertiser(self):
        """ Test Deleting an Advertiser. """
        company_name = 'Test Company'
        website = 'http://testcompany.com'
        user = User.objects.get(pk=1)
        advertiser = self._create_advertiser(user, company_name, website)
        advertiser_pk = advertiser.pk
        advertiser.delete()
        try:
            Advertiser.objects.get(pk=advertiser_pk)
        except Advertiser.DoesNotExist:
            pass
        else:
            self.fail('Advertiser should not exist.')

    def test_get_advertiser(self):
        """ Test Get the Advertiser. """
        company_name = 'Test Company'
        website = 'http://testcompany.com'
        user = User.objects.get(pk=1)
        advertiser = self._create_advertiser(user, company_name, website)
        try:
            advertiser2 = Advertiser.objects.get(pk=advertiser.pk)
        except Advertiser.DoesNotExist:
            self.fail('Advertiser must exist.')
        self.assertEqual(advertiser, advertiser2)

    def test_update_advertiser(self):
        """ Test Update the Advertiser. """
        company_name = 'Test Company'
        website = 'http://testcompany.com'
        user = User.objects.get(pk=1)
        company_name2 = 'Test Company 2'
        advertiser = self._create_advertiser(user, company_name, website)
        advertiser.company_name = company_name2
        advertiser.save()
        advertiser2 = Advertiser.objects.get(pk=advertiser.pk)
        self.assertEqual(advertiser2.company_name, company_name2)


class TextAdvertisementTestCase(TestCase):
    """ Test the Text Advertisement Model. """
    fixtures = ['./testproj/fixtures/data.json']

    def _create_advertisement(self, title, **kwargs):
        user = User.objects.get(pk=1)
        advertiser = Advertiser.objects.create(user=user, company_name='Test')
        return TextAdvertisement.objects.create(advertiser=advertiser, 
                                                title=title, **kwargs)

    def test_create_advertisement(self):
        """ Test Creating a new Text Advertisement object. """
        title = 'Test Title'
        content = 'Test Content'
        kwargs = {
            'content': content,
            'status': STATUS_PUBLISHED,
        }
        advertisement = self._create_advertisement(title, **kwargs)
        self.assertEqual(advertisement.title, title)
        self.assertEqual(advertisement.__str__(), title)
        self.assertEqual(advertisement.content, content)
        self.assertEqual(advertisement.status, STATUS_PUBLISHED)

    def test_delete_advertisement(self):
        """ Test Deleting a Text Advertisement object. """
        title = 'Test Title'
        advertisement = self._create_advertisement(title)
        advertisement_pk = advertisement.pk
        advertisement.delete()
        try:
            TextAdvertisement.objects.get(pk=advertisement_pk)
        except TextAdvertisement.DoesNotExist:
            pass
        else:
            self.fail('Text Advertisement should not exist.')

    def test_get_advertisement(self):
        """ Test Getting a Text Advertisement object. """
        title = 'Test Title'
        advertisement = self._create_advertisement(title)
        try:
            advertisement2 = TextAdvertisement.objects.get(pk=advertisement.pk)
        except TextAdvertisement.DoesNotExist:
            self.fail('Advertisement must exist.')
        self.assertEqual(advertisement.pk, advertisement2.pk)
        self.assertEqual(advertisement.title, advertisement2.title)

    def test_update_advertiser(self):
        """ Test Updating a Text Advertisement object. """
        title = 'Test Title'
        title2 = 'Test Title 2'
        content = 'Test Content'
        content2 = 'Test Content 2'
        kwargs = {'content': content}
        advertisement = self._create_advertisement(title, **kwargs)
        advertisement.title = title2
        advertisement.content = content2
        advertisement.save()
        advertisement2 = TextAdvertisement.objects.get(pk=advertisement.pk)
        self.assertEqual(advertisement2.title, title2)
        self.assertEqual(advertisement2.content, content2)