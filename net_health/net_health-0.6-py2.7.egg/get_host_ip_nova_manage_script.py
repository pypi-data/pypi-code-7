from nova.db.sqlalchemy.api import compute_node_get_all
from nova import context


ctx = context.get_admin_context()
print(dict((node['hypervisor_hostname'], node['host_ip'])
           for node in compute_node_get_all(ctx, True)))
