#!/usr/bin/env python3
#
# I waive copyright and related rights in the this work worldwide
# through the CC0 1.0 Universal public domain dedication.
# https://creativecommons.org/publicdomain/zero/1.0/legalcode
#
# Author(s):
#   Tom Parker <tparker@usgs.gov>

""" Poke web relays to initial camera upload."""
from string import Template
import signal
import logging
import errno
from multiprocessing import Process
import time
import math
import pathlib

import ruamel.yaml
import tomputils.util as tutil
import multiprocessing_logging
import requests


CONFIG_FILE_ENV = 'WRP_CONFIG_FILE'
DEFAULT_CONFIG_FILE = '/tmp/wrp.yaml'
URL_TMPL = Template("http://${address}:${port}/state.xml"
                    "?relay${relayidx}State=2"
                    "&pulseTime${relayidx}=${pulse_duration}")


def parse_config():
    config_file = pathlib.Path(tutil.get_env_var(CONFIG_FILE_ENV,
                                                 default=DEFAULT_CONFIG_FILE))
    yaml = ruamel.yaml.YAML()
    config = None
    try:
        config = yaml.load(config_file)
    except ruamel.yaml.parser.ParserError as e1:
        logger.error("Cannot parse config file")
        tutil.exit_with_error(e1)
    except OSError as e:
        if e.errno == errno.EEXIST:
            logger.error("Cannot read config file %s", config_file)
            tutil.exit_with_error(e)
        else:
            raise
    return config


def poke_relay(relay):
    try:
        url = URL_TMPL.substitute(relay)
        logger.debug("Poking %s at %s", relay['name'], url)
        r = requests.get(url, timeout=relay['timeout'])
        if r.status_code == r.ok:
            logger.debug("Poked.")
        else:
            logger.error("%s resisted with a status code %d.". relay['name'],
                         r.status_code)
    finally:
        for handler in logger.handlers:
            handler.flush()


def poke_relays(relays):
    procs = []
    minute = math.floor(time.time() / 60)
    for relay in relays:
        if relay['disabled']:
            logger.debug("Skipping %s, it's disabled.", relay['name'])
            continue

        if minute % relay['interval'] == relay['minute_offset']:
            p = Process(target=poke_relay, args=(relay,))
            procs.append(p)
            p.start()

    return procs


def main():
    # let ctrl-c work as it should.
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    global logger
    logger = tutil.setup_logging("webrelaypoker errors")
    multiprocessing_logging.install_mp_handler()

    config = None
    try:
        config = parse_config()
    except KeyError:
        msg = "Environment variable %s unset, exiting.".format(CONFIG_FILE_ENV)
        tutil.exit_with_error(msg)

    procs = poke_relays(config['relays'])
    for proc in procs:
        proc.join()

    logger.debug("That's all for now, bye.")
    logging.shutdown()


if __name__ == '__main__':
    main()
