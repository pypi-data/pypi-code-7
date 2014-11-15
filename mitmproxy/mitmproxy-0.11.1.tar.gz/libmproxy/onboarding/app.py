from __future__ import absolute_import
import flask
import os
from ..proxy import config

mapp = flask.Flask(__name__)
mapp.debug = True


def master():
    return flask.request.environ["mitmproxy.master"]


@mapp.route("/")
def index():
    return flask.render_template("index.html", section="home")


@mapp.route("/cert/pem")
def certs_pem():
    p = os.path.join(master().server.config.confdir, config.CONF_BASENAME + "-ca-cert.pem")
    return flask.Response(open(p, "rb").read(), mimetype='application/x-x509-ca-cert')


@mapp.route("/cert/p12")
def certs_p12():
    p = os.path.join(master().server.config.confdir, config.CONF_BASENAME + "-ca-cert.p12")
    return flask.Response(open(p, "rb").read(), mimetype='application/x-pkcs12')

