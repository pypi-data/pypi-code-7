from dnsfiles.files import DnsFileStore
from dnsfiles.gandi import GandiDns

def init_store():
  return DnsFileStore('.')

def init_dns_service():
  return GandiDns()

def init(file_store, dns_service):
  for zone, records in dns_service.list_zones().items():
    file_store.write_zone_file(zone, records)

  
