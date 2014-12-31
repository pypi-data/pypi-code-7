from service import service


class QuantGoService(object):
    """API client class that allows to query service API for service data."""

    def __init__(self):
        self._service_client = service

    def get_data(self, service, params, container):
        """Call this method to request data from QuantGo. Returned data will be
        stored in container object passed as argument.
        :Example:

        from service_cli.qgservice import QuantGoService
        with open('ibm.csv', 'w') as result_container:
            QuantGoService().get_data(
                6796,
                {"TickerNames": ["IBM"], "Header": True, "Date": "20130909"},
                result_container)

        :param int service: requested service id. User must be subscribed to
        service to be able to get service data.
        :param dict params: request parameters dict. Please refer to QuantGo
        service documentation for request parameters details.
        :param filelike container: filelike object to store requested data
        """
        if not hasattr(container, 'write'):
            raise ValueError('Container object must support write method.')
        service_params = {'params': params, 'service': service}
        return self._service_client('get-data', service_params,
                                    stdout=container)

    def get_service_specific(self, service, params, container):
        """This method allows to retrieve service specific data that does not
        fall under any standard category, i.e: data that is not of standard
        format or that are not historical data. Please refer to specific data
        service documentation for more information.

        :Example:

        with open('ibm.csv', 'w') as result_container:
            QuantGoService().get_service_specific(
                39, {"ServiceAction": "master_file",
                     "Date":"20140303", "Header": False},
                result_container)

        :param int service: requested service id. User must be subscribed to
        service to be able to get service data.
        :param dict params: request parameters dict. Please refer to QuantGo
        service documentation for request parameters details.
        :param filelike container: filelike object to store requested data
        """
        service_params = {'params': params, 'service': service}
        return self._service_client('get-service-specific', service_params,
                                    stdout=container)

    def search_services(self, params):
        """Allows to search through QuantGo services. Takes search parameters
        as argument. For search criteria parameters refer to QuantGo services
        documentation.
        :Example:

        from service_cli.qgservice import QuantGoService
        QuantGoService().search_services({"DataPartner": "algo seek"})

        :param dict params: search criteria.
        """
        service_params = {'params': params}
        return self._service_client('search-services', service_params)

    def list(self):
        """Returns list of all QuantGo services. Please note this list is quite
        big and it may take some time to retrieve it.
        :Example:

        from service_cli.qgservice import QuantGoService
        QuantGoService().list()
        """
        return self._service_client('list', {})

    def list_available(self):
        """Returns list of subscribed QuantGo services.
        :Example:

        from service_cli.qgservice import QuantGoService
        QuantGoService().list_available()
        """
        return self._service_client('available', {})

    def description(self, service):
        """Returns description of requested service.
        :Example:

        from service_cli.qgservice import QuantGoService
        QuantGoService().list_available()

        :param int service: service id.
        """
        service_params = {'service': service}
        return self._service_client('description', service_params)

    def countries(self):
        """Returns list of available countries.
        :Example:

        from service_cli.qgservice import QuantGoService
        QuantGoService().countries()
        """
        return self._service_client('countries', {})

    def partners(self):
        """Returns list of QuantGo data partners.
        :Example:

        from service_cli.qgservice import QuantGoService
        QuantGoService().partners()
        """
        return self._service_client('partners', {})

    def data_types(self):
        """Returns list of available data types.
        :Example:

        from service_cli.qgservice import QuantGoService
        QuantGoService().data_types()
        """
        return self._service_client('data-types', {})
