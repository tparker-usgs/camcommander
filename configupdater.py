#!/usr/bin/env python3
#
# I waive copyright and related rights in the this work worldwide
# through the CC0 1.0 Universal public domain dedication.
# https://creativecommons.org/publicdomain/zero/1.0/legalcode
#
# Author(s):
#   Tom Parker <tparker@usgs.gov>

""" Watch config file for changes."""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import argparse
import logging
import signal
import requests
import os

import tomputils.util as tutil
import ruamel.yaml
import difflib
import svn.remote


def _arg_parse():
    description = "I look after a config file."
    parser = argparse.ArgumentParser(description=description)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--svnurl', help='Subversion URL of config file')
    group.add_argument('--url', help='URL of config file')
    parser.add_argument("--user", help="Username")
    parser.add_argument("--passwd", help="password")
    parser.add_argument("config", help="Local config path")

    return parser.parse_args()


def checkout_config(args):
    (path, file) = os.path.split(args.svnurl)

    r = svn.remote.RemoteClient(path, username=args.user, password=args.passwd)
    config = r.cat(file)

    return config.decode("utf-8")


def download_config(args):
    try:
        r = requests.get(args.url, auth=(args.user, args.passwd))
        r.raise_for_status()
        return r.text
    except requests.exceptions.RequestException as e:
        logger.error("Cannot retrieve config file from %s", args.url)
        tutil.exit_with_error(e)


def get_config(args):
    if args.svnurl:
        return checkout_config(args)
    else:
        return download_config(args)


def validate_config(config):
    try:
        yaml = ruamel.yaml.YAML()
        yaml.load(config)
    except ruamel.yaml.parser.ParserError as e1:
        logger.error("Cannot parse config file")
        tutil.exit_with_error(e1)


def write_config(config, local_path):
    with open(local_path, "w") as f:
            f.write(config)


def compare_config(new_config_str, local_path):
    try:
        with open(local_path, "r") as f:
            current_config = list(f)

        result = difflib.unified_diff(current_config,
                                      new_config_str.splitlines(True),
                                      fromfile=local_path)
        diff = list(result)
        if len(diff) > 0:
            logger.error("Configfile has changed.")
            logger.error("\n" + "".join(diff))
            write_config(new_config_str, local_path)
        else:
            logger.info("Configfile has not changed.")
    except FileNotFoundError:
        logger.error("Container restarted, cannot verify config.")
        write_config(new_config_str, local_path)


def main():
    # let ctrl-c work as it should.
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    global logger
    logger = tutil.setup_logging("CONFIG FILE ERROR")

    args = _arg_parse()

    new_config = get_config(args)
    validate_config(new_config)
    compare_config(new_config, args.config)

    logger.debug("That's all for now, bye.")
    logging.shutdown()


if __name__ == '__main__':
    main()
