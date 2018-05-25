import base
import requests
import random
import threading
import multiprocessing
import re
import os
from fake_useragent import UserAgent
from multiprocessing import Process, Pool
from threading import Thread
from urllib.request import ProxyHandler, build_opener
from urllib.error import URLError
from requests.exceptions import HTTPError, ConnectTimeout, ProxyError

THREAD_NUMBER = 20
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

PROXY_FILE = 'proxy.txt'
GOOD_PROXY_FILE = 'good_proxy.txt'
GOOD_PROXY_TIMEOUT = 5
MAX_PAGE = 100

THREAD_LOCK = threading.Lock()

def get_headers():
    return {
        'User-Agent': UserAgent().random
    }


def get_proxies_by_page(page, proxies):
    headers = get_headers()
    url = BASE_URL.format(page)

    # urllib
    # request = base.get_request(url = url, headers = headers)
    # html = base.get_html(request)

    # requests
    html = requests.get(url, headers = headers).text
    match_result = re.findall(PATTERN, html)
    THREAD_LOCK.acquire()
    file_handler = open(PROXY_FILE, 'a')
    for proxy in match_result:
        file_handler.write("{{'{0}': '{1}:{2}'}},".format(proxy[2].lower(), proxy[0], proxy[1]))
        proxies.append({proxy[2].lower(): proxy[0] + ':' + proxy[1]})
    file_handler.close()
    THREAD_LOCK.release()


def is_good_proxy(proxy, good_proxies):
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
        # match_result = re.findall(check_pattern, res.text)
        # detect_ip = match_result[0]
        # proxy_match_result = re.findall(proxy_match_result, str(proxy))
        # proxy_ip = proxy_match_result[0]
        # if proxy_ip == detect_ip:
        #     return True
        # else:
        #     return False

    # requests
    try:
        res = requests.get(base.NET_CN_GET_IP_URL, get_headers(), proxies = proxy, timeout = GOOD_PROXY_TIMEOUT)
        res.raise_for_status()
    except HTTPError:
        print('not good proxy ' + str(proxy) + ' http_error')
        return False
    except ConnectTimeout:
        print('not good proxy ' + str(proxy) + ' connect_timeout')
        return False
    except ProxyError:
        print('not good proxy ' + str(proxy) + ' proxy_error')
        return False
    except Exception:
        print('not good proxy ' + str(proxy) + ' unknown error')
        return False
    else:
        find_detect_ip = re.findall('\d+\.\d+\.\d+\.\d+', res.text)
        if not find_detect_ip:
            print('detect ip error ' + str(proxy))
            detect_ip = ''
        else:
            detect_ip = find_detect_ip[0]

        proxy_ip = (proxy.get('http') or proxy.get('https')).split(':')[0]
        if proxy_ip == detect_ip:
            THREAD_LOCK.acquire()
            file_handler = open(GOOD_PROXY_FILE, 'a')
            file_handler.write(str(proxy) + ',')
            file_handler.close()
            good_proxies.append(proxy)
            THREAD_LOCK.release()
            print('is good proxy  ' + str(proxy))
            return True
        else:
            print('not good proxy ' + str(proxy))
            return False


def read_proxies(file_name):
    try:
        file_handler = open(file_name, 'r')
        proxies_line = file_handler.read()
        proxies = proxies_line.split(',')
        proxies.pop()
        file_handler.close()
        return proxies
    except Exception:
        return []


def random_proxy():
    proxies = read_proxies(GOOD_PROXY_FILE)
    return random.choice(proxies)


# def main():
    # 单线程
    # for page in range(1, MAX_PAGE):
    #     get_good_proxies_by_page(page)

    # 多线程
    # proxies = []
    # for page in range(1, MAX_PAGE, THREAD_NUMBER):
    #     threads = []
    #     for i in range(THREAD_NUMBER):
    #         threads.append(Thread(target = get_proxies_by_page, args = (page + i, proxies)))
    #     for i in range(THREAD_NUMBER):
    #         threads[i].start()
    #     for i in range(THREAD_NUMBER):
    #         threads[i].join()

    # proxies = read_proxies(PROXY_FILE)
    # for i in range(0, len(proxies), THREAD_NUMBER):
    #     threads = []
    #     for j in range(THREAD_NUMBER):
    #         threads.append(Thread(target = is_good_proxy, args = (eval(proxies[i + j]),)))
    #     for j in range(THREAD_NUMBER):
    #         threads[j].start()
    #     for j in range(THREAD_NUMBER):
    #         threads[j].join()

    # 多进程
    # if __name__ == '__main__':
    #     for page in range(1, MAX_PAGE, PROCESS_NUMBER):
    #             processes = []
    #             for i in range(PROCESS_NUMBER):
    #                 processes.append(Process(target = get_good_proxies_by_page, args = (page + i,)))
    #             for i in range(PROCESS_NUMBER):
    #                 processes[i].start()

    # 多进程 进程池
    # if __name__ == '__main__':
    #     pool = Pool(4)
    #     for page in range(1, MAX_PAGE, PROCESS_NUMBER):
    #         for i in range(PROCESS_NUMBER):
    #             pool.apply_async(get_good_proxies_by_page, args = (page + i,))
    #     pool.close()
    #     pool.join()

def get_proxies_to_file(restart = False):
    if restart and os.path.exists(PROXY_FILE):
        os.unlink(PROXY_FILE)
    else:
        return read_proxies(PROXY_FILE)

    proxies = []
    for page in range(1, MAX_PAGE, THREAD_NUMBER):
        threads = []
        for i in range(THREAD_NUMBER):
            if page + i <= MAX_PAGE:
                threads.append(Thread(target = get_proxies_by_page, args = (page + i, proxies)))
        for i in range(len(threads)):
            threads[i].start()
        for i in range(len(threads)):
            threads[i].join()
    return proxies

def get_good_proxies_to_file(restart = False):
    if restart and os.path.exists(GOOD_PROXY_FILE):
        os.unlink(GOOD_PROXY_FILE)
    else:
        return read_proxies(GOOD_PROXY_FILE)

    proxies = read_proxies(PROXY_FILE)
    good_proxies = []
    for i in range(0, len(proxies), THREAD_NUMBER):
        threads = []
        for j in range(THREAD_NUMBER):
            if i + j < len(proxies):
                threads.append(Thread(target = is_good_proxy, args = (eval(proxies[i + j]), good_proxies)))
        for j in range(len(threads)):
            threads[j].start()
        for j in range(len(threads)):
            threads[j].join()
    return good_proxies
