#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from email.utils import formatdate
from typing import Any, Tuple, List

from aiohttp.web import Request, Response

from nginx_blackout.app import NginxBlackout


def get_app(request: Request) -> NginxBlackout:
    app = request.app["nginx_blackout"]  # type: NginxBlackout
    return app


def norm_lang(s: str) -> str:
    return s.strip().lower().replace("_", "-")


def parse_accept_language(s: str) -> List[str]:
    raw_result = []  # type: List[Tuple[float, str]]
    if not s:
        return []

    for lang_full in s.split(","):
        lang_full = lang_full.strip()
        if not lang_full:
            continue

        if ";" not in lang_full:
            raw_result.append((1.0, norm_lang(lang_full)))
            continue

        lang, opts = lang_full.split(";", 1)
        qvalue = 1.0
        if opts.startswith("q="):
            try:
                qvalue = float(opts[2:])
            except ValueError:
                pass
        raw_result.append((qvalue, norm_lang(lang)))

    return [x[1] for x in sorted(raw_result, reverse=True)]


def get_request_locale(request: Request) -> str:
    candidates = []  # type: List[str]

    if request.query.get("locale"):
        candidates.append(norm_lang(request.query["locale"]))

    if request.cookies.get("locale"):
        candidates.append(norm_lang(request.cookies["locale"]))

    if request.headers.get("Accept-Language"):
        candidates.extend(parse_accept_language(request.headers["Accept-Language"]))

    known_locales = get_app(request).locales

    for lang in candidates:
        if lang in known_locales:
            return lang
        if "-" in lang:
            lang_short = lang.split("-", 1)[0]
            if lang_short in known_locales:
                return lang_short

    return known_locales[0]


def set_cache_headers(response: Response, max_age: int = 0) -> None:
    epoch_seconds = int(time.time()) + max_age
    response.headers["Expires"] = formatdate(epoch_seconds, usegmt=True)
    response.headers["Cache-Control"] = "max-age={max_age}".format(max_age=max(0, max_age))


def get_localized_config(locale: str, value: Any, default: Any = None) -> Any:
    if value is None:
        return default
    if not isinstance(value, dict):
        return value
    if "default" not in value:
        raise ValueError("Localized config must have the 'default' key")
    if locale in value:
        return value[locale]
    return value["default"]
