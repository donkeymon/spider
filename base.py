import re
import urllib
import urllib.request
import zlib
import socket
import random
import requests
import socket
import time
from urllib.request import ProxyHandler, build_opener
from fake_useragent import UserAgent

# 按速度降序
NET_CN_GET_IP_URL = 'http://www.net.cn/static/customercare/yourip.asp'
TAOBAO_GET_IP_URL = 'http://ip.taobao.com/service/getIpInfo.php?ip=myip'
CHINAZ_GET_IP_URL = 'http://ip.chinaz.com/getip.aspx'
SOHU_GET_IP_URL = 'https://txt.go.sohu.com/ip/soip'
GET_IP_URL_MAP = {
    0: NET_CN_GET_IP_URL,
    1: TAOBAO_GET_IP_URL,
    2: CHINAZ_GET_IP_URL,
    3: SOHU_GET_IP_URL
}

DETECT_IP_TIMEOUT = 2

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


def proxy_format(proxy):
    if isinstance(proxy, str):
        try:
            return eval(proxy)
        except Exception:
            return None
    elif isinstance(proxy, dict) and (proxy.get('http') or proxy.get('https')):
        return proxy
    else:
        return None


def decompress(data, encoding):
    try:
        if encoding == 'gzip':
            return zlib.decompress(data, zlib.MAX_WBITS | 16)
        elif encoding == 'zlib':
            return zlib.decompress(data, zlib.MAX_WBITS)
        elif encoding == 'deflate':
            return zlib.decompress(data, -zlib.MAX_WBITS)
        else:
            return data
    except zlib.error:
        return data


def get_html(req_or_url, proxy = None, timeout = socket._GLOBAL_DEFAULT_TIMEOUT):
    opener = get_opener(proxy_format(proxy))
    res = get_response(req_or_url, opener, timeout = timeout)
    if not res:
        return None
    html = decompress(res.read(), res.headers.get('Content-Encoding'))
    if not html:
        return None
    return html.decode('utf-8')


def get_ip_info(proxy = None, fast_priority = None, timeout = DETECT_IP_TIMEOUT, field = 'ip'):
    headers = {
        'User-Agent': UserAgent().random
    }

    if fast_priority == 1:
        try:
            res = requests.get(NET_CN_GET_IP_URL, proxies = proxy, headers = headers, timeout = timeout)
            res.raise_for_status()
            return re.findall('\d+\.\d+\.\d+\.\d+', res.text)[0]
        except Exception:
            return ''
    elif fast_priority == 2:
        try:
            res = requests.get(TAOBAO_GET_IP_URL, proxies = proxy, headers = headers, timeout = timeout)
            res.raise_for_status()
            return res.json()['data'].get(field)
        except Exception:
            return ''
    elif fast_priority == 3:
        try:
            res = requests.get(CHINAZ_GET_IP_URL, proxies = proxy, headers = headers, timeout = timeout)
            res.raise_for_status()
            return re.findall("{0}:'([^,]+)'".format('ip'), res.text)[0]
        except Exception:
            return ''
    elif fast_priority == 4:
        try:
            res = requests.get(SOHU_GET_IP_URL, proxies = proxy, headers = headers, timeout = timeout)
            res.raise_for_status()
            return re.findall('\d+\.\d+\.\d+\.\d+', res.text)[0]
        except Exception:
            return ''
    else:
        try:
            res = requests.get(NET_CN_GET_IP_URL, proxies = proxy, headers = headers, timeout = DETECT_IP_TIMEOUT)
            res.raise_for_status()
            return re.findall('\d+\.\d+\.\d+\.\d+', res.text)[0]
        except Exception:
            pass
        try:
            res = requests.get(TAOBAO_GET_IP_URL, proxies = proxy, headers = headers, timeout = DETECT_IP_TIMEOUT)
            res.raise_for_status()
            return res.json()['data'].get(field)
        except Exception:
            pass
        try:
            res = requests.get(CHINAZ_GET_IP_URL, proxies = proxy, headers = headers, timeout = DETECT_IP_TIMEOUT)
            res.raise_for_status()
            return re.findall("{0}:'([^,]+)'".format('ip'), res.text)[0]
        except Exception:
            pass
        try:
            res = requests.get(SOHU_GET_IP_URL, proxies = proxy, headers = headers, timeout = DETECT_IP_TIMEOUT)
            res.raise_for_status()
            return re.findall('\d+\.\d+\.\d+\.\d+', res.text)[0]
        except Exception:
            pass
