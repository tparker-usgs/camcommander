# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#  Purpose: work with webcam images
#   Author: Tom Parker
#
# -----------------------------------------------------------------------------
"""
camcommander
=========

Tools to handle webcam images.

:license:
    CC0 1.0 Universal
    http://creativecommons.org/publicdomain/zero/1.0/
"""


import tomputils.util as tutil
from camcommander.version import __version__

logger = tutil.setup_logging("camcommander - errors")
__all__ = ["__version__"]
