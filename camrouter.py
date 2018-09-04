# #!/usr/bin/env python3
# #
# # I waive copyright and related rights in the this work worldwide
# # through the CC0 1.0 Universal public domain dedication.
# # https://creativecommons.org/publicdomain/zero/1.0/legalcode
# #
# # Author(s):
# #   Tom Parker <tparker@usgs.gov>
#
# """ fetch and ship webcam images."""
# from string import Template
# import signal
# import logging
# import errno
# from multiprocessing import Process
# import time
# import math
# import pathlib
# import sys
# import os
#
# import ruamel.yaml
# import tomputils.util as tutil
# import multiprocessing_logging
# import requests
#
#
# CONFIG_FILE_ENV = 'CP_CONFIG_FILE'
# REMOTE_PATTERN = '/*/%Y/%m/%d/*.jpg'
#
# def parse_config(config_path):
#     logger.debug("Parsing config %s", config_path)
#     config_file = pathlib.Path(config_path)
#     yaml = ruamel.yaml.YAML()
#     config = None
#     try:
#         config = yaml.load(config_file)
#     except ruamel.yaml.parser.ParserError as e1:
#         logger.error("Cannot parse config file")
#         tutil.exit_with_error(e1)
#     except OSError as e:
#         if e.errno == errno.EEXIST:
#             logger.error("Cannot read config file %s", config_file)
#             tutil.exit_with_error(e)
#         else:
#             raise
#     return config
#
#
# def poke_relay(relay):
#     try:
#         url = URL_TMPL.substitute(relay)
#         logger.debug("Poking %s at %s", relay['name'], url)
#         r = requests.get(url, timeout=relay['timeout'])
#         r.raise_for_status()
#         logger.info("Poked.")
#     except requests.exceptions.ConnectionError:
#         # The web relay doesn't return headers when sent a sate.xml request
#         # urllib3 doesn't support HTTP/0.9 requests. What's to be done?
#         logging.info("Web relay connection error. This is normal.")
#     except requests.exceptions.ReadTimeout as e:
#         logging.info("Time-out poking %s", relay['name'])
#     except requests.exceptions.RequestException as e:
#         logging.exception("%s resisted.", relay['name'])
#     finally:
#         for handler in logger.handlers:
#             handler.flush()
#
#
# def validate_relay(relay):
#     if relay['minute_offset'] >= relay['interval']:
#         logger.error("minute_offset must be smaller than interval."
#                      "(%d >= %d)", relay['minute_offset'],
#                      relay['interval'])
#         return False
#
#     if relay['disabled']:
#         logger.debug("Skipping %s, it's disabled.", relay['name'])
#         return False
#
#     return True
#
#
# def poke_relays(relays):
#     procs = []
#     minute = math.floor(time.time() / 60)
#     for relay in relays:
#         if not validate_relay(relay):
#             continue
#
#         minute_offset = minute % relay['interval']
#         if minute_offset == relay['minute_offset']:
#             p = Process(target=poke_relay, args=(relay,))
#             procs.append(p)
#             p.start()
#         else:
#             logger.debug("Skipping %s, %d %% %d == %d not %d", relay['name'],
#                          minute, relay['interval'], minute_offset,
#                          relay['minute_offset'])
#
#     return procs
#
#
#
# def get_new_images(config):
#     rsync - va - -include = '2018/09/01/*.jpg' - -include = '**/' -
#           -exclude = '*' - -prune - empty - dirs
#     avosouth - int.wr.usgs.gov: / www / avosouth.wr.usgs.gov / htdocs / cam.
#     os.system("rsync -avrz /opt/data/filename root@ip:/opt/data/file")
#
#     return False
#
#
# def main():
#     # let ctrl-c work as it should.
#     signal.signal(signal.SIGINT, signal.SIG_DFL)
#
#     global logger
#     logger = tutil.setup_logging("webrelaypoker errors")
#     multiprocessing_logging.install_mp_handler()
#
#     if len(sys.argv) < 2:
#         tutil.exit_with_error("usage: camrouter.py config")
#
#     config = parse_config(sys.argv[1])
#     if get_new_images(config):
#         pass
#
#     logger.debug("That's all for now, bye.")
#     logging.shutdown()
#
#
# if __name__ == '__main__':
#     main()
