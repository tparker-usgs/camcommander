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
    rsync.append("--verbose --prune-empty-dirs --compress --archive --rsh ssh")
    rsync.append("{}:{}".format(config['name'], config['path']))
    rsync.append(config['scratch_dir'])
    rsync_cmd = " ".join(rsync)
    logger.debug("rsync: %s", rsync_cmd)
    output = os.popen(rsync_cmd, 'r')
    new_images = []
    for line in output:
        line = line.strip()
        if line.endswith(".jpg"):
            logger.info("New image %s", line)
            new_images.append(line)
        else:
            logger.debug("yada yada yada %s", line)
    logger.debug("All done with %s, new images: %d", config['name'],
                 len(new_images))

    return new_images


def flush_old_images(config):
    if 'retention' not in config:
        return

    ssh_cmd = 'ssh {} '' \
    + ''"find {} -name *.jpg -ctime +{} -print -exec rm {{}} \\;"'
    ssh_cmd = ssh_cmd.format(config['name'], config['path'],
                             config['retention'])
    logger.info("Flushing old images with: %s", ssh_cmd)
    output = os.popen(ssh_cmd, 'r')
    for line in output:
        logger.info(line.strip())


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


def check_source(config):
    scratch_dir = os.path.join(tutil.get_env_var('SCRATCH_DIR'),
                               config['name'])
    config['scratch_dir'] = scratch_dir
    new_images = get_new_images(config)
    if len(new_images) > 0:
        flush_old_images(config)
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

    config_path = sys.argv[1]
    if not os.path.isfile(config_path):
        msg = "Config doesn't exist, will try again next time. ({})"
        tutil.exit_with_error(msg.format(config_path))

    global global_config
    global_config = tutil.parse_config(config_path)

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