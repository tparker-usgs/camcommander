#!/usr/bin/env python3
#
# I waive copyright and related rights in the this work worldwide
# through the CC0 1.0 Universal public domain dedication.
# https://creativecommons.org/publicdomain/zero/1.0/legalcode
#
# Author(s):
#   Tom Parker <tparker@usgs.gov>

""" fetch webcam images."""


import os

import zmq
import tomputils.util as tutil


class Fetcher:
    def __init__(self, config, proxy_backend, context=None):
        global logger
        logger = tutil.setup_logging("fetcher errors")

        self.config = config
        self.context = context or zmq.Context().instance()
        self.socket = self.context.socket(zmq.PUB)
        logger.debug("Connecting to proxy on {}".format(proxy_backend))
        self.socket.connect(proxy_backend)

    def start(self):
        self.fetch()

    def fetch(self):
        pass


class RsyncFetcher(Fetcher):
    def fetch(self):
        rsync = ['rsync']
        rsync.append("--verbose")
        rsync.append("--prune-empty-dirs")
        rsync.append("--compress")
        rsync.append("--archive")
        rsync.append("--delete")
        rsync.append("--rsh ssh")
        rsync.append("{}:{}".format(self.config['name'], self.config['path']))
        rsync.append(self.config['scratch_dir'])
        rsync_cmd = " ".join(rsync)
        logger.debug("rsync: %s", rsync_cmd)
        output = os.popen(rsync_cmd, 'r')
        new_images = []
        for line in output:
            line = line.strip()
            if _is_image(line):
                logger.info("New image %s", line)
                self.send(line)

                new_images.append(line)
            else:
                logger.debug("yada yada yada %s", line)
        logger.debug("All done with %s, new images: %d", self.config['name'],
                     len(new_images))


def _is_image(self, name):
    if name.endswith('.jpg'):
        return True
    else:
        return False


def fetcher_factory(config, proxy_backend):
    if config['type'] == 'rsync':
        return RsyncFetcher(config, proxy_backend)
    else:
        error_msg = "Unkown fetcher type {} for source {}"
        tutil.exit_with_error(error_msg.format(config['type'], config['name']))
