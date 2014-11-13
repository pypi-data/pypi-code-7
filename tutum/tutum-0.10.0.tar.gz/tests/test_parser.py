import unittest
import copy
import mock
import StringIO
import sys

from tutumcli.tutum_cli import patch_help_option, dispatch_cmds, initialize_parser
from tutumcli.exceptions import InternalError
import tutumcli

from help_output_text import *


class PatchHelpOptionTestCase(unittest.TestCase):
    def setUp(self):
        self.add_help_argv_list = [
            ['tutum'],
            ['tutum', 'service'],
            ['tutum', 'service', 'inspect'],
            ['tutum', 'service', 'logs'],
            ['tutum', 'service', 'redeploy'],
            ['tutum', 'service', 'run'],
            ['tutum', 'service', 'scale'],
            ['tutum', 'service', 'set'],
            ['tutum', 'service', 'start'],
            ['tutum', 'service', 'stop'],
            ['tutum', 'service', 'terminate'],
            ['tutum', 'build'],
            ['tutum', 'container'],
            ['tutum', 'container', 'inspect'],
            ['tutum', 'container', 'logs'],
            ['tutum', 'container', 'start'],
            ['tutum', 'container', 'stop'],
            ['tutum', 'container', 'terminate'],
            ['tutum', 'image'],
            ['tutum', 'image', 'register'],
            ['tutum', 'image', 'push'],
            ['tutum', 'image', 'rm'],
            ['tutum', 'image', 'search'],
            ['tutum', 'image', 'update'],
            ['tutum', 'node'],
            ['tutum', 'node', 'inspect'],
            ['tutum', 'node', 'rm'],
            ['tutum', 'nodecluster'],
            ['tutum', 'nodecluster', 'create'],
            ['tutum', 'nodecluster', 'inspect'],
            ['tutum', 'nodecluster', 'rm'],
            ['tutum', 'nodecluster', 'scale'],
        ]
        self.not_add_help_argv_list = [
            ["tutum", "service", "ps"],
            ["tutum", "container", "ps"],
            ["tutum", "image", "list"],
            ["tutum", "node", "list"],
            ["tutum", "nodecluster", "list"],
            ["tutum", "nodecluster", "provider"],
            ["tutum", "nodecluster", "region"],
            ['tutum', 'nodecluster', 'nodetype'],
            ["tutum", "container", "run", "-p", "80:80", "tutum/wordpress"],
        ]

    def test_parser_with_empty_args(self):
        args = []
        self.assertRaises(InternalError, patch_help_option, args)

    def test_help_append(self):
        for argv in self.add_help_argv_list:
            args = patch_help_option(argv)
            target = copy.copy(argv[1:])
            target.append('-h')
            self.assertEqual(target, args, "Help option not patch correctly: %s" % argv)

    def test_help_not_append(self):
        for argv in self.not_add_help_argv_list:
            args = patch_help_option(argv)
            self.assertEqual(argv[1:], args, "Should not patch help option correctly: %s" % argv)

    def test_help_append_with_debug_option(self):
        argvlist = copy.copy(self.add_help_argv_list)
        for argv in argvlist:
            argv.insert(1, "--debug")
            args = patch_help_option(argv)
            target = copy.copy(argv[1:])
            target.append('-h')
            self.assertEqual(target, args, "Help option not patch correctly: %s" % argv)

    def test_help_not_append_with_debug_option(self):
        argvlist = copy.copy(self.not_add_help_argv_list)
        for argv in argvlist:
            argv.insert(1, "--debug")
            args = patch_help_option(argv)
            self.assertEqual(argv[1:], args, "Should not patch help option correctly: %s" % argv)


