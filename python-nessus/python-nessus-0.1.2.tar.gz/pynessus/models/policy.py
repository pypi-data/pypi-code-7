__author__ = 'Quentin Kaiser'
__license__ = "Apache 2.0"
__version__ = "0.1"
__contact__ = "kaiserquentin@gmail.com"
__date__ = "2014/16/11"


class Policy(object):
    """
    A Nessus Policy instance.

    Attributes:

    _Google Python Style Guide:
    http://google-styleguide.googlecode.com/svn/trunk/pyguide.html
    """

    def __init__(self):
        """Constructor
        """
        self._id = -1
        self._db_id = -1
        self._object_id = 0
        self._name = None
        self._owner = None
        self._visibility = None
        self._shared = False
        self._user_permissions = 0
        self._timestamp = 0
        self._last_modification_date = 0
        self._creation_date = 0
        self._no_target = False

        # BASIC
        self._description = None
        self._allow_post_scan_report_editing = True

        # PORT SCANNING
        self._port_scan_range = 0
        self._consider_unscanned_port_as_closed = False
        self._nessus_snmp_scanner = False
        self._netstat_port_scanner_ssh = False
        self._ping_remote_host = False
        self._netstat_port_scanner_wmi = False
        self._nessus_tcp_scanner = False
        self._nessus_syn_scanner = False

        # PERFORMANCE
        self._max_checks_per_host = 5
        self._max_hosts_per_scan = 100
        self._network_receive_timeout = 5
        self._max_simultaneous_tcp_sessions_per_host = None
        self._max_simultaneous_tcp_sessions_per_scan = None
        self._reduce_parallel_connections_on_congestion = False
        self._use_kernel_congestion_detection = False

        # ADVANCED
        self._safe_checks = True
        self._silent_dependencies = True
        self._log_scan_details_to_server = False
        self._stop_host_scan_on_disconnect = False
        self._avoid_sequential_scan = False
        self._designate_hosts_by_their_dns_name = False

        self._settings = {}

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, _id):
        self._id = int(_id)

    @property
    def db_id(self):
        return self._db_id

    @db_id.setter
    def db_id(self, db_id):
        self._db_id = int(db_id)

    @property
    def object_id(self):
        return self._object_id

    @object_id.setter
    def object_id(self, object_id):
        self._object_id = int(object_id)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        self._description = description

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, owner):
        self._owner = owner

    @property
    def visibility(self):
        return self._visibility

    @visibility.setter
    def visibility(self, visibility):
        self._visibility = visibility

    @property
    def shared(self):
        return self._shared

    @shared.setter
    def shared(self, shared):
        self._shared = shared

    @property
    def user_permissions(self):
        return self._user_permissions

    @user_permissions.setter
    def user_permissions(self, user_permissions):
        self._user_permissions = user_permissions

    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp):
        self._timestamp = timestamp

    @property
    def last_modification_date(self):
        return self._last_modification_date

    @last_modification_date.setter
    def last_modification_date(self, last_modification_date):
        self._last_modification_date = last_modification_date

    @property
    def creation_date(self):
        return self._creation_date

    @creation_date.setter
    def creation_date(self, creation_date):
        self._creation_date = creation_date

    @property
    def no_target(self):
        return self._no_target

    @no_target.setter
    def no_target(self, no_target):
        self._no_target = no_target

    #BASIC
    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        self._description = description

    @property
    def allow_post_scan_report_editing(self):
        return self.allow_post_scan_report_editing

    @allow_post_scan_report_editing.setter
    def allow_post_scan_report_editing(self, allow_post_scan_report_editing):
        self._allow_post_scan_report_editing = allow_post_scan_report_editing

    # PORT SCANNING
    @property
    def port_scan_range(self):
        return self._port_scan_range

    @port_scan_range.setter
    def port_scan_range(self, port_scan_range):
        self._port_scan_range = port_scan_range

    @property
    def consider_unscanned_port_as_closed(self):
        return self._consider_unscanned_port_as_closed

    @consider_unscanned_port_as_closed.setter
    def consider_unscanned_port_as_closed(self, consider_unscanned_port_as_closed):
        self._consider_unscanned_port_as_closed = consider_unscanned_port_as_closed

    @property
    def nessus_snmp_scanner(self):
        return self._nessus_snmp_scanner

    @nessus_snmp_scanner.setter
    def nessus_snmp_scanner(self, nessus_snmp_scanner):
        self._nessus_snmp_scanner = nessus_snmp_scanner

    @property
    def netstat_port_scanner_ssh(self):
        return self._netstat_port_scanner_ssh

    @netstat_port_scanner_ssh.setter
    def netstat_port_scanner_ssh(self, netstat_port_scanner_ssh):
        self._netstat_port_scanner_ssh = netstat_port_scanner_ssh

    @property
    def ping_remote_host(self):
        return self._ping_remote_host

    @ping_remote_host.setter
    def ping_remote_host(self, ping_remote_host):
        self._ping_remote_host = ping_remote_host

    @property
    def netstat_port_scanner_wmi(self):
        return self._netstat_port_scanner_wmi

    @netstat_port_scanner_wmi.setter
    def netstat_port_scanner_wmi(self, netstat_port_scanner_wmi):
        self._netstat_port_scanner_wmi = netstat_port_scanner_wmi

    @property
    def nessus_tcp_scanner(self):
        return self._nessus_tcp_scanner

    @nessus_tcp_scanner.setter
    def nessus_tcp_scanner(self, nessus_tcp_scanner):
        self._nessus_tcp_scanner = nessus_tcp_scanner

    @property
    def nessus_syn_scanner(self):
        return self._nessus_syn_scanner

    @nessus_syn_scanner.setter
    def nessus_syn_scanner(self, nessus_syn_scanner):
        self._nessus_syn_scanner = nessus_syn_scanner

    # PERFORMANCE

    @property
    def max_checks_per_host(self):
        return self._max_checks_per_host

    @max_checks_per_host.setter
    def max_checks_per_host(self, max_checks_per_host):
        self._max_checks_per_host = max_checks_per_host

    @property
    def max_hosts_per_scan(self):
        return self._max_hosts_per_scan

    @max_hosts_per_scan.setter
    def max_hosts_per_scan(self, max_hosts_per_scan):
        self._max_hosts_per_scan = max_hosts_per_scan

    @property
    def network_receive_timeout(self):
        return self._network_receive_timeout

    @network_receive_timeout.setter
    def network_receive_timeout(self, network_receive_timeout):
        self._network_receive_timeout = network_receive_timeout

    @property
    def max_simultaneous_tcp_sessions_per_host(self):
        return self._max_simultaneous_tcp_sessions_per_host

    @max_simultaneous_tcp_sessions_per_host.setter
    def max_simultaneous_tcp_sessions_per_host(self, max_simultaneous_tcp_sessions_per_host):
        self._max_simultaneous_tcp_sessions_per_host = max_simultaneous_tcp_sessions_per_host

    @property
    def max_simultaneous_tcp_sessions_per_scan(self):
        return self._max_simultaneous_tcp_sessions_per_scan

    @max_simultaneous_tcp_sessions_per_scan.setter
    def max_simultaneous_tcp_sessions_per_scan(self, max_simultaneous_tcp_sessions_per_scan):
        self._max_simultaneous_tcp_sessions_per_scan = max_simultaneous_tcp_sessions_per_scan

    @property
    def reduce_parallel_connections_on_congestion(self):
        return self._reduce_parallel_connections_on_congestion

    @reduce_parallel_connections_on_congestion.setter
    def reduce_parallel_connections_on_congestion(self, reduce_parallel_connections_on_congestion):
        self._reduce_parallel_connections_on_congestion = reduce_parallel_connections_on_congestion

    @property
    def use_kernel_congestion_detection(self):
        return self._use_kernel_congestion_detection

    @use_kernel_congestion_detection.setter
    def use_kernel_congestion_detection(self, use_kernel_congestion_detection):
        self._use_kernel_congestion_detection = use_kernel_congestion_detection

    # ADVANCED
    @property
    def safe_checks(self):
        return self._safe_checks

    @safe_checks.setter
    def safe_checks(self, safe_checks):
        self._safe_checks = safe_checks

    @property
    def silent_dependencies(self):
        return self._silent_dependencies

    @silent_dependencies.setter
    def silent_dependencies(self, silent_dependencies):
        self._silent_dependencies = silent_dependencies

    @property
    def log_scan_details_to_server(self):
        return self._log_scan_details_to_server

    @log_scan_details_to_server.setter
    def log_scan_details_to_server(self, log_scan_details_to_server):
        self._log_scan_details_to_server = log_scan_details_to_server

    @property
    def stop_host_scan_on_disconnect(self):
        return self._stop_host_scan_on_disconnect

    @stop_host_scan_on_disconnect.setter
    def stop_host_scan_on_disconnect(self, stop_host_scan_on_disconnect):
        self._stop_host_scan_on_disconnect = stop_host_scan_on_disconnect

    @property
    def avoid_sequential_scan(self):
        return self._avoid_sequential_scan

    @avoid_sequential_scan.setter
    def avoid_sequential_scan(self, avoid_sequential_scan):
        self._avoid_sequential_scan = avoid_sequential_scan

    @property
    def designate_hosts_by_their_dns_name(self):
        return self._designate_hosts_by_their_dns_name

    @designate_hosts_by_their_dns_name.setter
    def designate_hosts_by_their_dns_name(self, designate_hosts_by_their_dns_name):
        self._designate_hosts_by_their_dns_name = designate_hosts_by_their_dns_name

    @property
    def settings(self):
        return self._settings

    @settings.setter
    def settings(self, value):
        self._settings = value