import random
import time
import base
import proxy_list
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

def get_headers():
    return {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': 1,
        'User-Agent': USER_AGENTS.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'DNT': 1,
        'Referer': 'https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=0&rsv_idx=1&tn=baidu&wd=%E8%B1%86%E7%93%A3%20%E6%9D%AD%E5%B7%9E%E7%A7%9F%E6%88%BF%E5%B0%8F%E7%BB%84&rsv_pq=dc4ab5760000d649&rsv_t=0dc0TLK5%2FGWiLLaM7UX284evhE8e8ZKlCz8k80aVXAZPo1TP4cG06X1wVgg&rqlang=cn&rsv_enter=1&rsv_sug3=31&rsv_sug1=27&rsv_sug7=100&rsv_sug2=0&inputT=3576&rsv_sug4=3577',
        'Accept-Encoding': 'br',
        'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8,en-US;q=0.7'
    }


def get_pattern():
    return BASE_PATTERN.format(SPLITTER.join(KEY_WORDS))


def get_zufang(pattern, page = 1, proxies = None):
    if not proxies:
        opener = None
    else:
        opener = base.get_opener(eval(random.choice(proxies)))

    url = BASE_URL + SUB_URL + 'start=' + str((page - 1) * 25)
    headers = get_headers()
    req = base.get_request(url, headers = headers)

    html = base.get_html(req, opener, TIMEOUT)
    if not html:
        return

    match_result = base.get_match_result(pattern, html)
    if not match_result:
        return

    with open(FILE_NAME, 'a') as file_handler:
        for info in match_result:
            file_handler.write(info[0] + ' ' + info[1] + '\n')
            print(str(page) + ' ' + info[0] + ' ' + info[1])
        file_handler.close()


def main():
    pattern = get_pattern()
    proxies = proxy_list.read_proxies()

    for page in range(START_PAGE, MAX_PAGE, THREAD_NUMBER):
        threads = []
        for i in range(THREAD_NUMBER):
            threads.append(Thread(target = get_zufang, args = (pattern, page + i, proxies)))
        for i in range(THREAD_NUMBER):
            threads[i].start()
    print('done')

main()