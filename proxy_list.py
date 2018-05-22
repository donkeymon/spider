import base
import requests
import random
import threading
import multiprocessing
from fake_useragent import UserAgent
from multiprocessing import Process, Pool
from threading import Thread
from urllib.request import ProxyHandler, build_opener
from urllib.error import URLError
from socket import timeout

THREAD_NUMBER = 4
PROCESS_NUMBER = 4
BASE_URL = 'http://www.xicidaili.com/nn/{0}'
PATTERN = '''<td class=".*"><img src=".*" alt=".*" /></td>
      <td>(.*)</td>
      <td>(.*)</td>
      <td>
        <a href=".*">.*</a>
      </td>
      <td class=".*">.*</td>
      <td>(.*)</td>'''

FILE_NAME = 'proxy.txt'
GOOD_PROXY_TIMEOUT = 3
MAX_PAGE = 5

def get_headers():
    return {
        'User-Agent': UserAgent().random
    }


def get_good_proxies_by_page(page):
    proxies = get_proxies_by_page(page)
    for proxy in proxies:
        if is_good_proxy(proxy):
            with open(FILE_NAME, 'a') as file_handler:
                file_handler.write(str(proxy) + ',')
                print(str(proxy))
                file_handler.close()


def get_proxies_by_page(page):
    proxies = []

    headers = get_headers()
    url = BASE_URL.format(page)
    
    # urllib
    # request = base.get_request(url = url, headers = headers)
    # html = base.get_html(request)

    # requests
    html = requests.get(url, headers = headers).text
    match_result = base.get_match_result(PATTERN, html)
    for proxy in match_result:
        proxies.append({proxy[2].lower(): proxy[0] + ':' + proxy[1]})

    return proxies

def is_good_proxy(proxy):
    check_url = 'https://www.ipip.net'

    # urllib
    # proxy_handler = ProxyHandler(proxy)
    # opener = build_opener(proxy_handler)
    # req = base.get_request(check_url, headers = get_headers())
    # try:
    #     opener.open(req, timeout = GOOD_PROXY_TIMEOUT)
    # except URLError:
    #     return False
    # except timeout:
    #     return False
    # else:
    #     return True

    # requests
    try:
        res = requests.get(check_url, get_headers(), proxies = proxy, timeout = GOOD_PROXY_TIMEOUT)
        res.raise_for_status()
    except Exception:
        return False
    else:
        return True


def read_proxies():
    file_handler = open(FILE_NAME, 'r')
    proxies_line = file_handler.read()
    proxies = proxies_line.split(',')
    proxies.pop()
    return proxies


def random_proxy():
    proxies = read_proxies()
    return random.choice(proxies)


def main():
    # 单线程 [Finished in 579.6s]
    # for page in range(1, MAX_PAGE):
    #     get_good_proxies_by_page(page)

    # 多线程 [Finished in 150.0s]
    for page in range(1, MAX_PAGE, THREAD_NUMBER):
            threads = []
            for i in range(THREAD_NUMBER):
                threads.append(Thread(target = get_good_proxies_by_page, args = (page + i,)))
            for i in range(THREAD_NUMBER):
                threads[i].start()

    # 多进程  [Finished in 156.8s]
    # if __name__ == '__main__':
    #     for page in range(1, MAX_PAGE, PROCESS_NUMBER):
    #             processes = []
    #             for i in range(PROCESS_NUMBER):
    #                 processes.append(Process(target = get_good_proxies_by_page, args = (page + i,)))
    #             for i in range(PROCESS_NUMBER):
    #                 processes[i].start()

    # 多进程 进程池 [Finished in 156.2s]
    # if __name__ == '__main__':
    #     pool = Pool(4)
    #     for page in range(1, MAX_PAGE, PROCESS_NUMBER):
    #         for i in range(PROCESS_NUMBER):
    #             pool.apply_async(get_good_proxies_by_page, args = (page + i,))
    #     pool.close()
    #     pool.join()
