"""
camcommander -- deal with webcam images

"""

from setuptools import setup, find_packages
from distutils.util import convert_path

main_ns = {}
ver_path = convert_path("camcommander/version.py")
with open(ver_path) as ver_file:
    exec(ver_file.read(), main_ns)


DOCSTRING = __doc__.split("\n")

setup(
    name="camcommander",
    version=main_ns["__version__"],
    author="Tom Parker",
    author_email="tparker@usgs.gov",
    description=(DOCSTRING[1]),
    license="CC0",
    url="http://github.com/tparker-usgs/camcommander",
    packages=find_packages(),
    long_description="\n".join(DOCSTRING[3:]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Software Development :: Libraries",
        "License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
    ],
    install_requires=[
        "request",
        "msgpack",
        "pyzmq",
        "tomputils>=1.12.18",
        "single",
        "multiprocessing-logging",
        "svn",
    ],
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "webrelaypoker = camcommander.webrelaypoker:main",
            "imageshepherd = camcommander.imageshepherd:main",
        ]
    },
)
