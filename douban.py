import random
import time
import base
import proxy_list
import requests
import re
import threading
from fake_useragent import UserAgent
from threading import Thread
from urllib.request import ProxyHandler, build_opener

KEY_WORDS = ['钱江', '和谐', '九堡', '地铁']

BASE_URL = 'https://www.douban.com'
SUB_URL = '/group/HZhome/discussion?'
BASE_URL_M = 'https://m.douban.com'
SUB_URL_M = '/group/HZhome/?'
USER_AGENTS = UserAgent()


SPLITTER = '|'
BASE_PATTERN_M = '''<a href="(.*)" title="(.*)">
                        <h3 class=".*">
                            .*({0}).*'''
BASE_PATTERN = '''<a href="(.*)" title="(.*)" class="">
                       .*({0}).*
                    </a>'''

START_PAGE = 1
MAX_PAGE = 400
PAGE_SIZE = 25
FILE_NAME = '租房.txt'
TIMEOUT = 3

THREAD_NUMBER = 4
THREAD_LOCK = threading.Lock()

def get_headers():
    return {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': USER_AGENTS.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'DNT': '1',
        'Referer': 'https://www.baidu.com',
        'Accept-Encoding': 'gzip,deflate,br',
        'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8,en-US;q=0.7'
    }


def get_pattern():
    return BASE_PATTERN.format(SPLITTER.join(KEY_WORDS))


def get_zufang(pattern, proxies, page = 1):
    proxy = random.choice(proxies)
    if not get_zufang_by_page(pattern, proxy, page):
        #所有proxy都重试一遍
        for proxy in proxies:
            if get_zufang_by_page(pattern, proxy, page):
                break


def get_zufang_by_page(pattern, proxy = None, page = 1):
    url = BASE_URL + SUB_URL + 'start=' + str((page - 1) * 25)

    # urllib
    # req = base.get_request(url, headers = get_headers())
    # html = base.get_html(req, proxy, TIMEOUT)
    # if not html:
    #     return False

    # requests
    try:
        res = requests.get(url, get_headers(), proxies = proxy)
        res.raise_for_status()
        status_code = res.status_code
        html = res.text
    except Exception:
        return False

    match_result = re.findall(pattern, html)
    if not match_result:
        return False

    THREAD_LOCK.acquire()
    file_handler = open(FILE_NAME, 'a', encoding = 'utf-8')
    for info in match_result:
        file_handler.write(info[0] + ' ' + info[1] + '\n')
        print(str(status_code) + ' ' + str(page) + ' ' + info[0] + ' ' + info[1])
    file_handler.close()
    THREAD_LOCK.release()
    return True


def main():
    pattern = get_pattern()
    proxies = proxy_list.read_proxies(proxy_list.GOOD_PROXY_FILE)

    for page in range(START_PAGE, MAX_PAGE, THREAD_NUMBER):
        threads = []
        for i in range(THREAD_NUMBER):
            threads.append(Thread(target = get_zufang, args = (pattern, proxies, page + i)))
        for i in range(THREAD_NUMBER):
            threads[i].start()
