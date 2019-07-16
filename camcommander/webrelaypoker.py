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
from multiprocessing import Process
import time
import math

import tomputils.util as tutil
import multiprocessing_logging
import requests


CONFIG_FILE_ENV = "WRP_CONFIG_PATH"
URL_TMPL = Template(
    "http://${address}:${port}/state.xml"
    "?relay${relayidx}State=2"
    "&pulseTime${relayidx}=${pulse_duration}"
)


def poke_relay(relay):
    try:
        url = URL_TMPL.substitute(relay)
        logger.debug("Poking %s at %s", relay["name"], url)
        r = requests.get(url, timeout=relay["timeout"])
        r.raise_for_status()
        logger.info("Poked.")
    except requests.exceptions.ConnectionError:
        # The web relay doesn't return headers when sent a sate.xml request
        # urllib3 doesn't support HTTP/0.9 requests. What's to be done?
        msg = (
            "Web relay connection error. This is normal as the webrelay"
            + "doesn't provide a valid HTTP response to state.xml "
            + " requests, but it may also obscure other problems."
        )
        logging.info(msg)
    except requests.exceptions.ReadTimeout:
        logging.info("Time-out poking %s", relay["name"])
    except requests.exceptions.RequestException:
        logging.exception("%s resisted.", relay["name"])
    finally:
        for handler in logger.handlers:
            handler.flush()


def validate_relay(relay):
    if relay["minute_offset"] >= relay["interval"]:
        logger.error(
            "minute_offset must be smaller than interval." "(%d >= %d)",
            relay["minute_offset"],
            relay["interval"],
        )
        return False

    if relay["disabled"]:
        logger.debug("Skipping %s, it's disabled.", relay["name"])
        return False

    return True


def fork_poke_proc(relay):
    if not validate_relay(relay):
        return None

    minute = math.floor(time.time() / 60)
    minute_offset = minute % relay["interval"]
    p = None
    if minute_offset == relay["minute_offset"]:
        p = Process(target=poke_relay, args=(relay,))
        p.start()
    else:
        logger.debug(
            "Skipping %s, %d %% %d == %d not %d",
            relay["name"],
            minute,
            relay["interval"],
            minute_offset,
            relay["minute_offset"],
        )

    return p


def poke_relays(relays):
    procs = []
    for relay in relays:
        proc = fork_poke_proc(relay)
        if proc:
            procs.append(proc)

    return procs


def main():
    # let ctrl-c work as it should.
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    global logger
    logger = tutil.setup_logging("webrelaypoker errors")
    multiprocessing_logging.install_mp_handler()

    config = tutil.parse_config(tutil.get_env_var(CONFIG_FILE_ENV))
    procs = poke_relays(config["relays"])
    for proc in procs:
        proc.join()

    logger.debug("That's all for now, bye.")
    logging.shutdown()


if __name__ == "__main__":
    main()
