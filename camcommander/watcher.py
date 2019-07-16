#!/usr/bin/env python3
#
# I waive copyright and related rights in the this work worldwide
# through the CC0 1.0 Universal public domain dedication.
# https://creativecommons.org/publicdomain/zero/1.0/legalcode
#
# Author(s):
#   Tom Parker <tparker@usgs.gov>

""" watch for new webcam images."""


import zmq

import tomputils.util as tutil


class Watcher:
    def __init__(self, config, proxy_frontend, context=None):
        global logger
        logger = tutil.setup_logging("watcher errors")

        self.config = config
        self.context = context or zmq.Context().instance()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect(proxy_frontend)

    def watch(self):
        pass


def watcher_factory(config, proxy_frontend):
    if config["type"] == "console":
        msg = "Creating %s watcher %s."
        logger.debug(msg.format(config["name"], config["type"]))
        return ConsoleWatcher(config, proxy_frontend)
    else:
        error_msg = "Unkown watcher type %s for source %s"
        tutil.exit_with_error(error_msg.format(config["type"], config["name"]))


class ConsoleWatcher(Watcher):
    def watch(self):
        run = True
        while run:
            image = self.socket.recv()
            logger.info("New Image: %s", image)
