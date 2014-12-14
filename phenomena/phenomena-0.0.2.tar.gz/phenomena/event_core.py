"""The core event handler."""
import signal

from cognate.component_core import ComponentCore
from gevent import sleep, spawn
import zmq.green as zmq

from phenomena.command_message import CommandMessage
from phenomena.config_lock import global_config_lock, config_lock
from phenomena.connection_manager import ConnectionManager
from phenomena.controller import Controller


class EventCore(ComponentCore):
    """EventCore Class."""
    def __init__(self, command_port=60053, heartbeat=3, **kwargs):

        # initialize configurable attributes
        self.heartbeat = heartbeat
        self.command_port = command_port

        # execute the event core configuration
        ComponentCore.__init__(self, **kwargs)

        # configure the interrupt handlers and run state
        signal.signal(signal.SIGILL, self._signal_interrupt_handler)
        self._stopped = True

        # list of functions to call after config, but before event loop starts
        self._startup_hooks = list()

        # list of functions to call when after event loop is drained
        self._shutdown_hooks = list()

        # zmq context used to create sockets
        self._zmq_ctx = None

        # zmq poller used to retrieve messages
        self._poller = None

        # the service controller
        self._controller = None

        # input configs are of type input_socket_config.ListenerConfig
        self._connection_manager = ConnectionManager(self)
        self._active_input_sockets = None

    def cognate_options(self, arg_parser):
        arg_parser.add_argument('--heartbeat',
                                type=int,
                                default=self.heartbeat,
                                help='Set the heartbeat rate in seconds.')

    @property
    def controller(self):
        return self._controller

    @property
    def connection_manager(self):
        return self._connection_manager

    @property
    def is_stopped(self):
        return self._stopped

    def run(self):
        self._stopped = False

        self.log.info('Execution started with configuration : %s', self)

        # create the zmq context
        self._zmq_ctx = zmq.Context()

        # create poller loop
        self._poller = zmq.Poller()

        with global_config_lock:
            # initialize the control layer
            self._controller = Controller(event_core=self,
                                          port=self.command_port)
            self._poller.register(self._controller.listener, zmq.POLLIN)

            # initialize the output sockets

            # initialize the listener sockets
            self._active_input_sockets = []
            for sock_config in self._connection_manager.listener_configs:
                self.log.info('Configuring listener: %s', sock_config)
                # todo: raul - add actual socket creation logic

            # spawn the poller loop
            poller_loop_spawn = spawn(self._poll_loop_executable)
            sleep(0)

        # call the startup hooks before executing the loop
        for func in self._startup_hooks:
            func()

        # execute a run loop if one has been assigned
        # else wait for the poll loop to exit
        # ensure shutdown of poller loop
        poller_loop_spawn.join()
        self._clear_poller()

        with global_config_lock:
            # shutdown input sockets
            for sock in self._active_input_sockets:
                sock.close()

            self._listener_sockets = None

            # shutdown output sockets

            # shutdown command layer
            self._controller.close_connections()
            self._controller = None

        # destroy poller
        self._poller = None

        # destroy zmq context
        self._zmq_ctx = None

        # call shutdown hooks
        for func in self._shutdown_hooks:
            func()

        self.log.info('Execution terminated.')

    @config_lock
    def kill(self):
        # with self._config_lock:
        self.log.info('kill invoked.')
        kill_cmd = CommandMessage(cmd=CommandMessage.CMD_KILL)
        self._controller.signal_message(kill_cmd)

    @config_lock
    def register_startup_hook(self, func):
        self._startup_hooks.append(func)

    @config_lock
    def register_shutdown_hook(self, func):
        self._shutdown_hooks.append(func)

    def _clear_poller(self):
        self.log.info('Clearing poller.')

        count = 3
        while count > 0:
            count -= 1

            socks = dict(self._poller.poll(timeout=0.25))
            msg_found = False
            for sock in self._active_input_sockets:
                if socks.get(sock) == zmq.POLLIN:
                    msg_found = True
                    # todo: raul - add processing of message
                    spawn(sock.recv_handler, sock)

            if msg_found:
                count = 3

    def _poll_loop_executable(self):
        self.log.info('Starting run loop.')
        self._stopped = False
        while not self._stopped:
            socks = dict(self._poller.poll(timeout=self.heartbeat * 1000))

            if socks.get(self._controller.listener) == zmq.POLLIN:
                self._controller.handle_msg()

            for sock in self._active_input_sockets:
                if socks.get(sock) == zmq.POLLIN:
                    # todo: raul - add processing of msg
                    spawn(sock.recv_handler, sock)

            self.log.debug('Thump!, Thump!')

        self.log.info('Run loop shutdown.')
        sleep(0)  # yield to give other spawns a chance to terminate

    def _signal_interrupt_handler(self):
        self.kill()
