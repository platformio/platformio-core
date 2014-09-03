# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from click import argument, group, echo, style, secho
from requests import get
from requests.exceptions import ConnectionError

from platformio import __apiurl__
from platformio.exception import APIRequestError


def get_api_result(query):
    result = None
    r = None
    try:
        r = get(__apiurl__ + query)
        result = r.json()
    except ConnectionError:
        raise APIRequestError("Could not connect to PlatformIO API Service")
    except ValueError:
        raise APIRequestError("Invalid response: %s" % r.text)
    finally:
        if r:
            r.close()
    return result


@group(short_help="Library Manager")
def cli():
    pass


@cli.command("search", short_help="Search for library")
@argument("query")
def lib_search(query):
    result = get_api_result("/lib/search?query=%s" % query)
    secho("Found [ %d ] libraries:" % result['total'],
          fg="green" if result['total'] else "yellow")
    for item in result['items']:
        echo("{name:<30} {info}".format(name=style(item['name'], fg="cyan"),
                                        info=item['description']))