class CommandsDispatchTestCase(unittest.TestCase):
    def setUp(self):
        self.parser = tutumcli.tutum_cli.initialize_parser()

    @mock.patch('tutumcli.tutum_cli.commands')
    def test_login_dispatch(self, mock_cmds):
        args = self.parser.parse_args(['login'])
        dispatch_cmds(args)
        mock_cmds.login.assert_called_with()

    @mock.patch('tutumcli.tutum_cli.commands')
    def test_build_dispatch(self, mock_cmds):
        args = self.parser.parse_args(['build', '-t', 'mysql', '.'])
        dispatch_cmds(args)
        mock_cmds.build.assert_called_with(args.tag, args.directory, args.quiet, args.no_cache)

    @mock.patch('tutumcli.tutum_cli.commands')
    def test_service_dispatch(self, mock_cmds):
        args = self.parser.parse_args(['service', 'inspect', 'id'])
        dispatch_cmds(args)
        mock_cmds.service_inspect.assert_called_with(args.identifier)

        args = self.parser.parse_args(['service', 'logs', 'id'])
        dispatch_cmds(args)
        mock_cmds.service_logs.assert_called_with(args.identifier)

        args = self.parser.parse_args(['service', 'ps'])
        dispatch_cmds(args)
        mock_cmds.service_ps.assert_called_with(args.quiet, args.status)

        args = self.parser.parse_args(['service', 'redeploy', '-t', 'latest', 'mysql'])
        dispatch_cmds(args)
        mock_cmds.service_redeploy.assert_called_with(args.identifier, args.tag)

        args = self.parser.parse_args(['service', 'run', 'mysql'])
        dispatch_cmds(args)
        mock_cmds.service_run.assert_called_with(image=args.image, name=args.name, cpu_shares=args.cpushares,
                                                 memory=args.memory,target_num_containers=args.target_num_containers, 
                                                 privileged=args.privileged,
                                                 run_command=args.run_command,
                                                 entrypoint=args.entrypoint, expose=args.expose, publish=args.publish,
                                                 envvars=args.env,
                                                 linked_to_service=args.link_service,
                                                 autorestart=args.autorestart,
                                                 autoreplace=args.autoreplace, autodestroy=args.autodestroy,
                                                 roles=args.role,
                                                 sequential=args.sequential)

        args = self.parser.parse_args(['service', 'scale', 'id', '3'])
        dispatch_cmds(args)
        mock_cmds.service_scale.assert_called_with(args.identifier, args.target_num_containers)

        args = self.parser.parse_args(['service', 'set', 'id'])
        dispatch_cmds(args)
        mock_cmds.service_set.assert_called_with(args.autorestart, args.autoreplace, args.autodestroy, args.identifier)

        args = self.parser.parse_args(['service', 'start', 'id'])
        dispatch_cmds(args)
        mock_cmds.service_start.assert_called_with(args.identifier)

        args = self.parser.parse_args(['service', 'stop', 'id'])
        dispatch_cmds(args)
        mock_cmds.service_stop.assert_called_with(args.identifier)

        args = self.parser.parse_args(['service', 'terminate', 'id'])
        dispatch_cmds(args)
        mock_cmds.service_terminate.assert_called_with(args.identifier)

    @mock.patch('tutumcli.tutum_cli.commands')
    def test_container_dispatch(self, mock_cmds):
        args = self.parser.parse_args(['container', 'inspect', 'id'])
        dispatch_cmds(args)
        mock_cmds.container_inspect.assert_called_with(args.identifier)

        args = self.parser.parse_args(['container', 'logs', 'id'])
        dispatch_cmds(args)
        mock_cmds.container_logs.assert_called_with(args.identifier)

        args = self.parser.parse_args(['container', 'ps'])
        dispatch_cmds(args)
        mock_cmds.container_ps.assert_called_with(args.identifier, args.quiet, args.status)

        args = self.parser.parse_args(['container', 'start', 'id'])
        dispatch_cmds(args)
        mock_cmds.container_start.assert_called_with(args.identifier)

        args = self.parser.parse_args(['container', 'stop', 'id'])
        dispatch_cmds(args)
        mock_cmds.container_stop.assert_called_with(args.identifier)

        args = self.parser.parse_args(['container', 'terminate', 'id'])
        dispatch_cmds(args)
        mock_cmds.container_terminate.assert_called_with(args.identifier)

    @mock.patch('tutumcli.tutum_cli.commands')
    def test_image_dispatch(self, mock_cmds):
        args = self.parser.parse_args(['image', 'list'])
        dispatch_cmds(args)
        mock_cmds.image_list.assert_called_with(args.quiet, args.jumpstarts, args.linux)

        args = self.parser.parse_args(['image', 'register', 'name'])
        dispatch_cmds(args)
        mock_cmds.image_register(args.image_name, args.description)

        args = self.parser.parse_args(['image', 'push', 'name'])
        dispatch_cmds(args)
        mock_cmds.image_push(args.name, args.public)

        args = self.parser.parse_args(['image', 'rm', 'name'])
        dispatch_cmds(args)
        mock_cmds.image_rm(args.image_name)

        args = self.parser.parse_args(['image', 'search', 'name'])
        dispatch_cmds(args)
        mock_cmds.image_search(args.query)

        args = self.parser.parse_args(['image', 'update', 'name'])
        dispatch_cmds(args)
        mock_cmds.image_update(args.image_name, args.username, args.password, args.description)

    @mock.patch('tutumcli.tutum_cli.commands')
    def test_node_dispatch(self, mock_cmds):
        args = self.parser.parse_args(['node', 'inspect', 'id'])
        dispatch_cmds(args)
        mock_cmds.node_inspect.assert_called_with(args.identifier)

        args = self.parser.parse_args(['node', 'list'])
        dispatch_cmds(args)
        mock_cmds.node_list(args.quiet)

        args = self.parser.parse_args(['node', 'rm', 'id'])
        dispatch_cmds(args)
        mock_cmds.node_rm(args.identifier)

    @mock.patch('tutumcli.tutum_cli.commands')
    def test_nodecluste_dispatch(self, mock_cmds):
        args = self.parser.parse_args(['nodecluster', 'create', 'name', '1', '2', '3'])
        dispatch_cmds(args)
        mock_cmds.nodecluster_create(args.target_num_nodes, args.name,
                                     args.provider, args.region, args.nodetype)

        args = self.parser.parse_args(['nodecluster', 'inspect', 'id'])
        dispatch_cmds(args)
        mock_cmds.nodecluster_inspect(args.identifier)

        args = self.parser.parse_args(['nodecluster', 'list'])
        dispatch_cmds(args)
        mock_cmds.nodecluster_list(args.quiet)

        args = self.parser.parse_args(['nodecluster', 'provider'])
        dispatch_cmds(args)
        mock_cmds.nodecluster_show_providers(args.quiet)

        args = self.parser.parse_args(['nodecluster', 'region', '-p', 'digitalocean'])
        dispatch_cmds(args)
        mock_cmds.nodecluster_show_regions(args.provider)

        args = self.parser.parse_args(['nodecluster', 'nodetype', '-r', 'ams1', '-p', 'digitalocean'])
        dispatch_cmds(args)
        mock_cmds.nodecluster_show_types(args.provider, args.region)

        args = self.parser.parse_args(['nodecluster', 'rm', 'id'])
        dispatch_cmds(args)
        mock_cmds.nodecluster_rm(args.identifier)

        args = self.parser.parse_args(['nodecluster', 'scale', 'id', '3'])
        dispatch_cmds(args)
        mock_cmds.nodecluster_scale(args.identifier, args.target_num_nodes)


class ParserTestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = self.buf = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.stdout

    def compare_output(self, output, args):
        parser = initialize_parser()
        argv = patch_help_option(args)

        parser.parse_args(argv)

        out = self.buf.getvalue()
        self.buf.truncate(0)

        self.assertEqual(' '.join(output.split()), ' '.join(out.split()))

    @mock.patch('tutumcli.tutum_cli.argparse.ArgumentParser.add_argument')
    @mock.patch('tutumcli.tutum_cli.argparse.ArgumentParser.exit')
    def test_tutum_version(self, mock_exit, mock_add_arg):
        initialize_parser()
        mock_add_arg.assert_any_call('-v', '--version', action='version', version='%(prog)s ' + tutumcli.__version__)

    @mock.patch('tutumcli.tutum_cli.argparse.ArgumentParser.exit')
    def test_tutum_help_output(self, mock_exit):
        self.compare_output(TUTUM, args=['tutum', '-h'])
        self.compare_output(TUTUM_BUILD, args=['tutum', 'build', '-h'])
        self.compare_output(TUTUM_CONTAINER, args=['tutum', 'container', '-h'])
        self.compare_output(TUTUM_CONTAINER_INSPECT, args=['tutum', 'container', 'inspect', '-h'])
        self.compare_output(TUTUM_CONTAINER_LOGS, args=['tutum', 'container', 'logs', '-h'])
        self.compare_output(TUTUM_CONTAINER_PS, args=['tutum', 'container', 'ps', '-h'])
        self.compare_output(TUTUM_CONTAINER_START, args=['tutum', 'container', 'start', '-h'])
        self.compare_output(TUTUM_CONTAINER_STOP, args=['tutum', 'container', 'stop', '-h'])
        self.compare_output(TUTUM_CONTAINER_TERMINATE, args=['tutum', 'container', 'terminate', '-h'])
        self.compare_output(TUTUM_SERVICE, args=['tutum', 'service', '-h'])
        self.compare_output(TUTUM_SERVICE_INSPECT, args=['tutum', 'service', 'inspect', '-h'])
        self.compare_output(TUTUM_SERVICE_LOGS, args=['tutum', 'service', 'logs', '-h'])
        self.compare_output(TUTUM_SERVICE_PS, args=['tutum', 'service', 'ps', '-h'])
        self.compare_output(TUTUM_SERVICE_REDEPLOY, args=['tutum', 'service', 'redeploy', '-h'])
        self.compare_output(TUTUM_SERVICE_RUN, args=['tutum', 'service', 'run', '-h'])
        self.compare_output(TUTUM_SERVICE_SCALE, args=['tutum', 'service', 'scale', '-h'])
        self.compare_output(TUTUM_SERVICE_SET, args=['tutum', 'service', 'set', '-h'])
        self.compare_output(TUTUM_SERVICE_START, args=['tutum', 'service', 'start', '-h'])
        self.compare_output(TUTUM_SERVICE_STOP, args=['tutum', 'service', 'stop', '-h'])
        self.compare_output(TUTUM_SERVICE_TERMINATE, args=['tutum', 'service', 'terminate', '-h'])
        self.compare_output(TUTUM_IMAGE, args=['tutum', 'image', '-h'])
        self.compare_output(TUTUM_IMAGE_LIST, args=['tutum', 'image', 'list', '-h'])
        self.compare_output(TUTUM_IMAGE_REGISTER, args=['tutum', 'image', 'register', '-h'])
        self.compare_output(TUTUM_IMAGE_PUSH, args=['tutum', 'image', 'push', '-h'])
        self.compare_output(TUTUM_IMAGE_RM, args=['tutum', 'image', 'rm', '-h'])
        self.compare_output(TUTUM_IMAGE_SEARCH, args=['tutum', 'image', 'search', '-h'])
        self.compare_output(TUTUM_IMAGE_UPDATE, args=['tutum', 'image', 'update', '-h'])
        self.compare_output(TUTUM_LOGIN, args=['tutum', 'login', '-h'])
        self.compare_output(TUTUM_NODE, args=['tutum', 'node', '-h'])
        self.compare_output(TUTUM_NODE_INSPECT, args=['tutum', 'node', 'inspect', '-h'])
        self.compare_output(TUTUM_NODE_LIST, args=['tutum', 'node', 'list', '-h'])
        self.compare_output(TUTUM_NODE_RM, args=['tutum', 'node', 'rm', '-h'])
        self.compare_output(TUTUM_NODECLUSTER, args=['tutum', 'nodecluster', '-h'])
        self.compare_output(TUTUM_NODECLUSTER_CREATE, args=['tutum', 'nodecluster', 'create', '-h'])
        self.compare_output(TUTUM_NODECLUSTER_INSPECT, args=['tutum', 'nodecluster', 'inspect', '-h'])
        self.compare_output(TUTUM_NODECLUSTER_LIST, args=['tutum', 'nodecluster', 'list', '-h'])
        self.compare_output(TUTUM_NODECLUSTER_RM, args=['tutum', 'nodecluster', 'rm', '-h'])
        self.compare_output(TUTUM_NODECLUSTER_SCALE, args=['tutum', 'nodecluster', 'scale', '-h'])
        self.compare_output(TUTUM_NODECLUSTER_PROVIDER, args=['tutum', 'nodecluster', 'provider', '-h'])
        self.compare_output(TUTUM_NODECLUSTER_REGION, args=['tutum', 'nodecluster', 'region', '-h'])
        self.compare_output(TUTUM_NODECLUSTER_NODETYPE, args=['tutum', 'nodecluster', 'nodetype', '-h'])
