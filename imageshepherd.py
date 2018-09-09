#!/usr/bin/env python3
#
# I waive copyright and related rights in the this work worldwide
# through the CC0 1.0 Universal public domain dedication.
# https://creativecommons.org/publicdomain/zero/1.0/legalcode
#
# Author(s):
#   Tom Parker <tparker@usgs.gov>

""" fetch and ship webcam images."""
from string import Template
import signal
import logging
import errno
from multiprocessing import Process
import time
import math
import pathlib
import sys
import os

import ruamel.yaml
import tomputils.util as tutil
import multiprocessing_logging
import requests


CONFIG_FILE_ENV = 'CP_CONFIG_FILE'
REMOTE_PATTERN = '/*/%Y/%m/%d/*.jpg'

global_config = None


def get_new_images(config):
    rsync = ['rsync']
    rsync.append("--prune-empty-dirs --compress --archive")
    rsync.append('-rsh "ssh -i {}"'.format(config['ssh_key']))
    rsync.append("{}@{}:".format(config['user'], config['host']))
    rsync.append(os.path.join(tutil.get_env_var('SCRATCH_DIR'),
                              config['name']))

    output = os.popen(" ".join(rsync), 'r')

    return False


def main():
    # let ctrl-c work as it should.
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    global logger
    logger = tutil.setup_logging("webrelaypoker errors")
    multiprocessing_logging.install_mp_handler()

    if len(sys.argv) < 2:
        tutil.exit_with_error("usage: camrouter.py config")

    global global_config
    global_config = tutil.parse_config(sys.argv[1])
    for source in global_config['sources']:
        got_new_images = get_new_images(source)

    logger.debug("That's all for now, bye.")
    logging.shutdown()


if __name__ == '__main__':
    main()
