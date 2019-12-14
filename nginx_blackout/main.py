#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import argparse
from typing import Any, Dict

import toml

from nginx_blackout.app import NginxBlackout


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "config_file",
        metavar="config.toml",
        default="config.toml",
        nargs="?",
        help="configuration file",
    )
    args = parser.parse_args()

    with open(args.config_file, "r", encoding="utf-8-sig") as fp:
        config = dict(toml.load(fp))  # type: Dict[str, Any]

    app = NginxBlackout(config)
    app.run_app()
    return 0


if __name__ == "__main__":
    sys.exit(main())
