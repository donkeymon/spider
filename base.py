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

DETECT_IP_TIMEOUT = 4

def get_ip_info(proxy = None, fast_priority = None, timeout = DETECT_IP_TIMEOUT, field = 'ip'):
    headers = {
        'User-Agent': UserAgent().random
    }

    if fast_priority is 1:
        try:
            res = requests.get(NET_CN_GET_IP_URL, proxies = proxy, headers = headers, timeout = timeout)
            res.raise_for_status()
            return re.findall('\d+\.\d+\.\d+\.\d+', res.text)[0]
        except Exception:
            return ''
    elif fast_priority is 2:
        try:
            res = requests.get(TAOBAO_GET_IP_URL, proxies = proxy, headers = headers, timeout = timeout)
            res.raise_for_status()
            return res.json()['data'].get(field)
        except Exception:
            return ''
    elif fast_priority is 3:
        try:
            res = requests.get(CHINAZ_GET_IP_URL, proxies = proxy, headers = headers, timeout = timeout)
            res.raise_for_status()
            return re.findall("{0}:'([^,]+)'".format('ip'), res.text)[0]
        except Exception:
            return ''
    elif fast_priority is 4:
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
