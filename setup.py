#!/usr/bin/env python

from setuptools import setup
import subprocess

def readme():
    with open("README.rst", "r") as f:
        return f.read()

def get_version():
    tags = [e for e in subprocess.check_output(["git", "tag"]).decode("utf-8").split("\n")
            if e]
    if tags:
        return tags[-1]

    return "0.0"  # no tag found, default to 'no version'

setup(
    name="h5sh",
    version="{}".format(get_version()),
    description="An interactive shell for HDF5 files",
    long_description=readme(),
    keywords="h5sh hdf5 h5 shell",
    url="https://github.com/jl-wynen/h5shell",
    author="Jan-Lukas Wynen",
    author_email="j-l.wynen@hotmail.de",
    license="MIT",
    packages=["h5sh", "h5sh/commands"],
    entry_points={
        "console_scripts": ["h5sh=h5sh.command_line:main"]
    },
    requires=["h5py"],
    extras_require={
        "psutil": ["psutil"],
        "rtd_theme": ["sphinx_rtd_theme"]
    },
    include_package_data=True,
    zip_safe=False
)
