from . import InstanceResource, ListResource


class Fax(InstanceResource):
    """
    A Fax instance
    """
    pass


class Faxes(ListResource):
    """
    A fax list
    """
    name = "Faxes"
    instance = Fax

    def list(self, **kwargs):
        """
        Returns a page of :class:`Fax` resources as a list.
        """
        return self.get_instances(kwargs)

    def create(self, from_=None, **kwargs):
        """
        Creates a Fax record. This sends a fax.

        :param str to: the number to send the fax to
        :param str from_: the Twilio number to send the fax from
        :param str document_url: the url of the content you want to fax
        :param str status_callback: the url to webhook at when status changes
        :return:
        """
        kwargs["from"] = from_
        return self.create_instance(kwargs)


class Document(InstanceResource):
    """
    A Document instance
    """
    pass


class Documents(ListResource):
    """
    A Document list
    """
    name = "Documents"
    instance = Document

    def list(self, **kwargs):
        """
        Returns a page of :class:`Document` resources as a list.
        :param kwargs:
        :return:
        """

