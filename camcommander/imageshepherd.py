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

from fetcher import RsyncFetcher
from watcher import ConsoleWatcher
import tomputils.util as tutil
import multiprocessing_logging
import zmq
from zmq.devices import ThreadDevice


CONFIG_FILE_ENV = 'IS_CONFIG_PATH'
REMOTE_PATTERN = '/*/%Y/%m/%d/*.jpg'
PROXY_FRONTEND = "tcp://*:5560"
PROXY_BACKEND = "tcp://*:5559"

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


def start_fetchers():
    fetcher = RsyncFetcher(global_config, PROXY_BACKEND)
    _thread.start_new_thread(fetcher.start)


def start_shippers():
    pass


def start_watchers():
    watcher = ConsoleWatcher(global_config, PROXY_FRONTEND)
    _thread.start_new_thread(watcher.start)


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
    start_watchers()
    start_shippers()
    start_fetchers()

    logger.info("Waiting for proxy to die")
    device.join()


if __name__ == '__main__':
    main()
