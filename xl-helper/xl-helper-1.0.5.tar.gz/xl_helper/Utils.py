import urllib2
import time


class Utils:

    def __init__(self):
        pass

    __base_download_url = "https://dist.xebialabs.com"

    @staticmethod
    def build_product_label(_version):
        return 'xl-deploy' if int(_version.split()[0][0]) >= 4 else 'deployit'

    @staticmethod
    def build_server_zip_name(_version):
        return "{server_dir_name}.zip". \
            format(server_dir_name=Utils.build_server_dir_name(_version))

    @staticmethod
    def build_cli_zip_name(_version):
        return "%s.zip" % Utils.build_cli_dir_name(_version)

    @staticmethod
    def build_cli_zip_url(_version):
        return "%s/". \
            format(server_dir_name=Utils.build_cli_dir_name(_version))

    @staticmethod
    def build_server_dir_name(_version):
        return "{product_label}-{version}-server". \
            format(version=_version, product_label=Utils.build_product_label(_version))

    @staticmethod
    def build_cli_dir_name(_version):
        return "{product_label}-{version}-cli". \
            format(version=_version, product_label=Utils.build_product_label(_version))

    @staticmethod
    def build_plugin_name(_version, _plugin_name):
        return "{plugin_name}-plugin-{version}.jar". \
            format(version=_version, plugin_name=_plugin_name)


    @staticmethod
    def build_url(_version, _xltype, _plugin_short_name=''):
        if _xltype == "server":
            return "{base_url}/{product_label}/{version}/{zip_name}" \
                .format(
                base_url=Utils.__base_download_url,
                version=_version,
                product_label=Utils.build_product_label(_version),
                zip_name=Utils.build_server_zip_name(_version)
            )

        elif _xltype == 'cli':
            return "{base_url}/{product_label}/{version}/{zip_name}" \
                .format(
                base_url=Utils.__base_download_url,
                version=_version,
                product_label=Utils.build_product_label(_version),
                zip_name=Utils.build_cli_zip_name(_version)
            )

        elif _xltype == "plugin":
            return "{base_url}/plugins/{short_plugin_name}-plugin/{version}/{plugin_name}". \
                format(base_url=Utils.__base_download_url, version=_version, short_plugin_name=_plugin_short_name,
                       plugin_name=Utils.build_plugin_name(_version, _plugin_short_name))


        else:
            raise Exception("Unknown artifact type %s for building URL" % _xltype)

    @staticmethod
    def post(method, req):
        # by default method is GET, to make it POST add_data to be called.
        if method == 'POST':
            req.add_data('')

    @staticmethod
    def open_url(url, method, handler=None):

        if handler is None:
            opener = urllib2.build_opener()
        else:
            opener = urllib2.build_opener(handler)

        req = urllib2.Request(url)
        Utils.post(method, req)
        opener.open(req)

        return opener

    @staticmethod
    def auth_and_open_url(url, method, user, password):
        password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, url, user, password)
        handler = urllib2.HTTPBasicAuthHandler(password_mgr)
        return Utils.open_url(url, method, handler)

    @staticmethod
    def download(url, target, username=None, password=None):
        print "Downloading {url} is being started".format(url=url)

        if username is not None:
            print "Authenticating with username %s" % username

        opener = Utils.auth_and_open_url(url, 'GET', username, password)
        urllib2.install_opener(opener)

        file_name = url.split('/')[-1]
        u = urllib2.urlopen(url)
        target_file = (target + '/' + file_name, target + file_name)[target.endswith('/')]

        with open(target_file, 'wb') as f:
            block_size = 8192

            counter = 0

            while True:
                counter += 1
                if counter % 10 == 0:
                    Utils.print_no_newline(".")
                file_buffer = u.read(block_size)
                if not file_buffer:
                    break

                f.write(file_buffer)

            f.close()

        print ""

        return target_file

    @staticmethod
    def print_no_newline(text):
        import sys

        sys.stdout.write(text)
        sys.stdout.flush()

    @staticmethod
    def wait_until(some_predicate, timeout=30, period=1, tick=False):
        must_end = time.time() + timeout
        while time.time() < must_end:
            if some_predicate():
                return True
            if tick:
                print ' ... tick ... '
            time.sleep(period)

        raise Exception("The expected event hasn't happened within %s sec." % timeout)
