#!/usr/bin/env python

from setuptools import setup

def readme():
    with open("README.md", "r") as f:
        return f.read()

setup(
    name="h5sh",
    version="0.1",
    description="An interactive shell for HDF5 files",
    long_description=readme(),
    keywords="h5sh hdf5 h5 shell",
    url="https://github.com/jl-wynen/h5shell",
    author="Jan-Lukas Wynen",
    author_email="j-l.wynen@hotmail.de",
    license="MIT",
    packages=["h5sh", "h5sh/commands"],
    # scripts=["bin/h5sh.py"],
    entry_points={
        "console_scripts": ["h5sh=h5sh.command_line:main"]
    },
    requires=["h5py"],
    extras_require={
        "psutil": ["psutil"]
    },
#    include_package_data=True,
#    zip_safe=False
)
