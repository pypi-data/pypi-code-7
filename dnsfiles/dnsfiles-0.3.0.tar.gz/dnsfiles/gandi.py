import os

class GandiDns:

  def __init__(self):
    self.apikey = os.environ['GANDI_API_KEY']
    if not self.apikey:
      raise "api key NOT available"
    import xmlrpc.client as rpc
    self.api = rpc.ServerProxy('https://rpc.ote.gandi.net/xmlrpc/')
  
  def _record_to_df(self, record):
    return { 'name': record['name'],
             'type': record['type'],
             'value': record['value'],
             'ttl': record['ttl'],
           }

  def _df_records_for_zone(self, zone):
    records = self.api.domain.zone.record.list(self.apikey, zone['id'], zone['version'])
    return [ self._record_to_df(record) for record in records ]

  def list_zones(self):
    """
       Returns a dict mapping zone names to a list of records. (ignores public zones)

       A record is a dict containing keys 'name', 'type', 'value', 'ttl'. These 
       map directly to standard dns values.
    """
    gandi_zones = self.api.domain.zone.list(self.apikey)
    df_zones = [ (zone['name'], self._df_records_for_zone(zone)) for zone in gandi_zones if not zone['public'] ]
    return dict(df_zones)

  def list_domains(self):
    """
       Returns a dict mapping domains to zone names.
    """
    raise NotImplementedError("getting there...")

  def update_or_create_zone(self, zone_name, records):
    """
       Modifies the specified zone to contain exactly the specified records.
    """
    raise NotImplementedError("getting there...")

  def update_domain(self, domain_name, zone_name):
    """
       Modifies the specified domain to use the specified zone.
    """
    raise NotImplementedError("getting there...")


