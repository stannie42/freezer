"""
Copyright 2014 Hewlett-Packard

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

This product includes cryptographic software written by Eric Young
(eay@cryptsoft.com). This product includes software written by Tim
Hudson (tjh@cryptsoft.com).
========================================================================
"""

import logging
import os
import sys
from wsgiref import simple_server
import falcon
from keystonemiddleware import auth_token
from oslo.config import cfg

possible_topdir = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]),
                                   os.pardir, os.pardir, os.pardir))
if os.path.exists(os.path.join(possible_topdir, 'freezer_api', '__init__.py')):
    sys.path.insert(0, possible_topdir)

from freezer_api.common import config, log, exceptions
from freezer_api.api import v1
from freezer_api.api import versions
from freezer_api.api.common import middleware
from freezer_api.storage import driver


def get_application(db):
    app = falcon.API(middleware=[middleware.JSONTranslator()])

    for exception_class in exceptions.exception_handlers_catalog:
        app.add_error_handler(exception_class, exception_class.handle)

    endpoint_catalog = [
        ('/v1', v1.public_endpoints(db)),
        ('/', [('', versions.Resource())])
    ]
    for version_path, endpoints in endpoint_catalog:
        for route, resource in endpoints:
            app.add_route(version_path + route, resource)

    if 'keystone_authtoken' in config.CONF:
        app = auth_token.AuthProtocol(app, {})
    else:
        logging.warning("keystone authentication disabled")
    return app

config_file = '/etc/freezer-api.conf'
config_files_list = [config_file] if os.path.isfile(config_file) else []
config.parse_args(args=[], default_config_files=config_files_list)
log.setup()
logging.info("Freezer API starting")
logging.info("Freezer config file(s) used: {0}".format(
    ', '.join(cfg.CONF.config_file)))
try:
    db = driver.get_db()
    application = get_application(db)
except Exception as err:
    message = 'Unable to start server: {0}'.format(err)
    print message
    logging.fatal(message)
    sys.exit(1)


def main():
    ip, port = '127.0.0.1', 9090
    httpd = simple_server.make_server(ip, port, application)
    message = 'Server listening on {0}:{1}'.format(ip, port)
    print message
    logging.info(message)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print "\nThanks, Bye"
        sys.exit(0)


if __name__ == '__main__':
    main()
