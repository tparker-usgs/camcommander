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
        self.socket = context.socket(zmq.PUB)
        self.socket.bind(proxy_backend)

    def start(self):
        self.fetch()

    def fetch(self):
        pass


def fetcher_factory(config, proxy_backend):
    if config['type'] is 'rsync':
        return RsyncFetcher(config, proxy_backend)
    else:
        error_msg = "Unkown fetcher type %s for source %s"
        tutil.exit_with_error(error_msg.format(config['type'], config['name']))


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
            if line.endswith(".jpg"):
                logger.info("New image %s", line)
                self.send(line)

                new_images.append(line)
            else:
                logger.debug("yada yada yada %s", line)
        logger.debug("All done with %s, new images: %d", self.config['name'],
                     len(new_images))
