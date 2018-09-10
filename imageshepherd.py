#!/usr/bin/env python3
#
# I waive copyright and related rights in the this work worldwide
# through the CC0 1.0 Universal public domain dedication.
# https://creativecommons.org/publicdomain/zero/1.0/legalcode
#
# Author(s):
#   Tom Parker <tparker@usgs.gov>

""" fetch and ship webcam images."""
import signal
import logging
from multiprocessing import Process
import sys
import os

import tomputils.util as tutil
import multiprocessing_logging


CONFIG_FILE_ENV = 'CP_CONFIG_FILE'
REMOTE_PATTERN = '/*/%Y/%m/%d/*.jpg'

global_config = None


def get_new_images(config):
    rsync = ['rsync']
    rsync.append("--prune-empty-dirs --compress --archive --rsh ssh")
    rsync.append("{}:".format(config['name']))
    rsync.append(os.path.join(tutil.get_env_var('SCRATCH_DIR'),
                              config['name']))
    rsync_cmd = " ".join(rsync)
    logger.debug("rsync: %s", rsync_cmd)
    # output = os.popen(rsync_cmd, 'r')
    # logger.debug(output.read())
    return False


def deliver_images(config):
    pass


def check_source(config):
    scratch_dir = os.path.join(tutil.get_env_var('SCRATCH_DIR'),
                               config['name'])
    config['scratch_dir'] = scratch_dir
    got_new_images = get_new_images(config)
    if got_new_images:
        procs = []
        for destination in config['destinations']:
            destination['scratch_dir'] = config['scratch_dir']
            p = Process(target=deliver_images, args=(destination,))
            procs.append(p)
            p.start()

        for proc in procs:
            proc.join()


def main():
    # let ctrl-c work as it should.
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    global logger
    logger = tutil.setup_logging("imageshepherd errors")
    multiprocessing_logging.install_mp_handler()

    if len(sys.argv) < 2:
        tutil.exit_with_error("usage: imageshepherd.py config")

    global global_config
    global_config = tutil.parse_config(sys.argv[1])

    procs = []
    for source in global_config['sources']:
        p = Process(target=check_source, args=(source,))
        procs.append(p)
        p.start()

    for proc in procs:
        proc.join()

    logger.debug("That's all for now, bye.")
    logging.shutdown()


if __name__ == '__main__':
    main()
