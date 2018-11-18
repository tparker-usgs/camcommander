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
import time
import _thread

from .fetcher import fetcher_factory
from .watcher import watcher_factory

import tomputils.util as tutil
import multiprocessing_logging
import zmq
from zmq.devices import ThreadDevice


CONFIG_FILE_ENV = 'IS_CONFIG_PATH'
REMOTE_PATTERN = '/*/%Y/%m/%d/*.jpg'
PROXY_FRONTEND = "tcp://127.0.0.1:5560"
PROXY_BACKEND = "tcp://127.0.0.1:5559"

global_config = None


def deliver_images(config):
    logger.debug("Shipping images to %s", config['name'])
    rsync = ['rsync']
    rsync.append("-n")
    rsync.append("--verbose --prune-empty-dirs --compress --archive --rsh ssh")
    rsync.append(config['scratch_dir'])
    rsync.append("{}:{}".format(config['name'], config['path']))
    rsync_cmd = " ".join(rsync)
    logger.debug("rsync: %s", rsync_cmd)
    # output = os.popen(rsync_cmd, 'r')
    # for line in output:
    #     line = line.strip()
    #     if line.endswith(".jpg"):
    #         logger.info("Sent image %s", line)
    #     else:
    #         logger.debug("yada yada yada %s", line)
    logger.debug("Images delivered to %s", config['name'])


def start_proxy():
    logger.info("Starting proxy")
    device = ThreadDevice(zmq.FORWARDER, zmq.XSUB, zmq.XPUB)
    device.bind_in(PROXY_BACKEND)
    device.bind_out(PROXY_FRONTEND)
    device.start()

    return device


def start_fetchers(sources):
    for source in sources:
        fetcher = fetcher_factory(source, PROXY_BACKEND)
        _thread.start_new_thread(fetcher.start)
        logger.debug("Launched fetcher %s".format(source['name']))


def start_shippers():
    pass


def start_watchers(watchers):
    for watcher in watchers:
        watcher = watcher_factory(global_config, PROXY_FRONTEND)
    _thread.start_new_thread(watcher.start)
    logger.debug("Launched watcher %s".format(watcher['name']))


def main():
    # let ctrl-c work as it should.
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    global logger
    logger = tutil.setup_logging("imageshepherd errors")
    multiprocessing_logging.install_mp_handler()
    logger.info("Launching imageshepherd. Lets go!")

    global global_config
    global_config = None
    while global_config is None:
        try:
            config_file = tutil.get_env_var(CONFIG_FILE_ENV)
            global_config = tutil.parse_config(config_file)
        except FileNotFoundError:
            error = "Config file %s not found. ".format(CONFIG_FILE_ENV)
            error += "Lets wait a minute and look again."
            logger.info(error)
            time.sleep(60)
        time.sleep(1)

    device = start_proxy()
    if 'watchers' in global_config:
        start_watchers(global_config['watchers'])
    start_shippers()
    start_fetchers(global_config['sources'])

    logger.info("Waiting for proxy to die")
    device.join()


if __name__ == '__main__':
    main()
