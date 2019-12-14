#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from typing import Any, List, Dict

from aiohttp import web
import aiohttp_jinja2
import jinja2


class NginxBlackout:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.webapp = web.Application()
        self.webapp["nginx_blackout"] = self
        self._setup_routes()
        self._setup_templates()
        self.locales = list(config["general"].get(
            "locales",
            ["en", "ru"],
        ))  # type: List[str]

    def run_app(self) -> None:
        web.run_app(
            self.webapp,
            host=self.config["general"].get("host", "127.0.0.1") if not self.config["general"].get("unix_socket") else None,
            port=self.config["general"].get("port", 8000) if not self.config["general"].get("unix_socket") else None,
            path=self.config["general"].get("unix_socket", None),  # FIXME: permission bits
            access_log=None,
            handle_signals=True,
            reuse_port=self.config["general"].get("reuse_port", False),
        )

    def _setup_routes(self) -> None:
        from nginx_blackout import views
        self.webapp.add_routes([
            web.view(r"/favicon.ico", views.favicon),
            web.view(r"/{path:.*}", views.index),
        ])

    def _setup_templates(self) -> None:
        templates_dirs = []  # type: List[str]

        if "templates_dirs" in self.config["general"]:
            templates_dirs.extend([os.path.abspath(x) for x in self.config["general"]["templates_dirs"]])

        if "templates_dir" in self.config["general"]:
            templates_dirs.append(os.path.abspath(self.config["general"]["templates_dir"]))
        
        if not self.config["general"].get("ignore_builtin_templates"):
            templates_dirs.append(os.path.join(os.path.dirname(__file__), "templates"))

        aiohttp_jinja2.setup(
            self.webapp,
            loader=jinja2.FileSystemLoader(templates_dirs),
        )
