import re
import urllib
import urllib.request
import zlib
import socket
from urllib.request import ProxyHandler, build_opener

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
    'Mozilla/5.0 (Linux; Android 7.1.1; MI 6 Build/NMF26X; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.158 Mobile Safari/537.36'
]


def get_opener(proxy):
    proxy_handler = ProxyHandler(proxy)
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


def decompress(data, encoding):
    if encoding == 'gzip':
        try:
            return zlib.decompress(data, zlib.MAX_WBITS | 16)
        except zlib.error:
            return False
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
        return False
    html = decompress(res.read(), res.headers.get('Content-Encoding'))
    if not html:
        return False
    return html.decode('utf-8')


def get_match_result(pattern, str):
    return re.findall(pattern, str)
