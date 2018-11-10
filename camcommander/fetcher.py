#!/usr/bin/env python3
#
# I waive copyright and related rights in the this work worldwide
# through the CC0 1.0 Universal public domain dedication.
# https://creativecommons.org/publicdomain/zero/1.0/legalcode
#
# Author(s):
#   Tom Parker <tparker@usgs.gov>

""" fetch webcam images."""


import time

import zmq


class Fetcher:
    def __init__(self, config, proxy_backend, context=None):
        self.config = config
        self.context = context or zmq.Context().instance()
        self.socket = context.socket(zmq.PUB)
        self.socket.bind(proxy_backend)

    def start(self):
        while(True):
            self.fetch()
            time.sleep(self.config['interval'])

    def fetch(self):
        pass