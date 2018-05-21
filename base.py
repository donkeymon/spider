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


def proxy_str_to_dict(proxy):
    if isinstance(proxy, str):
        try:
            proxy = eval(proxy)
            if isinstance(proxy, dict):
                return None
        except Exception:
            return None
    elif isinstance(proxy, dict):
        return proxy
    else:
        return None


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


def get_html(req_or_url, proxy = None, timeout = socket._GLOBAL_DEFAULT_TIMEOUT):
    opener = get_opener(proxy_str_to_dict(proxy))
    res = get_response(req_or_url, opener, timeout = timeout)
    if not res:
        return None
    html = decompress(res.read(), res.headers.get('Content-Encoding'))
    if not html:
        return None
    return html.decode('utf-8')


def get_match_result(pattern, str):
    return re.findall(pattern, str)
