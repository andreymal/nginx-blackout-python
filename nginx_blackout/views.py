#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import asyncio

from aiohttp.web import Request, Response, HTTPFound
from aiohttp_jinja2 import render_template
import user_agents
from user_agents.parsers import UserAgent

from nginx_blackout import utils


available_templates = {
    "chrome": "browsers/chrome.html",
    "yandex_mobile": "browsers/yandex_mobile.html",
    "yandex_desktop": "browsers/yandex_desktop.html",
    "firefox": "browsers/firefox.html",
    "opera_mobile": "browsers/opera_mobile.html",
    "uc": "browsers/uc.html",
}


default_button_url = "https://m.habr.com/ru/company/itsumma/blog/479942/"


def select_template_by_user_agent(user_agent: UserAgent) -> str:
    if "Chrome" in user_agent.browser.family:
        return available_templates["chrome"]

    if "Yandex" in user_agent.browser.family:
        return available_templates["yandex_mobile"] if user_agent.is_mobile else available_templates["yandex_desktop"]

    if "Firefox" in user_agent.browser.family:
        return available_templates["firefox"]

    if "Opera Mobile" in user_agent.browser.family:
        return available_templates["opera_mobile"]

    if "UC Browser" in user_agent.browser.family:
        return available_templates["uc"]

    return available_templates["chrome"]


async def index(request: Request) -> Response:
    app = utils.get_app(request)
    locale = utils.get_request_locale(request)

    random_delay_ms_min = int(app.config["general"].get("random_delay_ms_min", 0))
    random_delay_ms_max = int(app.config["general"].get("random_delay_ms_max", 0))
    if random_delay_ms_max > 1:
        if random_delay_ms_min < 1:
            random_delay_ms_min = 1
        elif random_delay_ms_min >= random_delay_ms_max:
            random_delay_ms_min = random_delay_ms_max - 1
        delay = random.randrange(
            random_delay_ms_min,
            random_delay_ms_max,
        ) / 1000.0
        await asyncio.sleep(delay)

    user_agent_string = request.headers.get("User-Agent") or ""
    user_agent = user_agents.parse(user_agent_string)

    if request.query.get("template") and request.query["template"] in available_templates:
        ua_template = available_templates[request.query["template"]]
    else:
        ua_template = select_template_by_user_agent(user_agent)

    context = {
        "locale": locale,
        "user_agent_string": user_agent_string,
        "user_agent": user_agent,
        "ua_template": ua_template,
        "button_url": utils.get_localized_config(locale, app.config["general"].get("button_url")) or default_button_url,
        "button_text": utils.get_localized_config(locale, app.config["general"].get("button_text")),
        "site_name": utils.get_localized_config(locale, app.config["general"].get("site_name")) or "",
        "favicon_url": utils.get_localized_config(locale, app.config["general"].get("favicon_url")),
        "favicon_type": utils.get_localized_config(locale, app.config["general"].get("favicon_type")) or "image/x-icon",
        "metrika": bool(app.config["general"].get("metrika", False)),
        "yandex_metrika_id": app.config["general"].get("yandex_metrika_id", 0),
    }

    status = app.config["general"].get("status_code") or 200
    response = render_template(
        "nginx_blackout_{locale}.html".format(locale=locale),
        request,
        context,
        status=status,
    )

    utils.set_cache_headers(response, max_age=app.config["general"].get("browser_cache_max_age", 0))
    response.headers["Vary"] = "Accept-Language"
    response.headers["Content-Language"] = locale
    if app.config["general"].get("server_header") is not None:
        response.headers["Server"] = app.config["general"]["server_header"]

    return response


async def favicon(request: Request) -> Response:
    app = utils.get_app(request)
    locale = utils.get_request_locale(request)
    favicon_url = utils.get_localized_config(locale, app.config["general"].get("favicon_url"))
    if favicon_url:
        return HTTPFound(location=favicon_url)
    return Response(text="There is no favicon", status=404)
