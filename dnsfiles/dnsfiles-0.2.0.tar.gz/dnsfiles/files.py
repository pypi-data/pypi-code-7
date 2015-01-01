import os
import yaml

class DnsFileStore:

  def __init__(self, basedir):
    self.basedir = basedir

  def write_zone_file(self, zone, records):
    """
       Writes out the provided records to the file for the specified zone.
  
       zone is a string, while records is a list of dicts, where each dict has 
       'name', 'type', 'value', and 'ttl' fields.
    """
    zonepath = os.path.join(self.basedir, "zones")
    if not os.path.exists(zonepath):
      os.makedirs(zonepath)
    filename = os.path.join(zonepath, "%s.yml" % zone)
    with open(filename, "w") as f:
      f.write(yaml.dump(records, default_flow_style=False))

  def list_stored_zones(self):
    """
      Returns a list the names of zones stored in this filestore.
    """
    pass

  def read_zone_store(self, zone):
    """
       Reads the file for the specified zone and returns a list of records.
    """
    pass
