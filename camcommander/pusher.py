#!/usr/bin/env python3
#
# I waive copyright and related rights in the this work worldwide
# through the CC0 1.0 Universal public domain dedication.
# https://creativecommons.org/publicdomain/zero/1.0/legalcode
#
# Author(s):
#   Tom Parker <tparker@usgs.gov>

""" push webcam images."""


import os

import zmq
import tomputils.util as tutil


class Pusher:
    def __init__(self, config, proxy_frontend, context=None):
        global logger
        logger = tutil.setup_logging("pusher errors")

        self.config = config
        self.context = context or zmq.Context().instance()
        self.socket = self.context.socket(zmq.SUB)
        logger.debug("Connecting to proxy on {}".format(proxy_frontend))
        self.socket.connect(proxy_frontend)

    def push(self):
        pass


class RsyncPusher(Pusher):
    def push(self):
        rsync = ['rsync']
        rsync.append("--verbose")
        rsync.append("--prune-empty-dirs")
        rsync.append("--compress")
        rsync.append("--archive")
        rsync.append("--rsh ssh")
        rsync.append(self.config['scratch_dir'])
        rsync.append("{}:{}".format(self.config['name'], self.config['path']))
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


def pusher_factory(config, proxy_frontend):
    if config['type'] == 'rsync':
        return RsyncPusher(config, proxy_frontend)
    else:
        error_msg = "Unkown pusher type {} for source {}"
        tutil.exit_with_error(error_msg.format(config['type'], config['name']))


def _is_image(image):
    pass
