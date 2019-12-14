#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


def readfile(path):
    with open(path, "r", encoding="utf-8-sig") as fp:
        return fp.read()


setup(
    name="nginx_blackout",
    version="0.1.0",
    description="nginx-blackout-python",
    long_description=readfile("README.md").rstrip(),
    long_description_content_type="text/markdown",
    author="andreymal",
    author_email="andriyano-31@mail.ru",
    license="MIT",
    platforms=["any"],
    packages=find_packages(),
    python_requires=">=3.5",
    install_requires=[
        "aiohttp>=3.6,<4.0",
        "aiohttp-jinja2>=1.2,<1.3",
        "user-agents>=2.0,<3.0",
        "toml",
    ],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "nginx_blackout=nginx_blackout.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
)
