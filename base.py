import re
import urllib
import urllib.request
import zlib
import socket
import random
from urllib.request import ProxyHandler, build_opener


def get_opener(proxy):
    try:
        proxy_handler = ProxyHandler(proxy)
    except Exception:
        return None
    return build_opener(proxy_handler)


def get_request(url, data = None, headers = {}):
    return urllib.request.Request(url = url, data = data, headers = headers)


def get_response(req_or_url, opener = None, timeout = socket._GLOBAL_DEFAULT_TIMEOUT):
    if opener:
        try:
            return opener.open(req_or_url, timeout = timeout)
        except Exception:
            return False
    else:
        try:
            return urllib.request.urlopen(req_or_url, timeout = timeout)
        except Exception:
            return False


def urllib_open(req_or_url, proxy = None, headers = {}, timeout = socket._GLOBAL_DEFAULT_TIMEOUT):
    if isinstance(proxy, str):
        try:
            proxy = eval(proxy)
            if isinstance(proxy, dict):
                return None
        except Exception:
            return None
    opener = get_opener(proxy)

    return get_html(req_or_url, opener, timeout)


def decompress(data, encoding):
    if encoding == 'gzip':
        try:
            return zlib.decompress(data, zlib.MAX_WBITS | 16)
        except zlib.error:
            return None
    elif encoding == 'deflate':
        try:
            return zlib.decompress(data, -zlib.MAX_WBITS)
        except zlib.error:
            return zlib.decompress(data)
    else:
        return data


def get_html(req_or_url, opener = None, timeout = socket._GLOBAL_DEFAULT_TIMEOUT):
    res = get_response(req_or_url, opener, timeout = timeout)
    if not res:
        return None
    html = decompress(res.read(), res.headers.get('Content-Encoding'))
    if not html:
        return None
    return html.decode('utf-8')


def get_match_result(pattern, str):
    return re.findall(pattern, str)
