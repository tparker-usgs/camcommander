#!/usr/bin/env python3
#
# I waive copyright and related rights in the this work worldwide
# through the CC0 1.0 Universal public domain dedication.
# https://creativecommons.org/publicdomain/zero/1.0/legalcode
#
# Author(s):
#   Tom Parker <tparker@usgs.gov>

""" fetch webcam images."""


import zmq

import tomputils.util as tutil


class Watcher:
    def __init__(self, config, proxy_frontend, context=None):
        global logger
        logger = tutil.setup_logging("watcher errors")

        self.config = config
        self.context = context or zmq.Context().instance()
        self.socket = context.socket(zmq.SUB)
        self.socket.connect(proxy_frontend)

    def start(self):
        self.watch()

    def watch(self):
        pass


class ConsoleWater(Watcher):
    def watch(self):
        run = True
        while run:
            image = self.socket.recv()
            logger.info("New Images: %s", image)
